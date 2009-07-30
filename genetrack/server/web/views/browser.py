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

def dataview_populate(json, data, params):
    """
    Populates the data view with the results.
    This operates on a single data and populates the data in the json from it.
    """

    # the file that contains the data, index should already exist
    fname = data.content.path

    # no index building allowed here
    index  = hdflib.PositionalData(fname=fname, nobuild=True)
    results = index.query(start=params.start, end=params.end, label=params.chrom)
    
    # this provides a namespace for data properties
    dataprop = html.Params(chroms=index.labels)
    
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
        row['w'] = params.w

    return json, dataprop

def dataview_trackdef(params):
    """
    Returns the track specification based on parameters
    """
    
    lines = [
        # the default line that is always here
        "color=BLACK; style=BAR; data=1; h=300; ylabel=Read count; legend=Reads; bpad=1"
    ]
    
    if params.sigma>0:
        # fitting is on
        lines.append(
            "color=PURPLE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; ylabel=Cumulative sum; legend=Smoothed; color2=PURPLE 50%; threshold=2.5"
        )

    return "\n".join(lines)


def dataview_multiplot(data, params, debug=False):
    "Generates a  dataview based on data id"

    # will keep track of performance
    timer = util.Timer()
    
    # create the track definition
    text = dataview_trackdef(params)

    # parse the track definition into a json
    json = parsing.parse(text)
    
    # populates the json datafields with actual data
    json, dataprop = dataview_populate(json=json, data=data, params=params)

    # timing the query lenght
    query_elapsed = timer.stop()
    
    # build the actual multiplot
    multi = builder.get_multiplot(json, debug=debug)

    # timing the query lenght
    draw_elapsed = timer.stop()

    print draw_elapsed
    
    return multi, dataprop

def form_render(request, dataprop):
    
    submit = 'submit' in request.REQUEST
    search = formspec.make_form(dataprop.chroms)( request.REQUEST )

    # decide on submit action
    if submit and search.is_valid():
        # valid submission
        pass

    elif submit and not search.is_valid():
        # not a valid submission
        pass

    elif not submit:
        # initial view
        pass

    return search

@login_required
def data_view(request, did):
    "Renders a simple view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    
   

    params = html.Params(start=100, end=1500, chrom='chr1', sigma=20, w=800)

    # creates the multiplot
    multi, dataprop = dataview_multiplot(data=data, params=params, debug=False)
    
    search = form_render(request=request, dataprop=dataprop)
    
    forms  = html.Params(search=search)

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
    data = models.Data.objects.get(id=3)
    params = html.Params(start=100, end=1500, chrom='chr1', sigma=20, w=800)
    json = dataview_multiplot(data=data, params=params, debug=True)
