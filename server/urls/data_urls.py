from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    #
    # data related views
    #    
    #(r'^edit/(?P<did>(.*))/$', 'liondb.server.views.data.edit'),
    #(r'^action/(?P<pid>(\d+))/$', 'liondb.server.views.data.action'),
    (r'^upload/process/(?P<pid>(\d+))/$', 'web.views.data.upload_processor'),
    (r'^upload/start/(?P<pid>(\d+))/$', 'web.views.data.upload_start'),
    #(r'^download/(?P<did>(\d+))/$', 'liondb.server.views.data.download'),
    #(r'^summary/(?P<did>(\d+))/$', 'liondb.server.views.data.summary'),
    
    # the browser
    #(r'^view/(?P<did>(\d+))/$', 'liondb.genetrack.browser.view'),
)
