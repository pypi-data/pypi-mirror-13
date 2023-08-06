pylude
=======================

A library trying to clone the Haskell-Prelude for python3 :

http://hackage.haskell.org/package/base-4.8.1.0/docs/Prelude.html


Why? Because rapid prototyping for haskell should be a thing!



====================================================
==============    Features    ======================
====================================================
implemented so far:

-----The newType function:------

Just, Nothing = newType("Maybe", ("Just", 1), ("Nothing", 0), deriving={"Eq","Show"})


--constructor matching:--

def isJust(x):
    return Just(match=x)

def isNothing(x):
    return x==Nothing


--type-classes:--


def mapB(func, b):
    return b

T, F = newType("B", ("T",0), ("F",0), deriving={"Eq","Show"}, implements={Functor : {"fmap" : mapB} })

print(fmap(lambda x: x*2, T)) # 'T()'







