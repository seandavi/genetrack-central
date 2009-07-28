"""
Password url mapper
"""
from django.conf.urls.defaults import patterns

import django.contrib.auth.views


urlpatterns = patterns('',
    #
    # default password management interface for django
    #     
    (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', { 'template_name':'password_reset_done.html' } ), 
    (r'^password_reset/$', 'django.contrib.auth.views.password_reset',  { 'template_name':'password_reset_form.html', 'email_template_name':'password_reset_email.html' } ),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', { 'template_name':'password_reset_confirm.html' } ), 
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',  { 'template_name':'password_reset_complete.html' } ),     
)
