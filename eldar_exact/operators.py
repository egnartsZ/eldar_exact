import numpy as np

class Binary:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class AND(Binary):
    def evaluate(self, doc):
        left_match = self.left.evaluate(doc)
        if not left_match:
            return False
        right_match = self.right.evaluate(doc)
        if not right_match:
            return False
        return True

    def __repr__(self):
        return f"({self.left}) AND ({self.right})"


class ANDNOT(Binary):
    def evaluate(self, doc):
        left_match = self.left.evaluate(doc)
        if not left_match:
            return False
        right_match = self.right.evaluate(doc)
        return not right_match

    def __repr__(self):
        return f"({self.left}) AND NOT ({self.right})"


class OR(Binary):
    def evaluate(self, doc):
        if self.left.evaluate(doc):
            return True
        if self.right.evaluate(doc):
            return True
        return False

    def __repr__(self):
        return f"({self.left}) OR ({self.right})"
    
class NOT(Binary):
    def __init__(self, right):
        self.right = right

    def evaluate(self, doc):
        return not self.right.evaluate(doc)

    def __repr__(self):
        return f"NOT ({self.right})"


class SearchOR:
    def __init__(self, left, right):
        self.left = left
        self.right = right


    def evaluate(self, doc):
        left = self.left.evaluate(doc)
        right = self.right.evaluate(doc)
        return left + right

    def __repr__(self):
        return f"({self.left}) OR ({self.right})"
    

class IF:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def evaluate(self, doc):
        if self.right.evaluate(doc):
            return self.left.evaluate(doc)
        else:
            return []

    def __repr__(self):
        return f"({self.left}) IF ({self.right})"
    

class IFAFTER:
    #Returns only search results that are placed after the IF
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, doc):
        rightres = self.right.evaluate(doc)
        if rightres:
            starts = [res[1][0] for res in rightres]
            first_rigtres = np.argmin(starts)
            leftres = self.left.evaluate(doc)
            return [res for res in leftres if res[1][0] > first_rigtres[1][0]]
        else:
            return []

    def __repr__(self):
        return f"({self.left}) IFAFTER ({self.right})"
    

class IFBEFORE:
    #Returns only search results that are placed after the IF
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, doc):
        rightres = self.right.evaluate(doc)
        if rightres:
            starts = [res[1][0] for res in rightres]
            first_rigtres = np.argmin(starts)
            leftres = self.left.evaluate(doc)
            return [res for res in leftres if res[1][0] < first_rigtres[1][0]]
        else:
            return []

    def __repr__(self):
        return f"({self.left}) IFAFTER ({self.right})"