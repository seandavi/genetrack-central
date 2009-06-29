"""
Running this script will attempt to download and 
install the required python related libraries 
into the library directory.
"""
import sys, os, platform, urllib

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

URL = "http://genetrack.bx.psu.edu/libs"
LIBDIR = path_join(os.path.dirname( __file__ ))

def execute():

    try:
        # install pychardir
        import pychartdir
    except ImportError, exc:
        pass

    print platform.plaform

if __name__ == '__main__':
    execute()

