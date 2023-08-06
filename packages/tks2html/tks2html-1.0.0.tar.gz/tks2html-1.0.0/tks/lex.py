'''The Lexical Analyzer of tks2html

By Leslie Zhu <pythonisland@gmail.com>


'''

class KLexical(object):
    """The basic class for Kscript lexical analyzer"""
    
    def __init__(self,tks_line=""):
        self.tks_line = tks_line
        
    def analyse(self):
        token = ""
        for char in self.tks_line:
            if char in [' ','\t']:
                if token.strip(" |\t") != "":
                    yield token
                    token = char
                else:
                    token += char
            else:
                if char in ['(','{',')','}','=','+','-','%','>','<','>=','<=','!=','==',';',',',':']:
                    yield token
                    yield char
                    token = ""
                    continue
                elif token and token.strip(" |\t") == "":
                    yield token
                    token = char
                elif token in ['//','/*','*/']:
                    yield token
                    token = char
                else:
                    token += char
        # ;
        if token:
            yield token

                    

    
