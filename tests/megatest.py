"""
Runs a more demaniding test
"""
from genetrack import util, conf, logger, helper

logger.disable(None)

def test():
    inpfile = conf.testdata('big-yeast.bed', verify=True)
    outfile = conf.tempdata('big-yeast.genetrack')
    helper.bedreads2genetrack(inpfile, outfile)

if __name__ == '__main__':
    test()