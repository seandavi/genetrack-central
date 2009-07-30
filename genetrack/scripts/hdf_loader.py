"""
Genetrack file transformer. 

The program may be invoked in multiple ways. As a standalone script::

    python hdf_loader.py

As a python module::

    python -m genetrack.scripts.hdf_loader

Or in other python scripts::

>>>
>>> from genetrack.scripts import hdf_loader
>>> hdf_loader.transform(inpname)
>>>

Run the script with no parameters to see the options that it takes.

**Observed runtime**: insertion rate of 6 million lines per minute

"""
import os, sys, csv
from genetrack import logger, conf, util, hdflib


def transform(inpname, workdir=None, update=False):
    """
    Creates a transform from a genetrack input file
    """
    index = hdflib.PositionalData(fname=inpname, workdir=workdir, update=update)        
    return index

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog -i inputfile"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-i', '--input', action="store", 
        dest="inpname", type='str', default=None,
        help="the input file name (required)"
    )

    # setting the output file name
    parser.add_option(
        '-w', '--workdir', action="store", 
        dest="workdir", type='str', default=None,
        help="work directory (optional)"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    parser.add_option("-u", "--update",
        action="store_true", dest="update", default=False,
        help="recreates the index even if it exists")

    options, args = parser.parse_args()

    # set verbosity
    logger.disable( options.verbosity )

    # missing input file name
    if not options.inpname:
        parser.print_help()
    else:
        transform(inpname=options.inpname, workdir=options.workdir, update=options.update)
