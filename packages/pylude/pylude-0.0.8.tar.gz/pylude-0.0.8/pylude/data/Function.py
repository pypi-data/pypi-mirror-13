# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------
from functools import partial as _partial

#from pylude.core import Function as _Function
#from pylude.core import wrapBy, libfunc
#from pylude.core import libfunc


__all__ = ('id_', 'const', 'flip')
"""
Data.Function

Simple combinators working solely on and with functions.


http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Function.html
"""

#todo:
#Function class vs Function-module name collision
#with wrapBy



"""
============= Prelude re-exports ==============
"""


#@libfunc
def id_(x):
    """
    id :: a -> a
    Identity function.
    """
    return x


#@libfunc
def const(a, b):
    """
    const :: a -> b -> a
    Constant function.
    """
    return a

#compose

#@libfunc
def flip(op, b, a):
    """
    flip :: (a -> b -> c) -> b -> a -> c
    flip f takes its (first) two arguments in the reverse order of f.
    """
    return op(a,b)

#$

"""
Other combinators
"""


#&

#fix

#on




