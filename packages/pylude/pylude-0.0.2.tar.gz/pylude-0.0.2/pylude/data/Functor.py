

#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Functor.html#t:Functor

"""
Functors: uniform action over a parameterized type, generalizing the map function on lists.
"""
class Functor:

    def fmap(self, f):
        return None



def fmap(f,functor):
    try:
        return functor.fmap(f)
    except AttributeError:
        return map(f,functor)


def void(f,functor):
    """
    fmap without return value
    """
    fmap(f,functor)















