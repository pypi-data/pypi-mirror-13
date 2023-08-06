#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-List.html
from functools import reduce

"""
Operations on lists.


pylude tries treating generators and lists as the same thing
functions are iterator oriented and produce generator if possible
"""

#Basic functions


def head(iterable):
    """
    head :: iter a -> a 
    Extract the first element of an iterator, which must be non-empty.
    """
    for x in iterable:
        return x

def last(iterable):
    """
    last :: iter a -> a 
    Extract the last element of an iterator, which must be finite and non-empty.
    """
    try: return iterable[-1]
    except: pass

    c = None
    for x in iterable:
        c = x
    return c

def tail(iterable):
    """
    tail :: iter a -> iter a 
    Extract the elements after the head of an iterator, which must be non-empty.
    """
    first = True
    for i in iterable:
        if first: first = False
        else: yield i

def init(ls):
    """
    init :: [a] -> [a] 
    Return all the elements of a list except the last one. The list must be non-empty.
    """
    return ls[:-1]

def uncons(iterable):
    """
    uncons :: iter a -> (a, [a]) | None
    Decompose an iterator into its head and tail. If the list is empty, returns None. If the iterator is non-empty, returns Just (x, xs), where x is the head of the list and xs its tail.
    """
    return head(iterable), tail(iterable)

def null(iterable):
    """
    null :: iter a -> bool
    Test whether the iterator is empty.
    """
    #for x in iterable:
    #    return False
    #return True
    return any(iterable)

def length(iterable):
    """
    length :: iter a -> int
    Returns the size/length of a finite iterator as an int.
    """
    if type(iterable)==list: return len(iterable)
    i = 0
    for x in iterable:
        i += 1
    return i

#List transformations

reverse = reversed


#Reducing lists (folds)

foldl1 = reduce


#Special folds

def concat(iterable):
    """
    concat :: Foldable t => t [a] -> [a]
    The concatenation of all the elements of a container of lists.
    """
    return reduce(lambda a,b: a+b,iterable)




def any_(f,iterable):
    """
    any :: Foldable t => (a -> Bool) -> t a -> Bool
    Determines whether any element of the structure satisfies the predicate.
    """
    for x in iterable:
        if f(x): return True
    return False



def all_(f,iterable):
    """
    all :: Foldable t => (a -> Bool) -> t a -> Bool
    Determines whether all elements of the structure satisfy the predicate.
    """
    for x in iterable:
        if not f(x): return False
    return True


#Building lists
#Scans


#Accumulating maps


#Infinite lists


def cycle(iterable):
    """
    cycle :: iter a -> iter a
    cycle ties a finite list into a circular one, or equivalently, the infinite repetition of the original list. It is the identity on infinite lists.
    """
    while True:
        for x in iterable:
            yield x



#Unfolding




#Sublists
#Extracting sublists

def take(n, iterable):
    """
    take :: Int -> [a] -> [a]
    take n, applied to a list xs, returns the prefix of xs of length n, or xs itself if n > length xs:

    take 5 "Hello World!" == "Hello"
    take 3 [1,2,3,4,5] == [1,2,3]
    take 3 [1,2] == [1,2]
    take 3 [] == []
    take (-1) [1,2] == []
    take 0 [1,2] == []

    It is an instance of the more general genericTake, in which n may be of any integral type.
    """
    i = 0
    for x in iterable:
        if i < n: yield x
        i += 1

#Searching lists
#Searching by equality


def elem(x, ls):
    return x in ls

def notElem(x, ls):
    return not x in ls



#Searching with a predicate



#Zipping and unzipping lists


#def zipWith(op,ls,bs):
#    return (op(t[0],t[1]) for t in zip(ls,bs))

zipWith = map


#Special lists

#Functions on strings
# *moved to pylude.data.String


#"Set" operations

def nub(iterable):
    """
    nub :: [a] -> [a] 
    O(n^2). The nub function removes duplicate elements from a list. In particular, it keeps only the first occurrence of each element. (The name nub means `essence'.) It is a special case of nubBy, which allows the programmer to supply their own equality test.
    """
    rs = []
    for x in iterable:
        if not x in rs:
            rs.append(x)
    return rs


def delete(v, iterable):
    """
    delete :: __eq__ a => a -> iter a -> iter a
    delete x removes the first occurrence of x from its list argument. For example,
    delete 'a' "banana" == "bnana"
    It is a special case of deleteBy, which allows the programmer to supply their own equality test.
    """
    for x in iterable:
        if x != v: yield x


#Ordered lists

sort = sorted




