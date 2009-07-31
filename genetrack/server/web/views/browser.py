"""
Track related views
"""
import os, mimetypes, string
from django.conf import settings
from django import forms
from genetrack.visual import builder
from genetrack import logger, conf, hdflib, util, fitlib
from genetrack.server.web import html, status, webutil
from genetrack.server.web import models, authorize
from genetrack.server.web.views import formspec
from genetrack.server.web import login_required, private_login_required
from genetrack.visual import parsing, builder

FORM_DEFAULTS = formspec.ALL_DEFAULTS

def dataview_populate(json, index, params):
    """
    Populates the data view with the results.
    This operates on a single data and populates the data in the json from it.
    """

    results = index.query(start=params.start, end=params.end, label=params.chrom)
    
    data = map(list, (results.idx,results.val))
    xscale = (params.start, params.end)
    for row in json:

        if row['style'].startswith('FIT'):
            # fit the data
            data = fitlib.gaussian_smoothing(data[0], data[1], sigma=params.sigma, epsilon=0.01 )
            data = map(list, data)
            row['data'] = data
        else:
            row['data'] = data
        row['xscale'] = xscale
        row['w'] = params.image_width

    return json

def dataview_trackdef(params):
    """
    Returns the track specification based on parameters
    """
    
    lines = [
        # the default line that is always here
        "color=BLACK; style=BAR; data=1; h=400; ylabel=Read count; legend=Reads; bpad=1"
    ]
    
    if params.sigma>0:
        # fitting is on
        lines.append(
            "color=PURPLE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; ylabel=Cumulative sum; legend=Smoothed; color2=PURPLE 50%; threshold=2.5"
        )

    return "\n".join(lines)


def dataview_multiplot(index, params, debug=False):
    "Generates a  dataview based on data id"

    # will keep track of performance
    timer = util.Timer()
    
    # create the track definition
    text = dataview_trackdef(params)

    # parse the track definition into a json
    json = parsing.parse(text)
    
    # populates the json datafields with actual data
    json = dataview_populate(json=json, index=index, params=params)

    # timing the query lenght
    query_elapsed = timer.stop()
    
    # build the actual multiplot
    multi = builder.get_multiplot(json, debug=debug)

    # timing the query lenght
    draw_elapsed = timer.stop()

    print draw_elapsed
    
    return multi

def get_incoming(request, defaults):
    """
    Alters the incoming parameters based on user actions
    """
    # shortcut to user messages
    msg = request.user.message_set.create

    # incoming paramters
    incoming = dict( request.POST.items() )
    
    # return with defaults if nothing was sent
    if not incoming:
        return defaults

    # attempt to extract the feature from a number or a search
    try:
        center = int( incoming.get('feature', 10000) )
    except ValueError:
        # non numeric feature, search for feature location
        msg( message='Feature search not available')
        center = 10000

    try:
        # current zoom value
        zoom_value = int( incoming.get('zoom_value', 1000) )
    except ValueError:
        msg( message='Invalid zoom value')
        zoom_value = 1000

    # alter parameters if navigation buttons were pressed
    if 'zoom_in' in incoming:
        zoom_value = formspec.zoom_change(zoom_value, -1) 
    elif 'zoom_out' in incoming:
        zoom_value = formspec.zoom_change(zoom_value, +1)
    elif 'move_left' in incoming:
        center -= zoom_value/2
    elif 'move_right' in incoming:
        center += zoom_value/2

    # map it back to string to allow for form validation later
    incoming['zoom_value'] = str(zoom_value)
    incoming['feature'] = str(center)

    # smoothing will be turned on if peak prediction is on
    incoming['use_smoothing'] = incoming.get('use_smoothing') or incoming.get('use_predictor')

    # turn off smoothing for large zoom levels 
    # may be slow to do it live, and user may not be able to see anything useful anyhow
    if zoom_value > 25000 and incoming['use_smoothing']:
        incoming['use_smoothing'] = incoming['use_predictor'] = False
        msg( message='Range too large for live predictions (maximum 25,000)' )

    
    return incoming

def get_params(request, forms):
    "Extracts search parameters from the forms"
    # shortcut to user messages
    msg = request.user.message_set.create

    params = html.Params()
    params.update( formspec.ALL_DEFAULTS )
    for form in (forms.search, forms.fitting, forms.peaks):
        if form.is_valid():
            params.update( form.cleaned_data )
        else:
            msg( message=str(form.errors) ) 
    
    # now add the start and end regions
    center = int(params.feature)
    zoom_value = int( params.zoom_value )
    
    # the viewport may be different from the size of the image
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

    # the zoom arrows will appear on this line
    # todo generate automatically
    params.arrow_line = 170 if params.strand=='WC' else 302

    return params

@login_required
def data_view(request, did):
    "Renders a simple view page"
    global FORM_DEFAULTS

    user = request.user
    # verify access rights
    data = authorize.get_data(user=user, did=did)

    # incoming parameters cast into a dictionary
    incoming = get_incoming(request, FORM_DEFAULTS)

    # get the data representation
    index = data.index()

    # create the necessary forms
    forms  = html.Params()
    forms.search  = formspec.make_form(index.labels)(incoming)
    forms.navbar  = formspec.NavbarForm()
    forms.fitting = formspec.FitForm(  incoming )
    forms.peaks   = formspec.PeakForm( incoming )

    # extract the search parameters
    params = get_params(request=request, forms=forms)

    # creates the multiplot
    multi = dataview_multiplot(index=index, params=params, debug=False)
    
    # trigger the occasional cache cleaning
    webutil.cache_clean(age=1, chance=10)

    # creates a file representation and a name
    imgname, imgpath = webutil.cache_file(ext='png')

    # saves the multiplot
    multi.save(imgpath)
    params.imgname = imgname

    return html.template( request=request, name='data-browse.html', forms=forms, data=data, params=params)

if __name__ == '__main__':
    from genetrack.server.web import models
    data = models.Data.objects.get(id=1)
    index = data.index()

    params = html.Params(start=100, end=1500, chrom='chr1', sigma=20, image_width=800)
    json = dataview_multiplot(index=index, params=params, debug=True)
