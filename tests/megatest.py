"""
Runs a more demaniding test
"""
import os
from genetrack import util, conf, logger, scripts
from genetrack.scripts import bed2genetrack

logger.disable(None)

def bedfile(inpfile):
    basename = os.path.basename(inpfile)
    outfile = conf.tempdata('%s.genetrack' % basename)
    bed2genetrack.transform(inpfile, outfile)

if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser()

    # setting the input file name
    parser.add_option(
        '--bed2genetrack', 
        dest="bed2genetrack",
        help="run the bed2genetrack transform on a file"
    )

    options, args = parser.parse_args()
    
    if options.bed2genetrack:
        bedfile(options.bed2genetrack)
    

