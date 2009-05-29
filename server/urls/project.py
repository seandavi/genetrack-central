
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #
    # project related views
    #    
    (r'^list/', 'web.views.project.listall'),
    (r'^edit/(?P<pid>(.*))/$', 'web.views.project.edit'),
    (r'^delete/(?P<pid>(.*))/$', 'web.views.project.delete'),
    (r'^share/(?P<pid>(.*))/$', 'we.views.project.share'),
    (r'^view/(?P<pid>(.*))/$', 'web.views.project.view'),
)
