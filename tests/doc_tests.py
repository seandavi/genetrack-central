""""
This script runs the doctests
"""
import testlib
import os, unittest, doctest
from genetrack import data, hdflib

def codetest():
    "Test the code here before adding to doctest"
    pass

def get_suite():
    suite = unittest.TestSuite()
    
    file_names = [
        
    ]

    module_names = [
        data, hdflib
    ]

    # needs relative paths for some reason
    full_path = lambda name: os.path.join( '../docs/rest', name)
    file_paths = map( full_path, file_names)

    for file_path in file_paths:
        rest_suite = doctest.DocFileSuite( file_path )
        suite.addTest( rest_suite )

    for mod in module_names:
        docsuite = doctest.DocTestSuite( mod )
        suite.addTest( docsuite )

    return suite

if __name__ == '__main__':
    #codetest()
    suite  = get_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)