# Create your views here.
import sys
from django.conf import settings
from genetrack import logger
from server.web import html
from django.template import RequestContext

if not settings.DEBUG:
    logger.warn('debug mode is on')

def index(request):
    "Main index page"

    # check the lenght of secret key in non debug modes
    if not settings.DEBUG and len(settings.SECRET_KEY) < 5:
        msg = 'The value of the SECRET_KEY setting is too short. Please make it longer!'
        raise Exception(msg)
    
    params = html.Params()
    return html.template( request, name='index.html', params=params )

def about(request):
    "About page"
    params = html.Params()
    return html.template( request, name='about.html', params=params )

def error500(request):
    "Server error page when debug flag is False"
    context = RequestContext(request)
    exc_type, exc_value, tb = sys.exc_info()
    logger.error(exc_value)
    return html.template( request, name='500.html', debug=exc_value )
