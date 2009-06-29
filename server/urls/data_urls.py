from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    #
    # data related views
    #    
    (r'^edit/(?P<did>(.*))/$', 'web.views.data.edit'),
    (r'^action/(?P<pid>(\d+))/$', 'web.views.data.action'),
    (r'^view/(?P<did>(\d+))/$', 'web.views.data.view'),
    (r'^upload/process/(?P<pid>(\d+))/$', 'web.views.data.upload_processor'),
    (r'^upload/start/(?P<pid>(\d+))/$', 'web.views.data.upload_start'),

    # non applet version 
    (r'^upload/simple/(?P<pid>(\d+))/$', 'web.views.data.upload_simple'),

    (r'^download/(?P<did>(\d+))/$', 'web.views.data.download'),
    (r'^result/get/(?P<rid>(\d+))/(?P<target>(\w+))/$', 'web.views.data.result_get'),
    (r'^result/upload/(?P<did>(\d+))/$', 'web.views.data.result_upload'),
    (r'^result/delete/(?P<rid>(\d+))/$', 'web.views.data.result_delete'),

    # the browser
    #(r'^view/(?P<did>(\d+))/$', 'liondb.genetrack.browser.view'),
)
