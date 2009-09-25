"""
Browser related utility functions
"""

from genetrack.server.web import html
from genetrack.server.web.views import formspec
from genetrack import logger, conf, hdflib, util, fitlib

# the limit over which smoothing will be disabled
SMOOTH_LIMIT = 50000

# this padding is currently empirical, todo: generate automatically
IMAGE_PADDING = 120

# default composite plot
DEFAULT_COMPOSITE = """
color=BLACK; style=BAR; data=1; h=400; ylabel=Read count; legend=Reads; bpad=1;
color=PURPLE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; ylabel=Cumulative sum; legend=Smoothed; color2=PURPLE 50%%; threshold=%(minimum_peak)f
color=PURPLE 10%%; style=SEGMENT; data=1; bpad=1; legend=Prediction;
"""
DEFAULT_COMPOSITE = filter(None, DEFAULT_COMPOSITE.splitlines())

DEFAULT_TWO_STRAND = """
color=BLUE; style=BAR; data=1; h=400; ylabel=Read count; legend=Forward reads; bpad=1; h=180; strand=+; 
color=BLUE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; strand=+; 

color=RED; style=BAR; data=1; h=400; ylabel=Read count; legend=Reverse reads; bpad=0; strand=-; h=180; scaling=-1; tpad=-1
color=RED; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0;  legend=Forward; strand=-; scaling=-1

color=BLUE 10%%; style=SEGMENT; data=1; bpad=1; legend=Forward peaks; strand=+;
color=RED 10%%; style=SEGMENT; data=1; bpad=1; legend=Reverse peaks; strand=-;

"""
DEFAULT_TWO_STRAND = filter(None, DEFAULT_TWO_STRAND.splitlines())

def fit(x, y, params):
    "Fits the x and y data"
    fx, fy = fitlib.gaussian_smoothing(x, y, sigma=params.sigma, epsilon=0.01 )
    return list(fx), list(fy)

def peaks(x, y, params):
    "Returns peaks for x and y data"
    data = fitlib.fixed_width_predictor( x=x, y=y, params=params )
    return data

def index_populate(json, index, params):
    """
    Populates a data view from an index

    Operates on a single index and populates the data as specified by the content
    of the json spec.
    """

    # peform the query
    res = index.query(start=params.start, end=params.end, label=params.chrom, aslist=True)
    
    # separete strands
    composite = (params.strand == 'ALL')

    # compute smoothing before plotting
    if params.use_smoothing:
        if composite:
            res.fx, res.fy = fit(x=res.idx, y=res.val, params=params)
        else:
            res.fx1, res.fy1 = fit(x=res.idx, y=res.fwd, params=params)
            res.fx2, res.fy2 = fit(x=res.idx, y=res.rev, params=params)
    
    
    # compute all peak predictions before plotting
    if params.use_predictor:
        assert params.use_smoothing, 'Smoothing has not been turned on!'
        if composite:
            res.peaks = peaks(x=res.fx, y=res.fy, params=params)
        else:
            res.peaks1 = peaks(x=res.fx1, y=res.fy1, params=params)
            res.peaks2 = peaks(x=res.fx2, y=res.fy2, params=params) 
    
    # shortcuts
    isfit  = lambda x: x.startswith('FIT')
    ispred = lambda x: x.startswith('SEGMENT')

    if composite:
        # composite plot
        for row in json:
            style = row['style']
            if isfit(style):
                row['data'] = (res.fx, res.fy)
            elif ispred(style):
                row['data'] = res.peaks
            else:
                row['data'] = (res.idx, res.val)        
            row['xscale'] = params.xscale
            row['w'] = params.image_width
    else:
        # two strand plot
        for row in json:
            style = row['style']
            positive = row.get('strand', '+') == '+'

            print '>>>>>>', positive
            if isfit(style):
                if positive:
                    row['data'] = (res.fx1, res.fy1)
                else:
                    row['data'] = (res.fx2, res.fy2)
            elif ispred(style):
                if positive:
                    row['data'] = res.peaks1
                else:
                    row['data'] = res.peaks2
            else:
                row['data'] = (res.idx, res.val)        
            row['xscale'] = params.xscale
            row['w'] = params.image_width
    
    return json

def default_tracks(params):
    "Generates default tracks based on the parameter values"
    
    # detect which tracks to draw
    if params.strand == 'ALL':
        text = DEFAULT_COMPOSITE
    else:
        text = DEFAULT_TWO_STRAND

    # draws everything as specified in the spec
    if params.use_smoothing and params.use_predictor :
        return "\n".join(text)

    # only smoothing is performed
    if params.use_smoothing:
        # no smoothing no predictions
        return "\n".join(text[:2] + text[3:-1])
    
    # draws just the reads
    return "\n".join(text[::3])

def parse_parameters(forms, defaults):
    """
    Extracts search parameters from the forms and returns them 
    as a populated html.Params() instance that permits attribute access.
    """

    # set up default parameters
    params = html.Params()
    params.update( defaults )

    # loop over all forms and update with cleaned data
    for form in (forms.search, forms.fitting, forms.peaks):
        if form.is_valid():
            params.update( form.cleaned_data )
    
    # the view will be centered on the feature
    center = int(params.feature)
    zoom_value = int( params.zoom_value )
    
    # the viewport is different from the size of the image
    # and the visible region of the chart has be 'zoom level' wide
    zoom_factor = float(params.image_width)/params.viewport_width
    zoom_value *= zoom_factor

    # start and end based on zoom levels
    params.start = center - zoom_value/2
    params.end   = center + zoom_value/2

    # set the scale
    params.xscale = (params.start, params.end)

    # the width of the interval
    fullrange = (params.end - params.start)

    # what interval does a single pixel correspond to
    params.pixelscale  =  float(fullrange) / params.image_width

    # the actual size of the image
    params.actual_size = params.image_width + IMAGE_PADDING

    # negative or zero sigma turns off everything
    if params.sigma < 0:
        params.use_predictor = params.use_smoothing = False

    return params

def modify_incoming(incoming, defaults):
    """
    Modifies the incoming parameters based on user actions.
    
    This needs to be done before binding to form parameters as
    those need to reflect the state after button presses.
    """

    # return with defaults if nothing was sent
    if not incoming:
        return defaults

    # getting the feature cooridnate
    try:
        center = int( incoming.get('feature', 10000) )
    except ValueError:
        # for numeric features a search should 
        # have been triggered before this step
        center = 10000

    #
    # current zoom value
    #
    try:
        zoom_value = int( incoming.get('zoom_value', 1000) )
    except ValueError:
        zoom_value = 1000

    #
    # alter zoom level or panning if the buttons were pressed
    #
    if 'zoom_in' in incoming:
        zoom_value = formspec.zoom_change(zoom_value, -1) 
    elif 'zoom_out' in incoming:
        zoom_value = formspec.zoom_change(zoom_value, +1)
    elif 'move_left' in incoming:
        center -= zoom_value/2
    elif 'move_right' in incoming:
        center += zoom_value/2

    #
    # map values back to string to allow for form validation later
    #
    incoming['zoom_value'] = str(zoom_value)
    incoming['feature'] = str(center)

    #
    # smoothing will be turned on if peak prediction is on
    #
    incoming['use_smoothing'] = incoming.get('use_smoothing') or incoming.get('use_predictor')

    # turn off smoothing and predictions for large view levels 
    # it can be slow to do it live, and the user may not be able 
    # to see anything useful anyhow
    if zoom_value > SMOOTH_LIMIT:
        incoming['use_smoothing'] = incoming['use_predictor'] = False
    
    return incoming