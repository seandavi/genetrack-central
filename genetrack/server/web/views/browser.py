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
from genetrack.server.web import login_required, private_login_required
from genetrack.visual import parsing, builder

def dataview_populate(json, results, params):
    """
    Populates the data view with the results
    """
    data = map(list, (results.idx,results.val))
    xscale = (params.start, params.end)
    for row in json:
        if row['style'].startswith('FIT'):
            data = fitlib.gaussian_smoothing(data[0], data[1], sigma=params.sigma, epsilon=0.01 )
            data = map(list, data)
            row['data'] = data
        else:
            row['data'] = data
        row['xscale'] = xscale

    return json

def dataview_json(data, params, debug=False):
    "Generates a  dataview based on data id"

    # the file that contains the data, index should already exist
    fname = data.content.path

    # will keep track of performance
    timer = util.Timer()
    
    # no index building allowed here
    index  = hdflib.PositionalData(fname=fname, nobuild=True)
    results = index.query(start=params.start, end=params.end, label=params.chrom)
    
    # this creates the json
    text = """
    color=BLACK; style=BAR; data=1; h=300; ylabel=Read count; legend=Reads; bpad=1
    """

    if params.sigma:
        text += """
        color=PURPLE; style=FIT_LINE; lw=2; data=1; target=last; newaxis=0; ylabel=Cumulative sum; legend=Smoothed; color2=PURPLE 50%; threshold=2.5
        """ 

    json = parsing.parse(text)
    
    # populates the dataview with actual data
    json = dataview_populate(json=json, results=results, params=params)

    # timing the query lenght
    query_elapsed = timer.stop()

    multi = builder.get_multiplot(json, debug=debug)

    # timing the query lenght
    draw_elapsed = timer.stop()

    print draw_elapsed

    return multi

@login_required
def data_view(request, did):
    "Renders a simple view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params(start=100, end=200, chrom='chr1')
    return html.template( request=request, name='data-browse.html', data=data, param=param)


if __name__ == '__main__':
    from genetrack.server.web import models
    data = models.Data.objects.get(id=3)
    params = html.Params(start=100, end=1500, chrom='chr1', sigma=20)

    json = dataview_json(data=data, params=params, debug=True)
