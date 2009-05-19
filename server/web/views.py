# Create your views here.
from django.conf import settings
from server.web import html

def index(request):
    "Main index page"
    params = html.Params()
    return html.template( request, name='index.html', params=params )

def about(request):
    "About page"
    params = html.Params()
    return html.template( request, name='about.html', params=params )

