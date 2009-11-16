"""
Track related views
"""
import os, mimetypes, string, urllib
import sys, binascii, hmac, hashlib
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

def dataview_multiplot(index, params, debug=False):
    "Generates a  dataview based on data id"

    # will keep track of performance
    timer = util.Timer()
    
    # create the track definition
    text = browserutils.default_tracks(params)
    text = text % params

    # parse the track definition into a json
    json = parsing.parse(text)
    
    # populates the json datafields with actual data
    json = browserutils.index_populate(json=json, index=index, params=params)

    # timing the query lenght
    query_elapsed = timer.stop()
    
    # build the actual multiplot
    multi = builder.get_multiplot(json, debug=debug, w=params.image_width)

    # timing the query lenght
    draw_elapsed = timer.stop()
    
    return multi

@login_required
def data_view(request, did):
    "Renders a simple data view page"

    # get the user information
    user = request.user
    
    # verify access rights
    data = authorize.get_data(user=user, did=did)

    # get the data index 
    index = data.index()
    url = "/data/browser/%s/" % did
    return browser(request=request, index=index, url=url)

def validate_filename(request):
    "Validates a filename"
    encoded  = request.GET['filename']
    hashkey  = request.GET['hashkey']
    dataid   = request.GET['id']
    galaxy_url = request.GET['GALAXY_URL']
    filename = binascii.unhexlify( encoded )

    # validate filename
    hashcheck = hmac.new( settings.GALAXY_TOOL_SECRET, filename, hashlib.sha1 ).hexdigest()
    
    if hashkey != hashcheck:
        raise Exception('Unable to validate key!')

    return filename, encoded, hashkey, dataid, galaxy_url

def galaxy(request):
    """
    Returns a data view based on a galaxy forward
    """

    # validates a filename
    filename, encoded, hashkey, dataid, galaxy_url = validate_filename(request)
   
    # access the data on the filesystem
    index = hdflib.PositionalData(filename, nobuild=True)
    #url = urlib.urlencode()
    url = "/galaxy/?filename=%s&hashkey=%s&id=%s&GALAXY_URL=%s" % (encoded, hashkey, dataid, galaxy_url)
    return browser(request=request, index=index, url=url, dataid=dataid, galaxy_url=galaxy_url)


def browser(request, index, url, galaxy_url, dataid=0):
    ""
    global FORM_DEFAULTS

    # incoming parameters cast into a dictionary
    incoming = dict( request.POST.items() )

    # alters the incoming parameters based on user interaction
    incoming = browserutils.modify_incoming(incoming, FORM_DEFAULTS)

    # create the necessary forms
    forms  = html.Params()
    forms.search  = formspec.make_form(index.labels)(incoming)
    forms.navbar  = formspec.NavbarForm()
    forms.fitting = formspec.FitForm(  incoming )
    forms.peaks   = formspec.PeakForm( incoming )

    # extract the search parameters
    params = browserutils.parse_parameters(forms=forms, defaults=formspec.ALL_DEFAULTS)

    # run the tool or return an image
    if 'runtool' in incoming:
        # need to run the tool
        # form the url with dictionary substitution
        
        # TODO make parameters names consistent across Galaxy, GeneTrack and script!
        strand = 'all' if params.strand=='ALL' else 'two'
        mode = 'nolap' if params.smoothing_func =='GK' else 'all'

        urlparams = dict(
            strand = strand,
            exclusion=params.feature_width,
            level=int(params.minimum_peak),
            mode=mode,
            sigma=int(params.sigma),
            input=dataid,
            method='gauss',
            runtool_btn="Execute"
        )

        url = "%s/%s&%s" % (galaxy_url, settings.GALAXY_TOOL_URL, urllib.urlencode( urlparams ))

        return html.redirect(url)
       
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

    return html.template( request=request, name='data-browse.html', forms=forms, params=params, url=url)

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
