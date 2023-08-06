#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Maybe.html

from pylude.data.Functor import *

"""
The Maybe type encapsulates an optional value. A value of type Maybe a either contains a value of type a (represented as Just a), or it is empty (represented as Nothing). Using Maybe is a good way to deal with errors or exceptional cases without resorting to drastic measures such as error.

The Maybe type is also a monad. It is a simple kind of error monad, where all errors are represented by Nothing. A richer error monad can be built using the Either type.
"""
class Maybe(Functor):

    inst_counter = 0

    def __init__(self):
        #Maybe.inst_counter += 1
        #if Maybe.inst_counter > 2:
        #    raise Exception("Only 1 Nothing allowed!")
        self.__extracted = False

    def __str__(self):
        return "Nothing"

    def __iter__(self):
        return self

    def __next__(self):
        if self.__extracted:
            self.__extracted = False
            raise StopIteration
        self.__extracted = True
        return Nothing

    #======== new interfaces ==========

    def type(self):
        return Maybe

    def fmap(self, f):
        return Nothing


Nothing = Maybe()

class Just(Maybe):

    def __init__(self, value):
        super(Just, self).__init__()
        self.__extracted = False
        self.__value = value

    def __str__(self):
        return "Just("+str(self.__value)+")"

    def __next__(self):
        if self.__extracted:
            self.__extracted = False
            raise StopIteration
        self.__extracted = True
        return self.__value

    #======== new interfaces ==========

    def fmap(self, f):
        return Just(f(self.__value))







def mapMaybe(f, iterable):
    for x in iterable:
        r = f(x)
        if r != Nothing:
            a, = r
            yield a




