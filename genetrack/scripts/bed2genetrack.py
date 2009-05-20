"""
Bed file transformer. Requires the presence of 
at least 6 bed columns to access the strand.
Optional parameters may be used to shift the 5' ends with 
a specified amount. This is useful if the bed file corresponds to data with fixed fragment 
widths you can move each fragment to the center location. 
The program may be invoked in multiple ways. As a standalone script::

    python bed2genetrack.py

As a python module::

    python -m genetrack.scripts.bed2genetrack

Or in other python scripts::

>>>
>>> from genetrack.scripts import bed2genetrack
>>> bed2genetrack( input_name, output_name, shift=0)
>>>

Run the script with no parameters to see the options that it takes.

A genetrack input file format is a tab delimited text file
described in the API documentation of the LinearData 
class: `genetrack.hdflib.LinearData`
The transformation is a three step process, *transform*, 
*sort* and *consolidate*. It will create files in the 
genetrack temporary data directory and it will remove the intermediate files 
when the process is complete.

**Observed runtime**: tranformation rate of 2 million lines per minute

**Note1**: The script will invoke the system `sort` command to sort the file 
that is substantially faster under Unix than Windows.

"""
import os, sys, csv
from genetrack import logger, conf, util

def consolidate( inpname, outname):
    """
    Consolidates an input file. 
    Merges multiple indentical indices into one line
    """
    fp = open(outname, 'wt')

    # recover the original basename
    basename = os.path.basename(inpname).replace('.sorted', '')

    # create a few information headers
    fp.write("#\n# created with bed2genetrack\n")
    fp.write("# source: %s\n#\n" % basename)
    fp.write("chrom\tindex\tforward\treverse\tvalue\n")
    
    # the main reader
    reader = csv.reader(open(inpname, 'rb'), delimiter='\t')

    # will duplicate some code to avoid an extra conditional internally
    chrom, index, fwd, rev, val = reader.next()
    lastindex, fwd, rev, val = int(index), int(fwd), int(rev), int(val)
    collect = [ chrom, lastindex, fwd, rev, val ]

    for row in reader:
        chrom, index, fwd, rev, val = row
        index, fwd, rev, val = int(index), int(fwd), int(rev), int(val)
        if index == lastindex:
            collect[2] += fwd
            collect[3] += rev
            collect[4] += val
        else:
            # write out the collected data
            fp.write( '%s\t%s\t%s\t%s\t%s\n' % tuple(collect) )
            collect = [ chrom, index, fwd, rev, val ]
            lastindex = index

    fp.close()

def transform(inpname, outname, shift=0):
    """
    Transforms reads stored in bedfile to a genetrack input file.
    Requires at least 6 bed columns to access the strand.
    """

    # find the basename of the outputname
    basename = os.path.basename(outname)
   
    # two files store intermediate results
    flat = conf.tempdata( '%s.flat' % basename )
    sorted  = conf.tempdata( '%s.sorted' % basename )

    # check for track information on first line, 
    # much faster this way than conditional checking on each line
    fp = file(inpname, 'rU')
    first = fp.readline()
    fp.close()

    # create the reader
    reader = csv.reader(file(inpname, 'rU'), delimiter='\t')

    # skip if trackline exists
    if first.startswith == 'track':
        reader.next()

    # copious timing info for those who enjoy these
    timer, full = util.Timer(), util.Timer()

    logger.debug("parsing '%s'" % inpname)
    logger.debug("output to '%s'" % outname)

    # create the unsorted output file and apply corrections
    logger.debug("unsorted flat file '%s'" % flat)

    fp = file(flat, 'wt')
    for row in reader:
        chrom, start, end, strand = row[0], row[1], row[2], row[5]
        if strand == '+':
            # on forward strand, 5' is at start
            idx = int(start) + shift
            fwd, rev, val = 1, 0, 1
        elif strand == '-':
            # on reverse strand, 5' is at end
            idx = int(end) - shift
            fwd, rev, val = 0, 1, 1
        else:
            # no strand specified, generate interval centers
            idx = (int(start)+int(end))/2
            fwd, rev, val = 0, 0, 1

        # it is essential be able to sort the index as a string! 
        fp.write('%s\t%09d\t%s\t%s\t%s\n' % (chrom, idx, fwd, rev, val))

    fp.close()
    logger.debug("parsing finished in %s" % timer.report() )

    # now let the sorting commence
    cmd = "sort %s > %s" % (flat, sorted)
    logger.debug("sorting into '%s'" % sorted)
    os.system(cmd)
    logger.debug("sorting finished in %s" % timer.report() )

    logger.debug("consolidating into '%s'" % outname)
    consolidate( sorted, outname)
    logger.debug("consolidate finished in %s" % timer.report() )
    logger.debug("output saved to '%s'" % outname)
    logger.debug("full run finished in %s" % full.report() )

    # attempting to cleanup the remaining files
    for name in (flat, sorted):
        #os.remove(name)
        pass

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog -i inputfile -o outputfile"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-i', '--input', action="store", 
        dest="inpname", type='str', default=None,
        help="the input file name (required)"
    )

    # setting the output file name
    parser.add_option(
        '-o', '--output', action="store", 
        dest="outname", type='str', default=None,
        help="output file name (required)"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    # correction shift added in 5' direction for start/end coordinates
    parser.add_option(
        '-s', '--shift', action="store", 
        dest="shift", type="int", default=0, 
        help="shift for the 5' end on each strand (default=0)",
    )

    options, args = parser.parse_args()

    # set verbosity
    if options.verbosity > 0:
        logger.disable(None)

    # missing file names
    if not (options.inpname and options.outname):
        parser.print_help()
    else:
        transform(inpname=options.inpname, outname=options.outname, shift=options.shift)
