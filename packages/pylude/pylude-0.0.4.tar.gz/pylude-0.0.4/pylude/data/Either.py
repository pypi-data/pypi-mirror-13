

#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Maybe.html

from pylude.data.Functor import Functor

"""
The Either type represents values with two possibilities: a value of type Either a b is either Left a or Right b.

The Either type is sometimes used to represent a value which is either correct or an error; by convention, the Left constructor is used to hold an error value and the Right constructor is used to hold a correct value (mnemonic: "right" also means "correct").
"""
class Either(Functor):

    inst_counter = 0

    def __init__(self):
        #Maybe.inst_counter += 1
        #if Maybe.inst_counter > 2:
        #    raise Exception("Only 1 Nothing allowed!")
        self.__extracted = False


        #if Maybe.nothingcreated:
        #    raise TypeError("Maybe is not a constructor!")
        #Maybe.nothingcreated = True
        #self.__extracted = False


    #======== new interfaces ==========
    def type(self):
        return Either


class Left(Either):

    def __init__(self, value):
        super(Left, self).__init__()
        self.__extracted = False
        self.__value = value

    def __str__(self):
        return "Left "+str(self.__value)


    def __iter__(self):
        return self

    def __next__(self):
        if self.__extracted:
            self.__extracted = False
            raise StopIteration
        self.__extracted = True
        return self.__value

    #======== new interfaces ==========
    def fmap(self, f):
        return Left(f(self.__value))



class Right(Either):

    def __init__(self, value):
        super(Right, self).__init__()
        self.__extracted = False
        self.__value = value

    def __str__(self):
        return "Right "+str(self.__value)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__extracted:
            self.__extracted = False
            raise StopIteration
        self.__extracted = True
        return self.__value

    #======== new interfaces ==========
    def fmap(self, f):
        return Right(f(self.__value))




def either(f,g,x):
    if isLeft(x): return f(x)
    elif isRight(x): return g(x)
    raise TypeError("The either function expects an Either value! "+str(type(x))+" given!")



def lefts(ls):
    """
    lefts :: iter(Either a b) -> iter a 
    Extracts from a list of Either all the Left elements. All the Left elements are extracted in order.
    """
    return (x for x in ls if isLeft(x))


def rights(ls):
    """
    rights :: iter (Either a b) -> iter b
    Extracts from a list of Either all the Right elements. All the Right elements are extracted in order.
    """
    return (x for x in ls if isRight(x))



def isLeft(v):
    """
    isLeft :: Either a b -> Bool
    Return True if the given value is a Left-value, False otherwise.
    """
    return isinstance(v,Left)

def isRight(v):
    """
    isRight :: Either a b -> Bool
    Return True if the given value is a Right-value, False otherwise.
    """
    return isinstance(v,Right)



def partitionEithers(iterable):
    """
    partitionEithers :: [Either a b] -> ([a], [b]) 
    Partitions a list of Either into two lists. All the Left elements are extracted, in order, to the first component of the output. Similarly the Right elements are extracted to the second component of the output.
    """
    ls = []
    rs = []
    for x in iterable:
        if isLeft(x): ls.append(x)
        elif isRight(x): rs.append(x)
        else: raise TypeError("partitionEithers expects a list of Either values! "+str(type(x))+"is not an Either value!")

    return ls, rs



