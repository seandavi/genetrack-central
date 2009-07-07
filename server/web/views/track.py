"""
Track related views
"""
import os, mimetypes, string
from django.conf import settings
from django import forms
from genetrack import logger, conf
from server.web import html, status
from server.web import models, authorize
from server.web import login_required, private_login_required

class TrackForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='Track name', widget=forms.TextInput(attrs=dict(size=80)))
    text = forms.CharField( initial='', widget=forms.Textarea(attrs=dict(id='json')))

def track_parse(text):
    # clean all lines
    lines = filter(None, map(string.strip, text.splitlines()))
    try:
        json = dict()
        for line in lines:
            pass
        return json
    except Exception, exc:
        return None
    

@private_login_required
def delete_track(request, tid):
    "Deletes a track"
    project = authorize.delete_track(user=request.user, tid=tid)
    return html.redirect( "/project/view/%s/" % project.id )

@private_login_required
def edit_track(request, pid, tid):
    "Updates or creates a project"
    user = request.user
    
    #
    form = TrackForm( request.POST )   
    project = authorize.get_project(user=user, pid=pid, write=False)
    
    # track creation or editing
    create = tid == '0'
    submit = 'submit' in request.POST
    
    # setting the title
    title  = 'Create New Track' if create else 'Edit Track'

    # valid incoming data
    if submit and form.is_valid():
        # valid incoming data
        get  = form.cleaned_data.get
        name = get('name')
        text = get('text')
        json = {}
        if create:
            track = authorize.create_track(user=user, pid=pid, name=name, json=json, text=text )
        else:
            track = authorize.update_track(user=user, name=name, tid=tid, json=json, text=text)
        return html.redirect("/project/view/%s/" % track.project.id)
    
    print '.............', submit
    # no data submission
    if not submit:
        if create:
            form = TrackForm() 
        else:
            track = authorize.get_track(user=user, tid=tid)
            form = TrackForm(dict(name=track.name, text=track.text))
    
    data  = project.track_data()
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