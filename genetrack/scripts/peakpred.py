"""
Genetrack default smoothing and peak predictions. 

The program may be invoked in multiple ways. As a standalone script::

    python peakpred.py

As a python module::

    python -m genetrack.scripts.peakpred

Or in other python scripts::

>>>
>>> from genetrack.scripts import peakpred
>>> peakpred.smooth(x, y, sigma)
>>>

Run the script with no parameters to see the options that it takes.

**Observed runtime**: 

"""
import os, sys, csv
from genetrack import logger, conf, util, hdflib

def smooth(x, y, sigma):
    """
    Smooths the x,y data and returns two larger arrays with 
    containing the averaged data. Uses a gaussina kernel to
    average neighbouring points.
    """
    
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
