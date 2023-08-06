# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------
from pylude.core import newType
from pylude.data.Functor import Functor

#typeclasses
from pylude.data.Eq import Eq
from pylude.text.Show import Show



__all__ = ('Just', 'Nothing', 'isJust', 'isNothing', 'mapMaybe')


"""
The Maybe type encapsulates an optional value. A value of type Maybe a either contains a value of type a (represented as Just a), or it is empty (represented as Nothing). Using Maybe is a good way to deal with errors or exceptional cases without resorting to drastic measures such as error.

The Maybe type is also a monad. It is a simple kind of error monad, where all errors are represented by Nothing. A richer error monad can be built using the Either type.

http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Maybe.html
"""

#Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={"Eq","Show"})
Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={Eq, Show})




#maybe



def isJust(x):
    """
    isJust :: Maybe a -> Bool
    The isJust function returns True if its argument is of the form Just _.
    """
    return Just(match=x)



def isNothing(x):
    """
    isNothing :: Maybe a -> Bool
    The isNothing function returns True if its argument is Nothing.
    """
    return x==Nothing

#fromJust

#fromMaybe

#listToMaybe


#maybeToList


#maybeToList



#catMaybes


def mapMaybe(f, iterable):
    """
    mapMaybe :: (a -> Maybe b) -> [a] -> [b]

    The mapMaybe function is a version of map which can throw out elements.
    In particular, the functional argument returns something of type Maybe b.
    If this is Nothing, no element is added on to the result list.
    If it is Just b, then b is included in the result list.
    """
    for x in iterable:
        r = f(x)
        if r != Nothing:
            a, = r
            yield a



