# Create your views here.
import sys
from django.conf import settings
from genetrack import logger
from server.web import html, models
from django.contrib import auth
from django import forms
from django.core.exceptions import *

class LoginForm(forms.Form):
    "Used for logging in"
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def check_profile(user):
    "Creates a user profile if it did not exists"
    try:
        user.get_profile()
    except ObjectDoesNotExist, exc:
        logger.debug( 'Creating a user profile for %s' % user.username )
        profile = models.UserProfile.objects.create( user=user )


def index(request):
    "Login request"
    auth.logout(request)
    return html.redirect("/")

def logout(request):
    "Logout request"
    auth.logout(request)
    return html.redirect("/")
