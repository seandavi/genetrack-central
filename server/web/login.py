# Create your views here.
import sys
from django.conf import settings
from genetrack import logger
from server.web import html
from django.contrib import auth

def index(request):
    "Login request"
    auth.logout(request)
    return html.redirect("/")

def logout(request):
    "Logout request"
    auth.logout(request)
    return html.redirect("/")
