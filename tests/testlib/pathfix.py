"""
The sole purpose of this module is to alter the sys.path upon
importing to add the current genetrack package's path first into 
the import path
"""
import sys, os

def path_join(*args):
    return os.path.abspath(os.path.join(*args))

curr_dir = os.path.dirname( __file__ )
test_dir = path_join(curr_dir, '..')
base_dir = path_join(curr_dir, '..', '..' )
lib_dir  = path_join(base_dir, 'library')
zip_dir  = path_join(lib_dir, 'library.zip')

for path in [ base_dir, lib_dir, zip_dir ]:
    if path not in sys.path:
        sys.path.insert(0, path )

# test that the modules in library.zip are accessible
import twill, figleaf
