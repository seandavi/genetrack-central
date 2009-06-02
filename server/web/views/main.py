# Create your views here.
import sys
from django.conf import settings
from genetrack import logger
from server.web import html, authorize
from django.template import RequestContext

if not settings.DEBUG:
    logger.warn('debug mode is on')

def index(request):
    "Main index page"
    params = html.Params()
    params.project_count = authorize.project_count(request.user)
    return html.template( request, name='index.html', params=params )

def todo(request):
    "Todo page"
    params = html.Params()
    return html.template( request, name='todo.html', params=params )

def error500(request):
    "Server error page when debug flag is False"
    context = RequestContext(request)
    exc_type, exc_value, tb = sys.exc_info()
    logger.error(exc_value)
    return html.template( request, name='500.html', debug=exc_value )
