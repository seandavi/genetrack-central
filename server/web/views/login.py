# Create your views here.
import sys
from django.conf import settings
from genetrack import logger
from server.web import html, models
from django.contrib import auth
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import *

class LoginForm(forms.Form):
    "Used for logging in"
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def logout(request):
    "Logout request"
    auth.logout(request)
    return html.redirect("/")

def index(request):
    "Login request"
    
    # users are not logged in so we can't use the Django messaging system
    error_message = ''

    #
    # a logged in superuser may 'impersonate' other users 
    # this behavior may be disabled in the settings
    #
    if request.GET and settings.SUPERUSER_PASSWORD_OVERRIDE:
        uid = request.GET.get('uid', "").strip()
        if request.user.is_superuser and uid:
            user = User.objects.get(id=uid)
            backend = auth.get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            auth.login(request, user)            
            return html.redirect("/project/list/")  
        else:
            raise Exception('invalid login')
    #
    # normal login
    #
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '').strip()
            password = form.cleaned_data['password']
            userlist = User.objects.filter(email=email).all()
            if userlist:
                first = userlist[0]
                user = auth.authenticate(username=first.username, password=password)
                if user and user.is_active:
                    auth.login(request, user)                
                    return html.redirect("/project/list/")
                else:
                    error_message = 'Invalid user password!'
            else:
                 error_message = 'Invalid user email'
        else:
            # invalid form submission
            error_message = "Please specify an email and a password!"
    else:
        form = LoginForm()

    return html.template( request, name='login.html', form=form, error_message=error_message)