====================
Pylude
====================

Cloning the Haskell-Prelude for Python3 :
http://hackage.haskell.org/package/base-4.8.1.0/docs/Prelude.html


*** MAKING PYTHON GREAT AGAIN! ***


Features
========


The newType function
-----------------------


.. code:: python

    Just, Nothing = newType('Maybe', ('Just', 1), ('Nothing', 0), deriving={Eq, Show})


constructor matching
-----------------------

.. code:: python

    def isJust(x):
        return Just(match=x)

    def isNothing(x):
        return x==Nothing


type-classes
-----------------

.. code:: python

    def mapB(func, b):
        return b


    T, F = newType("B", ("T",0), ("F",0), deriving={Eq, Show}, implements={Functor : {"fmap" : mapB} })

    print(fmap(lambda x: x*2, T)) # 'T()'




operators
-----------------

.. code:: python

    # Application operator $ as |

    @pylu
    def f(x):
        return x

    print( f | (lambda x: x*3) | (lambda x: x+1) | 2) #9


    # Function composition . as *

    g = (lambda x: x*3) * f * (lambda x: x+1) * (lambda x: x+1)

    print(g(2)) #8







