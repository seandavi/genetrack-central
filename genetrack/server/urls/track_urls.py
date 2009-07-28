"""
Track url mapper
"""
from django.conf.urls.defaults import patterns

urlpatterns = patterns('genetrack.server.web.views',
    #
    # track related views
    #    
    (r'^edit/(?P<pid>(\d+))/(?P<tid>(.*))/$', 'track.edit_track'),
    (r'^delete/(?P<tid>(\d+))/$', 'track.delete_track'),
    (r'^view/(?P<uid>(\d+))/$', 'track.view_track'),
)
