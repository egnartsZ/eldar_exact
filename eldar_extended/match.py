import re
class Match:
    def __init__(self, start = None, end = None, match_substr = None, match = None):
        self.start = start
        self.end = end
        self.match = match_substr
        if isinstance(match, re.Match):
            self.start = match.start(0)
            self.end = match.end(0)
            self.match = match.group(0)
    
    def __repr__(self):
        return("<eldar_extended.Match object; span=(" + str(self.start) + ", " + str(self.end) + "), match = '" + str(self.match) + "'>")