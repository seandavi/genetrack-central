"""
Track related views
"""
import os, mimetypes, string
from django.conf import settings
from django import forms
from genetrack import logger, conf
from genetrack.server.web import html, status, webutil
from genetrack.server.web import models, authorize
from genetrack.server.web import login_required, private_login_required
from genetrack.visual import parsing, builder

@login_required
def data_view(request, did):
    "Renders a simple view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params()
    return html.template( request=request, name='data-browse.html', data=data, param=param)

if __name__ == '__main__':
    pass