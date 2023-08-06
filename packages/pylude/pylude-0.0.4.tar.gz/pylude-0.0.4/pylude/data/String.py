

#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-String.html
"""
The String type and associated operations.
"""

#more or less finished


#Functions on strings

def lines(s):
    """
    lines :: str -> [str]
    lines breaks a string up into a list of strings at newline characters. The resulting strings do not contain newlines.
    """
    return s.split("\n")


def words(text):
    """
    words breaks a string up into a list of words, which were delimited by white space.
    """
    return ( s for s in text.replace("\t"," ").replace("\n"," ").split(" ") if s != "")


def unlines(ls):
    """
    unlines :: [str] -> str
    unlines is an inverse operation to lines. It joins lines, after appending a terminating newline to each.
    """
    return "\n".join(ls)


def unwords(ls):
    """
    unwords is an inverse operation to words. It joins words with separating spaces.
    """
    return " ".join(ls)







