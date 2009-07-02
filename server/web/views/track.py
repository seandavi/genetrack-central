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
    name = forms.CharField( initial='Data name', widget=forms.TextInput(attrs=dict(size=80)))
    info = forms.CharField( initial='Data info', widget=forms.Textarea(attrs={'cols':60, 'rows':10, 'class':'text'}))

@private_login_required
def delete_track(request, tid):
    "Deletes a track"
    project = authorize.delete_track(user=request.user, tid=tid)
    return html.redirect( "/project/view/%s/" % project.id )

@private_login_required
def edit_track(request, did):
    "Updates or creates a track"
    user = request.user
    
    data = authorize.get_data(user=user, did=did)
    project = authorize.get_project(user=user, pid=data.project.id, write=False)
    editable = (data.owner == user) or (project.is_manager) 

    # raise error on not editable data
    if not editable:
        raise authorize.AccessError('Data not editable by this role')

    # no submission
    if 'submit' not in request.POST:
        form = DataForm( dict(name=data.name, info=data.info) )        
        return html.template( request=request, name='data-edit.html', data=data, form=form )
    
    # form submission
    form = DataForm( request.POST )  
    if form.is_valid():
        get  = form.cleaned_data.get      
        data.name = get('name')
        data.info = get('info')
        data.save()
        return html.redirect("/data/view/%s/" % data.id)
    else:    
        return html.template( request=request, name='data-edit.html', did=did, form=form )

@login_required
def view_track(request, did):
    "Renders the data view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params(file_list=data.file_list(), image_list= data.image_list())
    return html.template( request=request, name='data-view.html', data=data, param=param)

if __name__ == '__main__':
    pass    