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
from genetrack.server.web.views import formspec, browserutils
from genetrack.server.web import login_required, private_login_required
from genetrack.visual import parsing, builder

FORM_DEFAULTS = formspec.ALL_DEFAULTS

def dataview_populate(json, index, params):
    """
    Populates a data view.
    Operates on a single data and populates the data in the json from it.
    """

    results = index.query(start=params.start, end=params.end, label=params.chrom)
    
    fitdata = []
    data = map(list, (results.idx,results.val))
    xscale = (params.start, params.end)
    
    for row in json:
        style = row['style']
        if style.startswith('FIT'):
            # fit the data
            fitdata = fitlib.gaussian_smoothing(data[0], data[1], sigma=params.sigma, epsilon=0.01 )
            fitdata = map(list, fitdata)
            row['data'] = fitdata
        elif  style.startswith('SEGMENT'):
            assert fitdata, 'smoothing must be applied first'
            peakdata = fitlib.fixed_width_predictor( x=fitdata[0], y=fitdata[1], params=params )
            row['data'] = peakdata
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
    
    if params.use_smoothing and params.sigma > 0:
        # fitting is on
        lines.append(
            "color=PURPLE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; ylabel=Cumulative sum; legend=Smoothed; color2=PURPLE 50%%; threshold=%f" % params.minimum_peak
        )

    if params.use_predictor and params.sigma > 0:
        # fitting is on
        lines.append(
            "color=PURPLE 10%; style=SEGMENT; data=1; bpad=1; legend=Prediction;"
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
    multi = builder.get_multiplot(json, debug=debug, w=params.image_width)

    # timing the query lenght
    draw_elapsed = timer.stop()

    print draw_elapsed
    
    return multi

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

#@login_required
def data_view(request, did):
    "Renders a simple view page"
    global FORM_DEFAULTS

    # get the user information
    user = request.user
    
    # verify access rights
    data = authorize.get_data(user=user, did=did)

    # incoming parameters cast into a dictionary
    incoming = dict( request.POST.items() )

    # alters the incoming parameters based on user interaction
    incoming = browserutils.modify_incoming(incoming, FORM_DEFAULTS)

    # get the data representation
    index = data.index()

    # create the necessary forms
    forms  = html.Params()
    forms.search  = formspec.make_form(index.labels)(incoming)
    forms.navbar  = formspec.NavbarForm()
    forms.fitting = formspec.FitForm(  incoming )
    forms.peaks   = formspec.PeakForm( incoming )

    # extract the search parameters
    params = extract_parameters(forms=forms)

    # creates the multiplot
    multi = dataview_multiplot(index=index, params=params, debug=False)
    params.image_height = multi.h
    
    # close the data
    index.close()

    # trigger the occasional cache cleaning
    webutil.cache_clean(age=1, chance=10)

    # creates a file representation and a name
    image_name, image_path = webutil.cache_file(ext='png')

    # saves the multiplot
    multi.save(image_path)
    params.image_name = image_name

    return html.template( request=request, name='data-browse.html', forms=forms, data=data, params=params)

if __name__ == '__main__':
    from genetrack.server.web import models
    data = models.Data.objects.get(id=1)
    index = data.index()

    params = html.Params(
        start=100, end=1500, chrom='chr1',
        )
    params.update(FORM_DEFAULTS)
    params.image_width=800
    json = dataview_multiplot(index=index, params=params, debug=True)
