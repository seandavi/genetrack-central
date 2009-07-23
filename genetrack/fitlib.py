"""
Data fitting and peak prediction routines
"""
import genetrack
from genetrack import logger, conf
from itertools import *
import numpy, operator
from math import log, exp

def normal_function( w, sigma ):
    """
    Defaulf fitting function, it returns values 
    from a normal distribution over a certain width.

    The function is not normalized thus will be a representation of the sum of readcounts.
    """
    log2    = log(2)
    sigma2  = float(sigma)**2
    lo, hi  = int(-w), int(w+1)
    pi = numpy.pi

    # function definition, not normalized
    # thus will correspond to read counts
    def normal_func(index):
        return exp( -index*index/sigma2/2 )    
    
    values = map( normal_func, range(lo, hi) )
    values = numpy.array( values, numpy.float )

    return abs(lo), hi, values

def gaussian_smoothing(x, y, sigma=20, epsilon=0.1 ):
    """
    Fits data represented by f(x)=y with a sum of normal curves.
    Returns the new x, and y coordinates.
    """

    # this is a joyfully simple, marvelously elegant and superfast solution 
    # that's possible thanks to numpy. I bow before thy greatness, NumPY!!!

    # transform to numpy arrays
    x = numpy.array( x, numpy.int )
    y = numpy.array( y, numpy.float )

    # a sanity check
    assert len(x)==len(y), "Data lenghts must match!"

    # operate within 5 standard deviations
    w = 5 * sigma 

    # precompute the fitting values for a given sigma,
    lo, hi, normal = normal_function( w=w, sigma=sigma )

    # shift the original vector by the first index, so that 
    # the first index starts at the value abs(lo)
    # this copies the array
    zero_x = x - x[0] + lo

    # the size will influence memory consumption
    # long vectors need to be stiched together externally
    # uses around 100MB per 10 million size
    # on live displays there is no need to fit over large regions (over 100K)
    # as the features won't be visible by eye 
    size  = zero_x[-1] + lo + hi + 1 

    # this will hold the new fitted values
    new_y = numpy.zeros( size, numpy.float )

    # performs the smoothing by mutating the array values in place
    for index, value in izip(zero_x, y):
        lox = index - lo
        hix = index + hi
        # this is where the magic happens
        new_y[ lox:hix ] += value * normal
    
    # keep only values above the epsilon
    # this cuts out (potentially massive) regions where there are no measurements
    new_x = ( new_y > epsilon ).nonzero()[0] 
    new_y = new_y.take(new_x)

    # now shift back to get the real indices
    new_x =  new_x + x[0] - lo

    return new_x, new_y

def select_peaks( peaks, width, level=0):
    """
    Selects successive non-overlapping peaks 
    with a given exclusion zone.

    Takes as input a list of (index, value) tuples.

    Returns a list of tuples = ( midpoint, maxima )
    """
     
    # order by peak height
    work  = [ (y, x) for x, y in peaks if y >= level and x > width ]
    work.sort()
    work.reverse()

    # sanity check
    if not work:
        return []

    #largest index        
    xmax = max(work, key=operator.itemgetter(1) )[1]
    
    # selected peaks
    selected = []

    # keeps track of empty regions
    empty = numpy.ones( xmax+width+1, numpy.int8 )
    half  = width/2 + 1
    for peaky, peakx in work:
        if empty[peakx]:
            left  = peakx - width
            right = peakx + width
            # store into output data
            selected.append( ( peakx, peaky ) )
            # block the region
            empty[left:right] = numpy.zeros (right - left, numpy.int8)

    selected.sort()
    return selected

def detect_peaks( index, data ):
    """
    Detects peaks (local maxima) from an iterator that returns 
    float values. Input data is a list of tuples containing 
    the index and the value at the index.
    
    Returns a generator yielding tuples that corresponds 
    to the peak index and peak value.
    
    >>> data  = [ 0.0, 1.0, 2.5, 1.0, 3.5, 1.0, 0.0, 0.0, 10.5, 2.0, 1.0, 0.0 ]
    >>> index = range(len(data))
    >>> peaks = detect_peaks( index=index, data=data )
    >>> peaks
    [(2, 2.5), (4, 3.5), (8, 10.5)]
    >>> select_peaks( peaks, width=1)
    [(2, 2.5), (4, 3.5), (8, 10.5)]
    >>> select_peaks( peaks, width=2)
    [(4, 3.5), (8, 10.5)]
    """
    peaks = []
    indices = xrange(1, len(data)-1 )
    for i in indices:
        left, mid, right = data[i-1], data[i], data[i+1]
        if left < mid >= right:
            peaks.append( (index[i], mid) )
    return peaks

def fixed_width_predictor(index, data, params):   
    "Detects peaks in the data and returns them as intervals"
    width = params.feature_width        
    level = params.minimum_peak
    allpeaks = detect_peaks(index, data)

    peaks = select_peaks( allpeaks, width=width, level=level)

    results = []
    half = width/2
    for x, y in peaks:
        start = x - half
        end   = x + half
        results.append( (start, end, y) )

    return results

def test(verbose=0):
    """
    Main testrunnner
    """
    import doctest
    doctest.testmod( verbose=verbose )
     
if __name__ == '__main__':
    test(verbose=0)
    from pylab import *

    x = [ 1, 100,  500, 1000, 1010, 2000, 2500 ]
    y = [ 1,   1,    5,    1,  1,   2, 2.5  ]

    nx, ny  = gaussian_smoothing(x, y, sigma=50)

    print len(nx), nx
    print len(ny), ny

    plot(nx, ny, 'bo-')
    show()
    


