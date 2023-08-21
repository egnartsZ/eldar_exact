from unidecode import unidecode
import re
from .regex import WORD_REGEX
from .entry import Entry, SearchEntry
from .operators import AND, ANDNOT, OR, SearchOR, IF, NOT
import spacy


class QueryAbstract:
    def __init__(
        self,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en',
        stop_words = False,
        stop_words_list = []
    ):
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        self.exact_match = exact_match
        self.lemma_match = lemma_match
        self.language = language

        #load stopwords variables
        if stop_words:
            if len(stop_words_list) == 0:
                self.stop_words = True
                if language == "fr":
                    import spacy.lang.fr
                    self.stop_words_list = spacy.lang.fr.stop_words.STOP_WORDS
                elif language == "en":
                    import spacy.lang.en
                    self.stop_words_list = spacy.lang.en.stop_words.STOP_WORDS
                else:
                    raise ValueError("Language " + str(language) +" not supported")
            else:
                self.stop_words_list = stop_words_list
        else:
            self.stop_words = False
            self.stop_words_list = []
                
        #load lemmatizer
        if lemma_match:
            if self.language == "fr":
                self.nlp_model =  spacy.load('fr_core_news_sm')
            elif self.language == "en":
                self.nlp_model =  spacy.load('en_core_web_sm')
            else:
                raise ValueError("Language " + str(language) +" not supported")
        else:
            self.nlp_model = None
        
        
            
    

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
    
    def parse_query(self, query):
        # remove brackets and quotes around query if necessary
        if query[0] == '(' and query[-1] == ')':
            query = strip_brackets(query)
        query = strip_quotes(query)

        # find all operators
        match = []
        match_iter = re.finditer(r" (OR|IF|AND NOT|AND|NOT) ", query, re.IGNORECASE)
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

        #If there's an operator 
        if len(match) != 0:
            # stop at first balanced operation if no balanced operation raise an error
            for operator, (start, end) in match:
                left_part = query[:start]
                if not is_balanced(left_part):
                    continue
                right_part = query[end:]
                if not is_balanced(right_part):
                    raise ValueError("Query malformed, uninterpretable parenthesis" + str(right_part))
                break
            else:
                raise ValueError("Query malformed "+ str(query))
            
            return self.operator_handling(operator, left_part, right_part)
        else:
            query = self.preprocess(query)
            if isinstance(self, SearchQuery):
                return SearchEntry(query)
            if isinstance(self, Query):
                return Entry(query)


class Query(QueryAbstract):
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en', 
        stop_words = False,
        stop_words_list = []
    ):
        super(Query, self).__init__(ignore_case = ignore_case, ignore_accent= ignore_accent, exact_match= exact_match, lemma_match= lemma_match, language=language, stop_words_list = stop_words_list, stop_words= stop_words)
        self.query = self.parse_query(query)


    def operator_handling(self, operator, left_part, right_part):
            if operator == "or":
                return OR(
                    self.parse_query(left_part),
                    self.parse_query(right_part)
                )
            elif operator == "and":
                return AND(
                    self.parse_query(left_part),
                    self.parse_query(right_part)
                )
            elif operator == "and not":
                return ANDNOT(
                    self.parse_query(left_part),
                    self.parse_query(right_part)
                )
            elif operator == "not":
                return NOT(
                    self.parse_query(right_part)
                )
            else: 
                raise ValueError("Query malformed, unsupported operator for this type of queries " +str(operator))
            

    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
        if self.stop_words:
            processed = self.nlp_model(doc)
            filtered = [token.text for token in processed if not token.text in self.stop_words_list]
            doc = " ".join(filtered)
        if self.lemma_match:
            processed = self.nlp_model(doc)
            doc = " ".join([token.lemma_ for token in processed])
        return doc
    

class SearchQuery(QueryAbstract):
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        exact_match=True,
        lemma_match = False,
        language = 'en', 
        stop_words = False,
        stop_words_list = []
    ):
        super(SearchQuery, self).__init__(ignore_case = ignore_case, ignore_accent= ignore_accent, exact_match= exact_match, lemma_match= lemma_match, language=language, stop_words_list = stop_words_list, stop_words= stop_words)
        self.query = self.parse_query(query)

    def operator_handling(self, operator, left_part, right_part):
        if operator == "or":
            return SearchOR(
                self.parse_query(left_part),
                self.parse_query(right_part)
            )
        if operator == "if":
            ifquery = Query(right_part, ignore_case = self.ignore_case, ignore_accent= self.ignore_accent, exact_match= self.exact_match, lemma_match= self.lemma_match, language=self.language, stop_words_list = self.stop_words_list, stop_words= self.stop_words)
            return IF(
                self.parse_query(left_part),
                ifquery.parse_query(right_part)
            )
        else:
            raise ValueError("Query malformed, unsupported operator " +str(operator))
        
    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
        if self.stop_words and self.lemma_match:
            processed = self.nlp_model(doc)
            doc = [(token.lemma_, (token.idx, token.idx + len(token.text))) for token in processed if not token.text in self.stop_words_list]
        elif self.stop_words:
            processed = self.nlp_model(doc)
            doc = [(token.text, (token.idx, token.idx + len(token.text))) for token in processed if not token.text in self.stop_words_list]
        elif self.lemma_match:
            processed = self.nlp_model(doc)
            doc = [(token.lemma_, (token.idx, token.idx + len(token.text))) for token in processed]
        return doc

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

def strip_quotes(query):
    if query[0] == '"' and query[-1] == '"' and query.count('"') == 2:
        return query[1:-1]
    return query



def is_balanced(query):
    # are brackets balanced
    brackets_b = query.count("(") == query.count(")")
    quotes_b = query.count('"') % 2 == 0
    return brackets_b and quotes_b