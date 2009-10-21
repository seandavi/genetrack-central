"""
Galaxy specific views
"""
import sys, binascii, hmac, hashlib

from django.conf import settings
from genetrack import logger
from genetrack.server.web import html, authorize
from django.template import RequestContext



def index(request):
    "Main index page"
     # form submission
    params = html.Params( )

    
    return html.template( request, name='galaxy.html', params=params )

def browse(request):
    pass