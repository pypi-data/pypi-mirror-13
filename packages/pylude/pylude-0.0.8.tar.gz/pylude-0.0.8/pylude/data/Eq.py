# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------


#http://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Eq.html

#typeclass
class Eq:


    def __eq__(self, other):
        return self.getPrefix() == other.getPrefix() and self.getValues() == other.getValues()






