

#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Function.html


#wrapper class

class Function:

    def __init__(self, f):
        self.__f = f

    def __call__(self, *args):
        return self.__f(*args)

    def __mul__(self, f):
        return Function(comp(self.__f, f))


#def fix(f, x):
#    return lambda *args: f(*([x]+list(args)))

"""
def maybe(f):
    def g(*args):
        try: return f(*args)
        except: return None
    return g

def memoize(f):
    mem = {}
    def g(*args):
        if args in mem:
            print("Remember: f%s = %s" % (args,mem[args]))
            return mem[args]
        r = f(*args)
        if r != None:
            print("Memoize: f%s = %s" % (args,r))
            mem[args] = r
        return r
    return g

#docurry
def curryD(n):
    def deco(f):
        if n == 1: return f
        return lambda x: curry(fix(f, x), n-1)
    return deco


def log(f):
    def g(*args):
        r = f(*args)
        print("Calculating: %s(%s) = %s" % ( str(f).split(" ")[1], str(",".join(map(str,list(args)))), str(r)) )
        return r
    return g



"""




#curred deco


def id_(x):
    """
    id :: a -> a
    Identity function.
    """
    return x



def const(a, b):
    """
    const :: a -> b -> a
    Constant function.
    """
    return a


#compose(*funcs)
def comp(g,f):
    """
    comp :: (b -> c) -> (a -> b) -> a -> c
    Function composition.
    """
    return lambda *args: g(f(*args))


def flip(op, b, a):
    """
    flip :: (a -> b -> c) -> b -> a -> c
    flip f takes its (first) two arguments in the reverse order of f.
    """
    return op(a,b)







