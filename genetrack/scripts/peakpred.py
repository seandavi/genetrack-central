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
from genetrack import logger, util, hdflib, fitlib

TWOSTRAND = "two"

commify = util.commify

def output(stream, peaks, chrom, w=73, strand='+', ):
    "Outputs peaks to a stream"

    logger.debug('writing %s peaks on strand %s' % (commify(len(peaks)), strand))
    for mid, value in peaks:
        start, end = mid - w, mid + w
        stream.write("%s\t%d\t%d\t.\t%f\t%s\n" % (chrom, start, end, value, strand))

def predict(inpname, outname, options):
    """
    Generate the peak predictions on a genome wide scale
    """
    if options.strand == TWOSTRAND:
            logger.info('operating in twostrand mode')

    if options.index:
        index = hdflib.PositionalData(fname='', index=inpname, nobuild=True, workdir=options.workdir)
    else:
        index = hdflib.PositionalData(fname=inpname, nobuild=True, workdir=options.workdir)

    fp = file(outname, 'wt')

    for label in index.labels:
        table = index.table(label)
        size  = table.cols.idx[-1]
        info  = util.commify(size)
        logger.info('predicting on %s of total size %s' % (label, info))
        lo = 0
        hi = min( (size, options.maxsize) )

        while True:
            if lo >= size:
                break
            perc = '%.1f%%' % (100.0*lo/size)
            logger.info('processing %s %s:%s (%s)' % (label, lo, hi, perc))
            
            # get the data
            res = index.query(start=lo, end=hi, label=label)

            
            # exclusion zone
            w = options.exclude/2

            def predict(x, y):
                fx, fy = fitlib.gaussian_smoothing(x=x, y=y, sigma=options.sigma, epsilon=options.level )
                peaks = fitlib.detect_peaks(x=fx, y=fy )
                if options.mode != 'all':
                    peaks = fitlib.select_peaks(peaks=peaks, exclusion=options.exclude, threshold=options.level)
                return peaks

            if options.strand == TWOSTRAND:
                # operates in two strand mode
                for yval, strand in [ (res.fwd, '+'), (res.rev, '-') ]:
                    logger.debug('processing strand %s' % strand)
                    peaks = predict(x=res.idx, y=yval)
                    output(stream=fp, peaks=peaks, chrom=label, w=w, strand=strand)
            else:
                # combine strands
                peaks = predict(x=res.idx, y=res.val)
                output(stream=fp, peaks=peaks, chrom=label, w=w, strand='+')

            # switching to a higher interval
            lo = hi
            hi += options.maxsize
        
    fp.close()

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

    # the exclusion zone
    parser.add_option(
        '--strand', action="store", 
        dest="strand", type="str", default="ALL", 
        help="strand",
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

    parser.add_option(
        '--test', action="store_true", 
        dest="test", default=False, 
        help="demo mode used in testing",
    )

    parser.add_option(
        '-w', '--workdir', action="store", 
        dest="workdir", type='str', default=None,
        help="work directory (optional)"
    )

    parser.add_option(
        '-x', '--index', action="store_true", 
        dest="index", default=False,
        help="treat input file as binary index"
    )

    return parser


if __name__ == '__main__':
    import optparse

    parser = option_parser()

    options, args = parser.parse_args()

    logger.disable(options.verbosity)

    from genetrack import conf

    # trigger test mode
    if options.test:
        options.inpname = conf.testdata('test-hdflib-input.gtrack')
        options.outname = conf.testdata('predictions.bed')

    # missing input file name
    if not options.inpname and not options.outname:
        parser.print_help()
    else:
        print 'Sigma = %s' % options.sigma
        print 'Minimum peak = %s' % options.level
        print 'Peak-to-peak = %s' % options.exclude

        predict(options.inpname, options.outname, options)
