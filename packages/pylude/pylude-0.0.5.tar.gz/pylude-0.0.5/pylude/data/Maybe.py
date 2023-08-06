# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------


from pylude.core import newType
from pylude.data.Functor import Functor


"""
The Maybe type encapsulates an optional value. A value of type Maybe a either contains a value of type a (represented as Just a), or it is empty (represented as Nothing). Using Maybe is a good way to deal with errors or exceptional cases without resorting to drastic measures such as error.

The Maybe type is also a monad. It is a simple kind of error monad, where all errors are represented by Nothing. A richer error monad can be built using the Either type.
"""
#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Maybe.html





Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={"Eq","Show"})



def mapMaybe(f, iterable):
    for x in iterable:
        r = f(x)
        if r != Nothing:
            a, = r
            yield a



