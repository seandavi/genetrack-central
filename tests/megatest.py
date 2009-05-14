"""
Runs a more demaniding test
"""
from genetrack import util, conf, logger, scripts
from genetrack.scripts import bed2genetrack

logger.disable(None)

def bed1():
    inpfile = conf.testdata('big-yeast.bed', verify=True)
    outfile = conf.tempdata('big-yeast.genetrack')
    bed2genetrack.transform(inpfile, outfile)

if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser()

    # setting the input file name
    parser.add_option(
        '--bed1', action="store_true", 
        dest="bed1",  default=False,
        help="run the bed2genetrack tests"
    )

    options, args = parser.parse_args()
    
    if options.bed1:
        bed1()
    