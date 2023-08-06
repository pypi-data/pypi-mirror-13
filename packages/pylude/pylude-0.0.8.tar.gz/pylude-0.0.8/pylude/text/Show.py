# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------




#http://hackage.haskell.org/package/base-4.8.1.0/docs/Text-Show.html


class Show:


    def __str__(self):
        return self.getPrefix() + "("+ ", ".join(map(str, self.getValues())) +")"


    def __repr__(self):
        return self.getPrefix() + "("+ ", ".join(map(str, self.getValues())) +")"


