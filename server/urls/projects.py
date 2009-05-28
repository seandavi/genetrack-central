
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #
    # project related views
    #    
    (r'^list/', 'liondb.server.views.project.listall'),
    (r'^edit/(?P<pid>(.*))/$', 'liondb.server.views.project.edit'),
    (r'^delete/(?P<pid>(.*))/$', 'liondb.server.views.project.delete'),
    (r'^share/(?P<pid>(.*))/$', 'liondb.server.views.project.share'),
    (r'^view/(?P<pid>(.*))/$', 'liondb.server.views.project.view'),
)
