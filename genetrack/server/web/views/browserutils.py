"""
Browser related utility functions
"""

from genetrack.server.web.views import formspec

# the limit over which smoothing will be disabled
SMOOTH_LIMIT = 50000

def extract_parameters(forms):
    "Extracts search parameters from the forms"

    params = html.Params()
    params.update( formspec.ALL_DEFAULTS )
    for form in (forms.search, forms.fitting, forms.peaks):
        if form.is_valid():
            params.update( form.cleaned_data )
    
    # now add the start and end regions
    center = int(params.feature)
    zoom_value = int( params.zoom_value )
    
    # the viewport is different from the size of the image
    # the visible region has to cover the zoom level
    zoom_factor = float(params.image_width)/params.viewport_width
    zoom_value *= zoom_factor

    # start and end based on zoom levels
    params.start = center - zoom_value/2
    params.end   = center + zoom_value/2

    # needs to be scaled later
    fullrange = (params.end - params.start)

    # what range does a pixel correspond to
    params.pixelscale  =  float(fullrange) / params.image_width

    # this padding is empirical, 
    # todo generate automatically
    params.actual_size = params.image_width + 120

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