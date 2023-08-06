# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------


#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Maybe.html

from pylude.core import newType
from pylude.data.Functor import Functor

"""
The Either type represents values with two possibilities: a value of type Either a b is either Left a or Right b.

The Either type is sometimes used to represent a value which is either correct or an error; by convention, the Left constructor is used to hold an error value and the Right constructor is used to hold a correct value (mnemonic: "right" also means "correct").
"""


#def mapEither(f, either):
#    x, = either
#    return either


Left, Right = newType("Either", ("Left",1), ("Right",1), deriving={"Show","Eq"} )



def either(f,g,x):
    if isLeft(x): return f(x)
    elif isRight(x): return g(x)
    raise TypeError("The either function expects an Either value! "+str(type(x))+" given!")

def lefts(ls):
    return (x for x in ls if isLeft(x))

def rights(ls):
    return (x for x in ls if isRight(x))

def isLeft(v):
    return Left(match=v)

def isRight(v):
    return Right(match=v)


"""
Prelude> fmap (*2) (Left 5)
Left 5
Prelude> fmap (*2) (Left 5)
Left 5
Prelude> fmap (*2) (Just 5)
Just 10
Prelude> fmap (*2) (Right 5)
Right 10

"""




def partitionEithers(iterable):
    ls = []
    rs = []
    for x in iterable:
        if isLeft(x): ls.append(x)
        elif isRight(x): rs.append(x)
        else: raise TypeError("partitionEithers expects a list of Either values! "+str(type(x))+"is not an Either value!")

    return ls, rs


