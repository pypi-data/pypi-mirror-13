#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Tuple.html

def fst(t):
    """
    fst :: (a, b) -> a 
    Extract the first component of a pair.
    """
    return t[0]

def snd(t):
    """
    snd :: (a, b) -> b 
    Extract the second component of a pair.
    """
    return t[1]


#curry
#uncurry


def swap(t):
    """
    swap :: (a, b) -> (b, a) 
    Swap the components of a pair.
    """
    a, b = t
    return b, a




