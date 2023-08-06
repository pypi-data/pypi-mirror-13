# --------------------------------------------------------
# (c) Copyright 2016 by Tobias Weise. 
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------



#http://hackage.haskell.org/package/base-4.8.1.0/docs/System-IO.html



#def withFile


#def openFile(path, mode):


def readFile(path):
    """
    readFile :: str -> str
    The readFile function reads a file and returns the contents of the file as a string.
    """
    f = open(path,"r")
    c = f.read()
    f.close()
    return c


def writeFile(path, content):
    """
    writeFile :: str -> str -> None
    The computation writeFile file str function writes the string str, to the file file.
    """
    if type(content) == str:
        f = open(path,"w")
        f.write(content)
        f.close()
    elif type(content) == bytes:
        f = open(path,"wb")
        f.write(content)
        f.close()



def appendFile(path,content):
    """
    writeFile :: str -> str -> None
    The computation writeFile file str function writes the string str, to the file file.
    """
    if type(content) == str:
        f = open(path,"a")
        f.write(content)
        f.close()
    elif type(content) == bytes:
        f = open(path,"ab")
        f.write(content)
        f.close()

#Special cases for standard input and output


#def putChar(c):
#    print(c)

putChar = print

#def putStrLn(s):
#    print(s)


putStrLn = print


#def getLine():
#    return input()

getLine = input


#Binary input and output
















