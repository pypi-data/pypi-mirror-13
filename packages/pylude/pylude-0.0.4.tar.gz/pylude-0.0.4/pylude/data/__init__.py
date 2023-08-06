
#simple types
from pylude.data.Bool import *
from pylude.data.String import *
from pylude.data.Function import *


#types
from pylude.data.Dict import *
from pylude.data.List import *

from pylude.data.Tuple import *
from pylude.data.Maybe import *
from pylude.data.Either import *

#simple interfaces
from pylude.data.Eq import *
from pylude.data.Ord import *
from pylude.data.Read import *
#from pylude.data.Eq import *


#interfaces
from pylude.data.Foldable import *
from pylude.data.Functor import *
from pylude.data.Monad import *


#ops
from operator import add
from operator import sub
from operator import mul as multi
from operator import mod


#types
#from types import GeneratorType as _Gen
from types import FunctionType as _Func


def isiter(x):
    try:
        iterable = iter(x)
        return True
    except TypeError:
        return False

def iterToStr(iterable):
    return "[" + ", ".join(( "'"+str(x)+"'" for x in iterable)) + "]"


def type_(x):
    try: return x.type()
    except AttributeError: return type(x)


def signature(f):
    try: return [l.strip() for l in lines(f.__doc__) if "::" in l][0]
    except IndexError: pass




def printl(x):
    """
    Now you don't have to write print(list())
    over and over again! ;D
    """
    if isinstance(x,_Func):
        print(signature(x).split("::")[1].strip())

    elif isiter(x):
        #print("["+ ", ".join(map(str,x)) +"]")
        print(iterToStr(x))
    else:
        print(str(x))





