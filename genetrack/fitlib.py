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
    Fits data represented by f(x)=y by a sum of normal curves where
    each curve corresponds to a normal function of variance=sigma and
    height equal to the y coordinate.

    Parameters x and y are lists.

    Returns a tuple of with the new x, and y coordinates.
    """
    if len(x)==0:
        return x, y

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
    # the first index starts at the value lo
    # this copies the array
    zero_x = x - x[0] + lo

    # the size will influence memory consumption
    # long vectors need to be stiched together externally
    # uses around 100MB per 10 million size
    # on live displays there is no need to fit over large regions (over 100K)
    # as the features won't be visible by eye 
    size  = zero_x[-1] + lo + hi

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

def detect_peaks( x, y ):
    """
    Detects peaks (local maxima) from an iterators x and y 
    where f(x)=y. Will not propely detect plateus!

    Returns a list of tuples where the two
    elements correspond to the peak index and peak value.
    
    >>> y = [ 0.0, 1.0, 2.5, 1.0, 3.5, 1.0, 0.0, 0.0, 10.5, 2.0, 1.0, 0.0 ]
    >>> x = range(len(y))
    >>> peaks = detect_peaks( x=x, y=y )
    >>> peaks
    [(2, 2.5), (4, 3.5), (8, 10.5)]
    >>> select_peaks( peaks, exclusion=1)
    [(2, 2.5), (4, 3.5), (8, 10.5)]
    >>> select_peaks( peaks, exclusion=2)
    [(4, 3.5), (8, 10.5)]
    """
    peaks = []
    # finds local maxima 
    for i in xrange(1, len(y)-1 ):
        left, mid, right = y[i-1], y[i], y[i+1]
        if left < mid >= right:
            peaks.append( (x[i], mid) )
    return peaks

def select_peaks( peaks, exclusion, threshold=0):
    """
    Selects maximal non-overlapping peaks with a given exclusion zone 
    and over a given treshold.

    Takes as input a list of (index, value) tuples corresponding to
    all local maxima. Returns a filtered list of tuples (index, value)
    with the maxima that pass the conditions.

    >>> peaks = [ (0, 20), (100, 19), (500, 4), (10**6, 2) ]
    >>> select_peaks( peaks, exclusion=200)
    [(0, 20), (500, 4), (1000000, 2)]
    """

    # zero exclusion allows all peaks to pass
    if exclusion == 0:
        return peaks

    # sort by peak height
    work  = [ (y, x) for x, y in peaks if y >= threshold ]
    work.sort()
    work.reverse()

    # none of the values passed the treshold
    if not work:
        return []

    # this will store the selected peaks
    selected = []

    # we assume that peaks are sorted already increasing order by x
    xmin, xmax = peaks[0][0], peaks[-1][0]
    
    # we create an occupancy vector to keep track of empty regions 
    size  = xmax - xmin + exclusion
    shift = xmin - exclusion

    # exclusion will be applied for both ends
    # the size must fit into memory, int8 is fairly small though
    # chop large chromosomes into chunks and predict on each
    empty = numpy.ones(size + exclusion, numpy.int8)

    # starting with the largest select from the existing peaks
    for peaky, peakx in work:

        # get the peak index as occupancy vector index
        locind = peakx - shift
        
        # check region
        if empty[locind]:
            
            # store this peak
            selected.append( ( peakx, peaky ) )

           # block the region
            left  = locind - exclusion
            right = locind + exclusion
            empty[left:right] = numpy.zeros (right - left, numpy.int8)
    
    selected.sort()
    return selected

def fixed_width_predictor(x, y, params):   
    """
    Generates peaks from a x,y dataset.

    >>> from genetrack import util
    >>>
    >>> y = [ 0.0, 1.0, 2.5, 1.0, 3.5, 1.0, 0.0, 0.0, 10.5, 2.0, 1.0, 0.0 ]
    >>> x = range(len(y))
    >>>
    >>> params = util.Params(feature_width=1, minimum_peak=0, zoom_value=1)
    >>> fixed_width_predictor(x, y, params=params)
    [(2, 2, '2.5'), (4, 4, '3.5'), (8, 8, '10.5')]
    >>>
    >>> params = util.Params(feature_width=2, minimum_peak=3, zoom_value=1)
    >>> fixed_width_predictor(x, y, params=params)
    [(3, 5, '3.5'), (7, 9, '10.5')]
    """

    width = params.feature_width
    all_peaks = detect_peaks(x=x, y=y )
    sel_peaks = select_peaks(peaks=all_peaks, exclusion=width, threshold=params.minimum_peak)

    #print params
    #print sel_peaks
    # generate the fixed lenght intervals with open 
    h = width/2
    if int(params.zoom_value)> 5000:
        results = [ (m - h, m + h, '' ) for m, v in sel_peaks ]    
    else:
        results = [ (m - h, m + h, '%.1f' % v ) for m, v in sel_peaks ]

    return results

def test(verbose=0):
    """
    Main testrunnner
    """
    import doctest
    doctest.testmod( verbose=verbose )

def test_plot():
    "Visualize results via matplotlib"
    from pylab import plot, show

    x = [ 1, 101, 102, 103,  500, 503,  ]
    y = [ 1,   1,   2,   3,    5,    1,  ]

    nx, ny  = gaussian_smoothing(x, y, sigma=30)

    plot(nx, ny, 'bo-')
    show()

if __name__ == '__main__':
    test(verbose=0)
   
    peaks = [ (0, 20), (100, 19), (500, 4), (10**6, 2) ]
    print select_peaks( peaks, exclusion=200)

    #test_plot()
    


