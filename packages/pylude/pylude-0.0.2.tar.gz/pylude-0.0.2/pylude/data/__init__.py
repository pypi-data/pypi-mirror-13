from pylude.data.Dict import *
from pylude.data.List import *
from pylude.data.String import *
from pylude.data.Tuple import *
from pylude.data.Maybe import *
#interfaces
from pylude.data.Functor import *

from types import GeneratorType as _Gen

def type(x):
    try:
        return x.type()
    except AttributeError:
        return type(x)


def printl(x):
    """
    Now you don't have to write print(list())
    over and over again! ;D
    """
    if isinstance(x,_Gen): print(list(x))
    else: print(x)
