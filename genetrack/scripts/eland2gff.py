"""
Eland file transformer. Transforms an eland file
to a gff file format.

    python eland2gff.py

As a python module::

    python -m genetrack.scripts.eland2gff

Or in other python scripts::

>>>
>>> from genetrack.scripts import eland2gff
>>> eland2gff.transform(inpname, outname)
>>>

Run the script with no parameters to see the options that it takes.

**Observed runtime**: tranformation rate of 5 million lines per minute

"""
import os, sys, csv
from itertools import *
from genetrack import logger, conf, util


def transform(inpname, size, outname=None):
    """
    Transforms reads stored in bedfile to a genetrack input file.
    Requires at least 6 bed columns to access the strand.
    """
    logger.debug('input %s' % inpname)
    logger.debug('output %s' % outname)

    reader = csv.reader(open(inpname), delimiter='\t')

    # unwind the iterator 
    list(takewhile( lambda x: x[0].startswith('#'), reader))

    output = file(outname, 'wt')
    output.write('##gff-version 3\n') 
    output.write('# created with eland2gff on %s\n' % inpname)
    output.write('# fixed read lenght of %s\n' % size)
    for row in reader:
        chrom, start, strand = row[10], int(row[12]), row[13]
        end = start + size
        if strand == 'F':
            strand = '+'
        else:
            strand = '-'
        result = map(str, [chrom, '.', '.', start, end, '.', strand, '.', '.'])
        output.write("%s\n" % '\t'.join(result))
    
    output.close()

def option_parser():
    "The option parser may be constructed in other tools invoking this script"
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
        help="output file name (optional)"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    # correction shift added in 5' direction for start/end coordinates
    parser.add_option(
        '-s', '--size', action="store", 
        dest="size", type="int", default=36, 
        help="readlength (fixed) default 36",
    )

    return parser

if __name__ == '__main__':
    
    parser = option_parser()

    options, args = parser.parse_args()

    # set verbosity
    logger.disable(options.verbosity)

    # missing file names
    if not options.inpname:
        parser.print_help()
    else:
        options.outname=options.outname or '%s.gff' % options.inpname
        transform(inpname=options.inpname, outname=options.outname, size=options.size)
