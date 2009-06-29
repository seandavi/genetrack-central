"""
Data Generator
"""
import random
import pathfix
from testutil import commify

def fasta_generator(fname, seqnum, seqlen):
    """
    Generates a FASTA file
    """
    fp = file( fname, 'wt')
    seq = [ random.choice("ATGC") for x in range(seqlen) ]
    
    snum, slen = commify(seqnum ), commify(seqlen )
    print "Fasta Generator N=%s L=%s into '%s' " % (snum, slen, fname) 

    for id in xrange( seqnum):
        line1 = "id%06d" % id
        random.shuffle( seq )
        line2 = "".join( seq ) 
        fp.write( '>%s\n' % line1 )
        fp.write( '%s\n' % line2 )

    fp.close()

def run():
    seqnum = 10**5
    seqlen = 10**2
    fname = 'data/100K.fasta'
    fasta_generator( fname, seqnum, seqlen)

if __name__ == '__main__':
    run()