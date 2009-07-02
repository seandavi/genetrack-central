from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    #
    # track related views
    #    
    (r'^edit/(?P<tid>(.*))/$', 'web.views.track.edit_track'),
    (r'^delete/(?P<tid>(\d+))/$', 'web.views.track.delete_track'),
    (r'^view/(?P<uid>(\d+))/$', 'web.views.track.view_track'),
)
