"""
Runs a more demaniding test
"""
from genetrack import util, conf, logger, scripts

logger.disable(None)

def test():
    inpfile = conf.testdata('big-yeast.bed', verify=True)
    outfile = conf.tempdata('big-yeast.genetrack')
    bed2genetrack.transform(inpfile, outfile)

if __name__ == '__main__':
    test()