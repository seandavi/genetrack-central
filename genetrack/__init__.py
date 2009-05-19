"""
GeneTrack
=========

Data analysis and visualization framework for genomic data. 

Note:: The default webserver is located under the `server` directory 
and is completely independent of the main genetrack package. The server 
is implemented with the Django web framework.

"""
import sys
from time import strftime, gmtime

tstamp = strftime("%Y-%j", gmtime() )

__version__ = '2.0.0b-%s' % tstamp

# version check
if sys.version_info < (2, 5):
    error( 'genetrack requires python 2.5 or higher' )




