# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------


"""

core serves as the absolute basis for pylude and implements the Haskell typesystem


Examples:


Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={"Eq","Show"})

maybe = Just(1)

Just(match=maybe) == True


"""


#todo: record syntax

from abc import ABCMeta


class TypeClass(metaclass=ABCMeta):
    pass



def newType(name, *args, **kwargs):
    """


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
            #print(cls)
            #print(clsdict)
            #def show(self):
            #    return "Human"
            #clsdict["__str__"] = show

            def func2method(f):

                def method(self, *args):

                    return f(*tuple(list(args)+[self]))


                return method


            for interface, funcsdict in implementedInterfaces.items():
                #print(interface, funcsdict)
                #print(interface, type(interface))
                #if type(interface)==type:
                if True: #isinstance(interface, TypeClass):
                    print("XXXXX")
                    for abstractfuncname, func in funcsdict.items():
                        print(clsname, "add", abstractfuncname, "implemented by", func)
                        #clsdict[abstractfuncname] = func
                        clsdict[abstractfuncname] = func2method(func)




            clsobj = super().__new__(cls, clsname, bases, clsdict)

            return clsobj

        def __str__(self):
            return name

    class T(metaclass=datatypeMeta):
        __slots__ = ("__prefix", "__num", "__values")

        def __init__(self, prefix, num, *args):
            if len(args) != num:
                raise TypeError("%s-constructor: Wrong number of arguments(%s)! %s given but %s needed!" % (prefix,args,len(args), num))
            self.__prefix = prefix
            self.__num = num
            self.__values = args

        if "Show" in derivingInterfaces:
            def __str__(self):
                return self.__prefix + " "+ " ".join(map(str,self.__values))

        if "Eq" in derivingInterfaces:
            def __eq__(self, other):
                return self.__prefix == other.__prefix and self.__values == other.__values
        else:
            def __eq__(self, other):
                return self.__prefix == other.__prefix

        def getPrefix(self):
            return self.__prefix


        def __iter__(self):
            if self.__num > 0: return iter(self.__values)
            else: return iter([self])

    T.__name__ = name


    #register typeclasses
    for interface, funcsdict in implementedInterfaces.items():
        interface.register(T)



    def newConstructor(constructor_name, constructor_arity):
        if constructor_arity > 0:
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



    if len(args)==1: return newConstructor(*args[0])
    return (newConstructor(constructor_name, constructor_arity) for constructor_name, constructor_arity in args)






















