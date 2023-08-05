from os.path import splitext, getsize, basename, dirname, isdir
from os import makedirs
from sys import argv
import pickle

def setVar(key, val, t='data'):
    d = dirname(argv[0])
    n = splitext(basename(argv[0]))[0]
    path = d + '/data/' + n + '_' + t + '.dat'
    
    try:
        
        file = open(path, 'rb')

        if (getsize(path) > 0):
            v = pickle.load(file)
            v.update({key: val})
            file.close()
        else:
            v = {key: val}
        

    except FileNotFoundError:
        if (not isdir(d + '/data/')):
            makedirs(d + '/data/')
            
        open(path, 'w+').close()
        v = {key: val}

    file = open(path, 'wb')
    pickle.dump(v, file)
    file.close()
    return v

def getVar(key, t='data'):
    d = dirname(argv[0])
    n = splitext(basename(argv[0]))[0]
    path = d + '/data/' + n + '_' + t + '.dat'

    try:
        file = open(path, 'rb')

        if (getsize(path) > 0):
            v = pickle.load(file)
            file.close()

            if (key in v):
                return v[key]

    except:
        pass
    return None

def getAllVars(t='data'):
    return delVar(None, t)

def delVar(key, t='data'):
    d = dirname(argv[0])
    n = splitext(basename(argv[0]))[0]
    path = d + '/data/' + n + '_' + t + '.dat'

    try:
        file = open(path, 'rb')

        if (getsize(path) > 0):
            v = pickle.load(file)
            file.close()

            if (key in v):
                del v[key]

                file = open(path, 'wb')
                pickle.dump(v, file)
                file.close()

            return v
    except:
        pass

    return None
                

            
