"""
Core data represenation.


"""
from itertools import *
import cPickle as pickle
import os, sys, bsddb
import logger, util, conf

def path_join(*args):
    return os.path.abspath(os.path.join(*args))

class FileDict(object):
    """
    File based dictionary that can be pickled and restored 
    from a pickle. Built around bsddb.btopen.

    >>> fname = conf.tempdata('filedict-testdata.bin')
    >>> fdict = FileDict(fname, mode='n')
    >>> for value in range(5):
    ...     fdict[value] = value*10
    >>> fdict.save()

    >>> # still works after unpickling the object
    >>> blob = pickle.dumps(fdict)
    >>> db = pickle.loads(blob)
   
    >>> db['1']
    10
    >>> list(db.keys())
    ['0', '1', '2', '3', '4']
    >>> list(db.values())
    [0, 10, 20, 30, 40]
    >>> list(iter(db))
    [0, 10, 20, 30, 40]
    >>> list(db.items())
    [('0', 0), ('1', 10), ('2', 20), ('3', 30), ('4', 40)]
    >>> len(db)
    5
    >>> 4 in db
    True
    >>> 5 in db
    False
    """
    
    def __init__(self, fname, mode='c' ):
        self.fname = path_join( fname )
        try:
            self.db = bsddb.btopen(self.fname, flag=mode)
        except Exception, exc:
            # default error does not indicate the file name
            logger.error('error opening %s' % self.fname)
            raise exc

    def __setitem__(self, key, value):
        self.db[ str(key) ] = pickle.dumps(value, 0)

    def __getstate__(self): 
        # remove file handle
        cdict = self.__dict__.copy()
        del cdict['db']
        return cdict

    def __setstate__(self, data):
        self.db = bsddb.btopen( data['fname'], flag='c')

    def __getitem__(self, key):
        return pickle.loads( self.db[str(key)] )
    
    def save(self):
        self.db.sync()

    def keys( self ):
        return self.db.iterkeys()

    def values( self ):
        return imap(pickle.loads, self.db.itervalues())

    def items( self ):
        return izip(self.keys(), self.values() )

    def __iter__(self):
        return self.values()

    def __contains__(self, key):
        return self.db.has_key(str(key))

    def __len__(self):
        return len(self.db)

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()

def test():
    fname = conf.testdata('filedict-testdata.bin')
    

if  __name__ == '__main__':
    import doctest
    doctest.testmod()

    test()