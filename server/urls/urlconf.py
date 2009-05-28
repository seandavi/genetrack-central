from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

if not settings.DEBUG:
    handler500 = 'web.views.error500'

urlpatterns = patterns('',

    # index page
    (r'^$', 'web.views.index'),
    
    # login handlers
    (r'^login/', 'web.login.index'),
    (r'^logout/', 'web.login.logout'),

    #(r'^about/', 'web.views.about'),

    # password handling
    #(r'^password/',  include('liondb.urlconf.passwords')),

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
