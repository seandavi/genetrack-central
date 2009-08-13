"""
Genetrack default smoothing and peak predictions. 

The program may be invoked in multiple ways. As a standalone script::

    python peakpred.py

As a python module::

    python -m genetrack.scripts.peakpred

Or in other python scripts::

>>>
>>> from genetrack.scripts import peakpred
>>> peakpred.predict(inpname, outname, options)
>>>

Run the script with no parameters to see the options that it takes.

**Observed runtime**: 

"""
import os, sys, csv
from genetrack import logger, conf, util, hdflib

def predict(inpname, outname, options):
    """
    Generate the peak predictions on a genome wide scale
    """
    index = hdflib.PositionalData(inpname, nobuild=True)
    
    for label in index.labels:
        table = index.table(label)
        size = len(table)
        info = util.commify(size)
        logger.info('predicting on %s of total size %s' % (label, info))
        lo = 0
        hi = min( (size, options.maxsize) )
        
        while True:
            if lo >= size:
                break
            perc = '%4.1f%%' % (100.0*hi/size)
            logger.info('processing %s %s:%s (%s)' % (label, lo, hi, perc))
            lo = hi
            hi += options.maxsize

def option_parser():
    "The option parser may be constructed in other tools invoking this script"
    import optparse

    usage = "usage: %prog -i inputfile -o outputfile"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-i', '--input', action="store", 
        dest="inpname", type='str', default=None,
        help="the input hdf file name (required)"
    )

    # setting the output file name
    parser.add_option(
        '-o', '--output', action="store", 
        dest="outname", type='str', default=None,
        help="the output file name (required)"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=2, 
        help="sets the verbosity (0, 1, 2) (default=1)",
    )

    # sigma correction
    parser.add_option(
        '--sigma', action="store", 
        dest="sigma", type="float", default=20, 
        help="the smoothing factor",
    )

    # the exclusion zone
    parser.add_option(
        '--exclusion', action="store", 
        dest="exclude", type="int", default=100, 
        help="the exclusion zone",
    )

    # threshold
    parser.add_option(
        '--level', action="store", 
        dest="level", type="float", default=1, 
        help="the minimum signal necessary to call peaks",
    )

    # currently not used
    parser.add_option(
        '--mode', action="store", 
        dest="mode", type="str", default='maximal', 
        help="the peak prediction method: 'maximal', 'threshold' or 'all'",
    )

    parser.add_option(
        '--maxsize', action="store", 
        dest="maxsize", type="int", default=10**7, 
        help="the size of the largest internal array allocated (default=10 million)",
    )
    return parser


if __name__ == '__main__':
    import optparse

    parser = option_parser()

    options, args = parser.parse_args()

    logger.disable(options.verbosity)

    # override as text
    options.inpname = conf.testdata('short-good-input.gtrack')
    options.outname = conf.tempdata('predictions-short-good-input.bed')

    # missing input file name
    if not options.inpname and not options.outname:
        parser.print_help()
    else:
        predict(options.inpname, options.outname, options)
