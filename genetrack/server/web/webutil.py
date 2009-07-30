"""
Various utility functions
"""
from django.conf import settings
import os, random, hashlib, time, glob, stat


def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

def uuid(KEY_SIZE=128):
    "Genenerates a unique id"
    id  = str( random.getrandbits( KEY_SIZE ) )
    return hashlib.md5(id).hexdigest()

def cache_file(name=None, ext=None):
    "Generates a path to the cache directory"
    name = name or uuid()
    name = '%s.%s' % (name, ext) if ext else name
    path = path_join(settings.CACHE_DIR, name  )
    return name, path

def cache_clean(name=None, age=1, chance=1):
    "Cleans the cache directory. Chance to trigger, file age in seconds"
    if chance < random.randint(1, 100):
        return
    expiration = time.time()
    fpatt = path_join(settings.CACHE_DIR, '*')
    for fname in glob.glob(fpatt):
        ctime = os.stat(fname)[stat.ST_CTIME ]
        ctime += age * 3600 * 24 * 7 # in days
        if ctime < expiration:
            os.remove(fname)
        
if __name__ == '__main__':
    
    cache_clean()

