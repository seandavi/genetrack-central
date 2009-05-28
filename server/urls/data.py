
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #
    # data related views
    #    
    (r'^edit/(?P<did>(.*))/$', 'liondb.server.views.data.edit'),
    (r'^action/(?P<pid>(\d+))/$', 'liondb.server.views.data.action'),
    (r'^handler/(?P<pid>(\d+))/$', 'liondb.server.views.data.handler'),
    (r'^upload/(?P<pid>(\d+))/$', 'liondb.server.views.data.upload'),
    (r'^download/(?P<did>(\d+))/$', 'liondb.server.views.data.download'),
    (r'^summary/(?P<did>(\d+))/$', 'liondb.server.views.data.summary'),
    
    # the browser
    (r'^view/(?P<did>(\d+))/$', 'liondb.genetrack.browser.view'),
)
