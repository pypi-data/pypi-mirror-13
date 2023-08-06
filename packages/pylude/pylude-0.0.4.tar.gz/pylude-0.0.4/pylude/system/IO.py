
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


def writeFile(path,content):
    """
    writeFile :: str -> str -> None
    The computation writeFile file str function writes the string str, to the file file.
    """
    f = open(path,"w")
    f.write(content)
    f.close()


def appendFile(path,content):
    """
    writeFile :: str -> str -> None
    The computation writeFile file str function writes the string str, to the file file.
    """
    f = open(path,"a")
    f.write(content)
    f.close()

#Special cases for standard input and output


def putChar(c):
    print(c)

def putStrLn(s):
    print(s)


def getLine():
    return input()



#Binary input and output
















