# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------
from abc import ABCMeta
from inspect import signature as _signature
from functools import update_wrapper


__all__ = ('TypeClass', 'newType', 'createSig', 'wrapBy','pylu','fix', 'curry')

"""

'core' serves as the absolute basis for pylude and implements the Haskell typesystem, syntactic sugar and signature creation

Examples:

Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={"Eq","Show"})
maybe = Just(1)
Just(match=maybe) == True


Inspired by:
http://learnyouahaskell.com/making-our-own-types-and-typeclasses
http://hackage.haskell.org/package/base-4.8.2.0/docs/Data-Data.html
"""
#====== Helper-decos: ========
def wrapBy(clsconstr):
    def deco(f):
        return clsconstr(f)
    return deco

#todo rename to 'pylu'
#def libfunc(f):
def pylu(f):
    return Function(f)

#====== Helper-funcs: ========

def func2method(f):
    """
    Turns a function into a method:
    fmap(f,ls) -> ls.fmap(f)
    """
    def method(self, *args):
        return f(*tuple(list(args)+[self]))
    return method






#=============================

#todo:
#record syntax
#signatures: (int,int,int) == int -> int -> int
#signatures: ((int,int),int) == (int -> int) -> int


class TypeClass(metaclass=ABCMeta):
    pass

#newTypeClass

def newType(name, *args, **kwargs):
    """
    The central type factory
    """
    if "deriving" in kwargs:
        if type(kwargs["deriving"])==set:
            derivingInterfaces = kwargs["deriving"]
        else:
            raise TypeError("The 'deriving'-keyword expects a set of names not %s!" % type(kwargs["deriving"]).__name__)
    else:
        derivingInterfaces = set()



    if "implements" in kwargs:
        if type(kwargs["implements"])==dict:
            implementedInterfaces = kwargs["implements"]
        else:
            raise TypeError("The 'implements'-keyword expects a dict of names not a %s!" % type(kwargs["implements"]).__name__)
    else:
        implementedInterfaces = {}


    class datatypeMeta(type):

        def __new__(cls, clsname, bases, clsdict):

            for interface in derivingInterfaces:
                for k, v in interface.__dict__.items():
                    if callable(v):
                        #print("derive", k)
                        clsdict[k] = v



            for interface, funcsdict in implementedInterfaces.items():
                #print(interface, funcsdict)
                #print(interface, type(interface))
                #if type(interface)==type:
                if True: #isinstance(interface, TypeClass):
                    #print("XXXXX")
                    for abstractfuncname, func in funcsdict.items():
                        #print(clsname, "add", abstractfuncname, "implemented by", func)
                        #clsdict[abstractfuncname] = func
                        clsdict[abstractfuncname] = func2method(func)

            clsobj = super().__new__(cls, clsname, bases, clsdict)

            return clsobj

        def __str__(self):
            return "<"+name+">"

        def __repr__(self):
            return str(self)


    class T(metaclass=datatypeMeta):
        __slots__ = ("__prefix", "__num", "__values")

        def __init__(self, prefix, num, *args):
            if len(args) != num:
                raise TypeError("%s-constructor: Wrong number of arguments(%s)! %s given but %s needed!" % (prefix,args,len(args), num))
            self.__prefix = prefix
            self.__num = num
            self.__values = args


        def getPrefix(self):
            return self.__prefix

        def getValues(self):
            return self.__values



        def __iter__(self):
            if self.__num > 0: return iter(self.__values)
            else: return iter([self])

    T.__name__ = name


    #register typeclasses
    for interface, funcsdict in implementedInterfaces.items():
        interface.register(T)



    def newConstructor(constructor_name, constructor_arity):
        if constructor_arity > 0:

            @wrapBy(Function)
            def constructor_func(*args, **kwargs):

                if "match" in kwargs and len(args)==0:
                    #return type(kwargs["match"]) == type(T())
                    return kwargs["match"].getPrefix() == constructor_name


                return T(constructor_name, constructor_arity, *args)



            constructor_func.__name__ = constructor_name
            return constructor_func

        elif constructor_arity == 0:
            return T(constructor_name, 0)
        else:
            raise TypeError("The arity of a constructor cannot be negative!")


    #todo typeSymbol class IO(int)


    if len(args)==1: return newConstructor(*args[0])
    return (newConstructor(constructor_name, constructor_arity) for constructor_name, constructor_arity in args)





class Function:
    """
    wrapper-class for functions
    """
    def __init__(self, *funcs):
        self.__funcs = funcs
        update_wrapper(self, self.__funcs[0])
        #todo: nerge names, docs, return_anno



    def __call__(self, *args, **kwargs):
        val = self.__funcs[0](*args, **kwargs)
        for f in reversed(self.__funcs[1:]):
            val = f(val)
        return val


    def __mul__(self, f):
        """
        composition: self * f
        """
        return Function(*(list(self.__funcs)+[f]))

    def __rmul__(self, f):
        """
        composition: f * self
        """
        return Function(*([f]+list(self.__funcs)))


    def __repr__(self):
        return str(self)

    def __str__(self):
        lasttype = createSig(self.__funcs[0]).split("->")[-1].strip()
        firsttype = createSig(self.__funcs[-1]).split("->")[0].strip()
        return "(%s :: %s -> %s)" % (".".join([f.__name__ for f in self.__funcs]), firsttype, lasttype)


    #$ == |
    def __or__(self, other):
        """
        not made for composition!
        """
        if callable(other): return Function(comp(self, other))
        else: return self(other)



def comp(g,f):
    """
    basic composition/no metadata-copying
    """
    def h(*args, **kwargs):
        return g(f(*args, **kwargs))
    return h







#signature class?


def numFuncArgs(f):
    pass


def createSig(f):

    anno = False
    try:
        __annotations__ = f.__annotations__
        anno = True
    except AttributeError: pass

    sig = False
    try:
        __typesig__ = str(_signature(f))
        sig = True
    except ValueError: pass

    #build stuff
    if anno and sig:
        r = __typesig__.replace("(","").replace(")","")
        varls = [s.split(":")[0].strip() for s in r.split(",")]
        varls = [s.split(" -> ")[0].strip() for s in varls]
        r = " -> ".join(varls)
        for varname, vartype in __annotations__.items():
            r = r.replace(varname, vartype.__name__)
        if "return" in __annotations__:
            r += " -> "+__annotations__["return"].__name__
        else:
            r += " -> ?"
        return r

    elif sig:
        return " -> ".join(__typesig__.split(",")) + " -> ?"
    else:
        return "? -> ?"



#todo curryed-deco

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




#todo: curred deco


def fix(f, x):
    return lambda *args: f(*([x]+list(args)))


def curry(f, n):
    if n == 1: return f
    return lambda x: curry(fix(f, x), n-1)







    """
    h.__name__ == "("+g.__name__+"."+f.__name__+")"

    fdoc = "?"
    gdoc = "?"
    try:
        fdoc = f.__doc__
        if fdoc==None:
            fdoc = "?"
    except AttributeError:
        pass
    try:
        gdoc = g.__doc__
        if gdoc==None:
            gdoc = "?"
    except AttributeError:
        pass
    h.__doc__ = fdoc + "\n\n => \n\n" + gdoc


    try:
        h.__annotations__ = f.__annotations__
    except AttributeError: pass


    try:
        h.__annotations__["return"] = g.__annotations__["return"]
    except AttributeError: pass


    return Function(h)
    """





