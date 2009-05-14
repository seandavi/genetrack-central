"""
Helper functions
"""
import os, sys, csv
from genetrack import logger, conf, util

def transform(inpname, outname, shift=0):
    """
    Transforms reads stored in bedfile to a genetrack input file.
    Requires at least 6 bed columns.

    it is a three step process, transform, sort and consolidate. It 
    will create files placed in the temporary data directory.
    """

    # find the basename of the outputname
    basename = os.path.basename(outname)
   
    # check for track information on first line, 
    # faster this way than conditional checking on each line
    fp = file(inpname, 'rU')
    first = fp.readline()
    fp.close()

    # create the reader
    reader = csv.reader(file(inpname, 'rU'), delimiter='\t')

    # skip if trackline exists
    if first.startswith == 'track':
        reader.next()

    timer, full = util.Timer(), util.Timer()

    logger.debug("parsing '%s'" % inpname)
    logger.debug("output to '%s'" % outname)

    # write the unsorted output file
    nonsort = conf.tempdata( '%s.temp' % basename )
    logger.debug("unsorted file '%s'" % nonsort)

    op = file(nonsort, 'wt')
    #op.write('#\n# transformed from \%s\n#\n' % inpname)
    #op.write('chrom\tindex\tforward\treverse\tvalue\n')
    for row in reader:
        chrom, start, end, strand = row[0], row[1], row[2], row[5]
        if strand == '+':
            start = int(start)
            idx = start + shift 
            fwd, rev, val = 1, 0, 1
        elif strand == '-':
            end = int(end)
            idx = end - shift
            fwd, rev, val = 1, 0, 1
        else:
            start = int(start)
            end = int(end)
            idx = (start+end)/2
            fwd, rev, val = 1, 0, 1
        op.write('%s\t%09d\t%s\t%s\t%s\n' % (chrom, idx, fwd, rev, val))
    op.close()

    logger.debug("parsing finished in %s" % timer.report() )

    # now let sorting commence
    
    sortdata = conf.tempdata( '%s.sorted' % basename )

    cmd = "sort %s > %s" % (nonsort, sortdata)
    logger.debug("sorting into '%s'" % sortdata)
    os.system(cmd)
    logger.debug("sorting finished in %s" % timer.report() )

    logger.debug("consolidating into '%s'" % sortdata)
    #os.system(cmd)
    logger.debug("consolidate finished in %s" % timer.report() )
    logger.debug("full run finished in %s" % full.report() )

    os.remove(nonsort)
    os.remove(sortdata)

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog -i inputfile -o outputfile -s correction (default=0)"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-i', '--input', action="store", 
        dest="inpname", type='str', default=None,
        help="the input file name"
    )

    # setting the output file name
    parser.add_option(
        '-o', '--output', action="store", 
        dest="outname", type='str', default=None,
        help="output file name"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) [default]",
    )

    # correction shift added in 5' direction for start/end coordinates
    parser.add_option(
        '-s', '--shift', action="store", 
        dest="shift", type="int", default=0, 
        help="sets the correction shift for each strand (default=0)",
    )

    options, args = parser.parse_args()

    # missing file names
    if not (options.inpname and options.outname):
        parser.print_help()
        sys.exit()

    if options.verbosity > 0:
        logger.disable(None)

    #transform(inpname=options.inpname, outname=options.outname, shift=options.shift)