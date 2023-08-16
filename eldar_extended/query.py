from unidecode import unidecode
import re
from .regex import WORD_REGEX
from .entry import Entry, SearchEntry
from .operators import AND, ANDNOT, OR, SearchOR, IF
import spacy


class QueryInterface:
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en'
    ):
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        self.match_word = exact_match
        self.lemma_match = lemma_match
        self.language = language
        if lemma_match:
            if self.language == "fr":
                self.nlp_model =  spacy.load('fr_core_news_md')
            elif self.language == "en":
                self.nlp_model =  spacy.load('en_core_web_sm')
            else:
                raise ValueError("Language " + str(language) +" not supported")
        else:
            self.nlp_model = None
        
        
            
    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
        if self.lemma_match:
            processed = self.nlp_model(doc)
            doc = " ".join([token.lemma_ for token in processed])
        return doc

    def evaluate(self, doc):
        doc = self.preprocess(doc)
        return self.query.evaluate(doc)

    def filter(self, documents):
        docs = []
        for doc in documents:
            if not self.evaluate(doc):
                continue
            docs.append(doc)
        return docs

    def __call__(self, doc):
        return self.evaluate(doc)

    def __repr__(self):
        return self.query.__repr__()
    


class Query(QueryInterface):
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en'
    ):
        super(Query, self).__init__(query, ignore_case, ignore_accent, exact_match, lemma_match, language)
        self.query = Query.parse_query(query, self.ignore_case, self.ignore_accent, self.lemma_match, self.nlp_model)

    def parse_query(query, ignore_case, ignore_accent, lemma_match, nlp_model):
        # remove brackets around query
        if query[0] == '(' and query[-1] == ')':
            query = strip_brackets(query)
        # if there are quotes around query, make an entry
        if query[0] == '"' and query[-1] == '"' and query.count('"') == 1:
            if ignore_case:
                query = query.lower()
            if ignore_accent:
                query = unidecode(query)
            return Entry(query)

        # find all operators
        match = []
        match_iter = re.finditer(r" (AND NOT|AND|OR) ", query, re.IGNORECASE)
        for m in match_iter:
            start = m.start(0)
            end = m.end(0)
            operator = query[start+1:end-1].lower()
            match_item = (start, end)
            match.append((operator, match_item))
        match_len = len(match)
        if match_len != 0:
            # stop at first balanced operation
            for i, (operator, (start, end)) in enumerate(match):
                left_part = query[:start]
                if not is_balanced(left_part):
                    continue

                right_part = query[end:]
                if not is_balanced(right_part):
                    raise ValueError("Query malformed")
                break

            if operator == "or":
                return OR(
                    Query.parse_query(left_part, ignore_case, ignore_accent, lemma_match, nlp_model),
                    Query.parse_query(right_part, ignore_case, ignore_accent, lemma_match, nlp_model)
                )
            elif operator == "and":
                return AND(
                    Query.parse_query(left_part, ignore_case, ignore_accent, lemma_match, nlp_model),
                    Query.parse_query(right_part, ignore_case, ignore_accent, lemma_match, nlp_model)
                )
            elif operator == "and not":
                return ANDNOT(
                    Query.parse_query(left_part, ignore_case, ignore_accent, lemma_match, nlp_model),
                    Query.parse_query(right_part, ignore_case, ignore_accent, lemma_match, nlp_model)
                )
        else:
            if ignore_case:
                query = query.lower()
            if ignore_accent:
                query = unidecode(query)
            if lemma_match:
                processed = nlp_model(query)
                query = " ".join([token.lemma_ if not '*' in token.text else token.text for token in processed])

            return Entry(query)


class SearchQuery(QueryInterface):
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en'
    ):
        super(SearchQuery, self).__init__(query, ignore_case, ignore_accent, exact_match, lemma_match, language)
        self.query = SearchQuery.parse_query(query, self.ignore_case, self.ignore_accent, self.lemma_match, self.nlp_model)



    def parse_query(query, ignore_case, ignore_accent, lemma_match, nlp_model):
        # remove brackets around query
        if query[0] == '(' and query[-1] == ')':
            query = strip_brackets(query)
        # if there are quotes around query, make an entry
        if query[0] == '"' and query[-1] == '"' and query.count('"') == 1:
            if ignore_case:
                query = query.lower()
            if ignore_accent:
                query = unidecode(query)
            return SearchEntry(query)
        # find all operators
        match = []
        match_iter = re.finditer(r" (OR|IF) ", query, re.IGNORECASE)
        nb_if = 0
        for m in match_iter:
            start = m.start(0)
            end = m.end(0)
            operator = query[start+1:end-1].lower()
            if operator == "if":
                nb_if+= 1
                if nb_if >= 2:
                    raise ValueError("Query malformed, contains multiple IF")
            match_item = (start, end)
            match.append((operator, match_item))
        match_len = len(match)
        if match_len != 0:
            # stop at first balanced operation
            for i, (operator, (start, end)) in enumerate(match):
                left_part = query[:start]
                if not is_balanced(left_part):
                    continue

                right_part = query[end:]
                if not is_balanced(right_part):
                    raise ValueError("Query malformed")
                break

            if operator == "or":
                return SearchOR(
                    SearchQuery.parse_query(left_part, ignore_case, ignore_accent, lemma_match, nlp_model),
                    SearchQuery.parse_query(right_part, ignore_case, ignore_accent, lemma_match, nlp_model)
                )
            if operator == "if":
                return IF(
                    SearchQuery.parse_query(left_part, ignore_case, ignore_accent, lemma_match, nlp_model),
                    Query.parse_query(right_part, ignore_case, ignore_accent, lemma_match, nlp_model)
                )
        else:
            if ignore_case:
                query = query.lower()
            if ignore_accent:
                query = unidecode(query)
            if lemma_match:
                processed = nlp_model(query)
                query = " ".join([token.lemma_ if not '*' in token.text else token.text for token in processed])

            return SearchEntry(query)
        


def strip_brackets(query):
    count_left = 0
    for i in range(len(query) - 1):
        letter = query[i]
        if letter == "(":
            count_left += 1
        elif letter == ")":
            count_left -= 1
        if i > 0 and count_left == 0:
            return query

    if query[0] == "(" and query[-1] == ")":
        return query[1:-1]
    return query


def is_balanced(query):
    # are brackets balanced
    brackets_b = query.count("(") == query.count(")")
    quotes_b = query.count('"') % 2 == 0
    return brackets_b and quotes_b


