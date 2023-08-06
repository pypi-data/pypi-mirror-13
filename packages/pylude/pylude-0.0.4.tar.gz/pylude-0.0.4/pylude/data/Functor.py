

#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Functor.html#t:Functor

"""
Functors: uniform action over a parameterized type, generalizing the map function on lists.


The Functor interface is used for types that can be mapped over. Instances of Functor should satisfy the following laws:

fmap id  ==  id
fmap (f . g)  ==  fmap f . fmap g
"""
class Functor:

    def fmap(self, f):
        return None



def fmap(f,functor):
    """
    fmap :: (a -> b) -> f a -> f b 
    """
    try:
        return functor.fmap(f)
    except AttributeError:
        return map(f,functor)


def void(f,functor):
    """
    fmap without return value
    """
    fmap(f,functor)















