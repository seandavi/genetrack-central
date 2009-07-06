"""
Track related views
"""
import os, mimetypes
from django.conf import settings
from django import forms
from genetrack import logger, conf
from server.web import html, status
from server.web import models, authorize
from server.web import login_required, private_login_required

class TrackForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='Track name', widget=forms.TextInput(attrs=dict(size=80)))

@private_login_required
def delete_track(request, tid):
    "Deletes a track"
    project = authorize.delete_track(user=request.user, tid=tid)
    return html.redirect( "/project/view/%s/" % project.id )

@private_login_required
def edit_track(request, pid, tid):
    "Updates or creates a project"
    user = request.user
    
    form = TrackForm( request.POST )   
    project = authorize.get_project(user=user, pid=pid, write=False)
    
    if form.is_valid():
        # incoming data
        get = form.cleaned_data.get
        
        json = {}
        if tid == '0':
            track = authorize.create_track(user=user, pid=pid, name=get('name'), json=json )
            message="New track created"
        else:
            track = authorize.update_track(user=user, name=get('name'), tid=tid, json=json)
            message="Track updated"

        user.message_set.create(message=message)
        
        return html.redirect("/project/view/%s/" % track.project.id)

    else:
        # no form data sent
        if tid == '0':
            title = 'Create New Track'
            form = TrackForm( )            
        else:
            title = 'Edit Track'
            track = authorize.get_track(user=user, tid=tid)
            form = TrackForm(dict(name=track.name) )    
        
        data  = project.track_data()
        print data
        param = html.Params(tid=tid, pid=pid, title=title, data=data)
        return html.template( request=request, name='track-edit.html', param=param, form=form )
 
@login_required
def view_track(request, did):
    "Renders the data view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params(file_list=data.file_list(), image_list= data.image_list())
    return html.template( request=request, name='data-view.html', data=data, param=param)

if __name__ == '__main__':
    pass    