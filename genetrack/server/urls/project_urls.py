
from django.conf.urls.defaults import *

urlpatterns = patterns('genetrack.server.web.views',
    #
    # project related views
    #    
    (r'^list/', 'project.listall'),
    (r'^edit/(?P<pid>(.*))/$', 'project.edit'),
    (r'^delete/(?P<pid>(.*))/$', 'project.delete'),
    (r'^share/(?P<pid>(.*))/$', 'project.share'),
    (r'^view/(?P<pid>(.*))/$', 'project.view'),
)
