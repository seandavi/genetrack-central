"""
Main url configuration
"""
from django.conf.urls.defaults import *
from django.conf import settings
from genetrack.server.web.views import browser

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

if not settings.DEBUG:
    handler500 = 'genetrack.server.web.views.error500'

urlpatterns = patterns('',

    # index page
    (r'^$', 'genetrack.server.web.views.main.index'),
    
    # login handlers
    (r'^login/', 'genetrack.server.web.views.login.index'),
    (r'^logout/', 'genetrack.server.web.views.login.logout'),

    # placeholder for pages that are not yet completed
    (r'^todo/', 'genetrack.server.web.views.main.todo'),

    # placeholder for pages that are not yet completed
    (r'^galaxy', 'genetrack.server.web.views.browser.galaxy'),

    # project related urls
    (r'^project/',  include('genetrack.server.urls.project_urls')),

    # data related urls
    (r'^data/',  include('genetrack.server.urls.data_urls')),

    # track related urls
    (r'^track/',  include('genetrack.server.urls.track_urls')),

    # password reset related urls
    (r'^password/',  include('genetrack.server.urls.password_urls')),
    

    # (r'^server/', include('server.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

# static content to be served for test server only
# disabled for now
if 1 or settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DIR }),
    )
