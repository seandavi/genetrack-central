"""
Data analysis and visualization framework for genomic data. 
See the genetrack_ site for installation instructions.

Framework
=========

Required libraries: numpy_ , bx-python_ and pytables_

Server
======

Required libraries: django_ and chartdirector_

The default webserver is located under the `server` directory 
and is completely independent of the main genetrack package and therefore is **NOT** documented
here. The server is implemented with the django_ web framework. See the genetrack_ site for 
more details about the server settings.

.. _genetrack: http://genetrack.bx.psu.edu
.. _numpy: http://numpy.scipy.org
.. _bx-python: http://bitbucket.org/james_taylor/bx-python/wiki/Home
.. _django: http://www.djangoproject.com/
.. _pytables: http://www.pytables.org/
.. _chartdirector: http://www.advsofteng.com
"""
import sys
from time import strftime, gmtime

tstamp = strftime("%Y-%j", gmtime() )

__version__ = '2.0.0-beta-1'

# version check
if sys.version_info < (2, 5):
    error( 'genetrack requires python 2.5 or higher' )

from genetrack.hdflib import PositionalData

if __name__ == '__main__':
    print '\n*** GeneTrack import successful ***'

