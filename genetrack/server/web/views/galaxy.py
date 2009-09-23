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

    # unpack the request parameters    
    msg, value = request.GET['filename'].split( ":" )
    filename = binascii.unhexlify( value )

    # validate filename
    verify = hmac.new( settings.GALAXY_TOOL_SECRET, filename, hashlib.sha1 ).hexdigest()
    
    if msg != verify:
        raise Exception('Unable to validate key!')

    return html.template( request, name='galaxy.html', params=params )
