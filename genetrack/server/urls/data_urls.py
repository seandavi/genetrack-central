from django.conf.urls.defaults import patterns

from genetrack.server.web.views import data

urlpatterns = patterns('',
    #
    # data related views
    #    
    (r'^edit/(?P<did>(.*))/$', data.edit),
    (r'^action/(?P<pid>(\d+))/$', data.action),
    (r'^view/(?P<did>(\d+))/$', data.view),
    (r'^upload/process/(?P<pid>(\d+))/$', data.upload_processor),
    (r'^upload/start/(?P<pid>(\d+))/$', data.upload_start),

    # non applet version 
    (r'^upload/simple/(?P<pid>(\d+))/$', data.upload_simple),

    (r'^download/(?P<did>(\d+))/$', data.download),
    (r'^result/get/(?P<rid>(\d+))/(?P<target>(\w+))/$', data.result_get),
    (r'^result/upload/(?P<did>(\d+))/$', data.result_upload),
    (r'^result/delete/(?P<rid>(\d+))/$', data.result_delete),

    # the browser
    #(r'^view/(?P<did>(\d+))/$', 'liondb.genetrack.browser.view'),
)
