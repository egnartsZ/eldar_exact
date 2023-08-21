import re
from collections import defaultdict
from dataclasses import dataclass

from .regex import WILD_CARD_REGEX
from .match import Match

class EntryAbstract:
    def __init__(self, query):
        if isinstance(query, list):
            self.query = [q[0] for q in query]
            joined_query = " ".join(self.query)
            if "*" in joined_query:
                self.query = [query]
                self.pattern = joined_query.replace("*", WILD_CARD_REGEX)
                self.rgx = re.compile(self.pattern)
            else:
                self.rgx = None
            return

        self.query = query
        if "*" in self.query:
            self.pattern = self.query.replace("*", WILD_CARD_REGEX)
            self.rgx = re.compile(self.pattern)
        else:
            self.rgx = None

    def __repr__(self):
        return f'"{self.query}"'


class Entry(EntryAbstract):
    def evaluate(self, doc):
        #Multiword query
        if isinstance(self.query, list):
            #find all occurences of first word of the query
            if self.rgx[0]:
                occurence_first_word = []
                for i, word in enumerate(doc):
                    present, index = check_regex_multiword(doc, self.rgx[0], i)
                    if present:
                        occurence_first_word.append(i)
            else:
                occurence_first_word = find_all_list(doc, self.query[0])
            
            #loop through the first occurences found of each word to identify if there's a subsring matching the query that starts there
            for i, word in enumerate(occurence_first_word):
                for j, q in enumerate(self.query):
                    if self.rgx[j]:
                        check_regex_multiword(doc, self.rgx[j], i)
                    elif q == doc[i + j]:
                        continue
                    else:
                        break
                else:
                    return True
            else:
                return False
                    

        if self.rgx:
            if self.rgx.search(doc):
                res = True
            else:
                res = False
        else:
            res = self.query in doc
        return res

    

class SearchEntry(EntryAbstract):
    def evaluate(self, doc):
        if isinstance(self.query, list):
            res = []
            if self.rgx:
                res_regex = check_regex_multiword(doc, self.rgx, 0)
                while res_regex[0]:
                    res.append(Match(start = doc[res_regex[1]][1][0], end = doc[res_regex[2]][1][1], match_substr = " ".join([token[0] for token in doc[res_regex[1] : res_regex[2] + 1]])))
                    res_regex = check_regex_multiword(doc, self.rgx, res_regex[2])
                return res

            #find all occurences of first word of the query
            occurence_first_word = find_all_list(doc, self.query[0])
            #loop through the first occurences found of each word to identify if there's a subsring matching the query that starts there
            for i, token_id in enumerate(occurence_first_word):
                token = doc[token_id]
                current_token_id = token_id
                for j, q in enumerate(self.query):
                    if q == doc[current_token_id][0]:
                        current_token_id += 1
                    else:
                       break
                else:
                    res.append(Match(start =token[1][0], end = doc[current_token_id - 1][1][1], match_substr = " ".join([token[0] for token in doc[token_id : current_token_id]])))
            else:
                return res

        if self.rgx:
            matchs = self.rgx.finditer(doc)
            res = [Match(match = m) for m in matchs]
        else:
            res = find_all(doc, self.query)
        return res


class IndexEntry:
    def __init__(self, query_term):
        self.not_ = False

        if query_term == "*":
            raise ValueError(
                "Single character wildcards * are not implemented")

        query_term = strip_quotes(query_term)
        if " " in query_term:  # multiword query
            self.query_term = query_term.split()
            self.search = self.search_multiword
        else:
            self.query_term = query_term
            self.search = self.search_simple

    def search_simple(self, index):
        res = index.get(self.query_term)
        return {match.id for match in res}

    def search_multiword(self, index):
        docs = defaultdict(list)
        for token in self.query_term:
            items = index.get(token)
            for item in items:
                docs[item.id].append((item.position, token))

        # utils variable
        first_token = self.query_term[0]
        query_len = len(self.query_term)
        query_rest = self.query_term[1:]
        iter_rest = range(1, query_len)

        results = set()
        for doc_id, tokens in docs.items():
            tokens = sorted(tokens)
            if len(tokens) < query_len:
                continue
            for i in range(len(tokens) - query_len + 1):
                pos, tok = tokens[i]
                if tok != first_token:
                    continue
                is_a_match = True
                for j, correct_token in zip(iter_rest, query_rest):
                    next_pos, next_tok = tokens[i + j]
                    if correct_token != next_tok or next_pos != pos + j:
                        is_a_match = False
                        break
                if is_a_match:
                    results.add(doc_id)
                    break
        return results

    def __repr__(self):
        if self.not_:
            return f'NOT "{self.query_term}"'
        return f'"{self.query_term}"'




def check_regex_multiword(doc, rgx, start_id):
    initial_offset = doc[start_id][1][0]
    joined_doc = " ".join([token[0] for token in doc[start_id:]])
    res = rgx.match(joined_doc)
    if not res:
        return False, None
    elif res.start(0) != doc[start_id][1][0]:
        return False, None
    
    for current_id in range(start_id,len(doc)):
        if doc[current_id][1][0] < res.start(0) + initial_offset:
            continue
        elif doc[current_id][1][0] >= res.start(0) + initial_offset:
            start_res = current_id
            break

    for current_id in range(start_res,len(doc)):
        if doc[current_id][1][1] < res.end(0) + initial_offset:
            continue
        elif doc[current_id][1][1] >= res.end(0) + initial_offset:
            return True, start_res, current_id




def strip_quotes(query):
    if query[0] == '"' and query[-1] == '"' and query.count('"') == 2:
        return query[1:-1]
    return query

@dataclass(unsafe_hash=True, order=True)
class Item:
    id: int
    position: int

def find_all_list(L, q):
    all_occurences= []
    for i, token in enumerate(L):
        if q == token[0]:
            all_occurences.append(i)
    return all_occurences

def find_all(s, sub):
    start = 0
    res = []
    while True:
        start = s.find(sub, start)
        if start == -1: return res
        res.append(Match(start = start, end = start + len(sub), match_substr= sub))
        start += len(sub) # use start += 1 to find overlapping matches