# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------


#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Functor.html#t:Functor

"""
Functors: uniform action over a parameterized type, generalizing the map function on lists.


The Functor interface is used for types that can be mapped over. Instances of Functor should satisfy the following laws:

fmap id  ==  id
fmap (f . g)  ==  fmap f . fmap g
"""

from pylude.core import TypeClass


class Functor(TypeClass):
    pass

    #def fmap(self, f):
    #    return None


def fmap(func, functor):
    """
    fmap :: (a -> b) -> f a -> f b 
    """
    if not isinstance(functor, Functor):
        raise TypeError("%s is not an instance of Functor!" % type(functor))
    else:
        try:
            return functor.fmap(func)
        except AttributeError:
            return map(func, functor)





def void(f,functor):
    """
    fmap without return value
    """
    fmap(f,functor)















