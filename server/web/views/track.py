"""
Track related views
"""
import os, mimetypes, string
from django.conf import settings
from django import forms
from genetrack import logger, conf
from server.web import html, status, webutil
from server.web import models, authorize
from server.web import login_required, private_login_required
from genetrack.visual import trackspec, builder

def fixup_paths(json):
    "Adds path information for known data attribute fields"
    known_attrs = ('data', )
    for row in json:
        attrs = [ attr for attr in known_attrs if attr in row]
        for attr in attrs:
            key = '%s_path' % attr
            row[key]=models.Data.objects.get(id=row[attr]).content.path
    return json

class AttributeField(forms.Field):
    "Custom field for attribute validation"
    def clean(self, value):
        "Adding a custom validation"
        
        # some data must be present
        if not value:
            raise forms.ValidationError('Field may not be empty.')
        
        # check format then fixup the paths
        try:
            # parse it into a json
            value = trackspec.parse(value)
            # add paths to data
            value = fixup_paths(value)
        except Exception, exc:
            raise forms.ValidationError(exc)
            
        # Always return the cleaned data.
        return value
        
class TrackForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='Track name', widget=forms.TextInput(attrs=dict(size=80)))
    text = AttributeField( initial='', widget=forms.Textarea(attrs=dict(id='json')))
    
@private_login_required
def delete_track(request, tid):
    "Deletes a track"
    project = authorize.delete_track(user=request.user, tid=tid)
    return html.redirect( "/project/view/%s/" % project.id )

def create_track(request, pid, tid):
    "Page to create a new track"
    form = TrackForm()
    project = authorize.get_project(user=request.user, pid=pid, write=False)
    data = project.track_data()
    param = html.Params(tid=tid, pid=pid, title='Create Track', data=data)
    return html.template( request=request, name='track-edit.html', param=param, form=form )

@private_login_required
def edit_track(request, pid, tid):
    "Updates or creates a project"
    user = request.user
    
    # detect track creation or editing
    create = (tid == '0')
    submit = ('submit' in request.POST) or ('preview' in request.POST)
    title = 'Create track' if create else 'Edit track'
    preview = ('preview' in request.POST) # preview request
    
    # form represents the incoming parameters
    form = TrackForm( request.POST )   
    valid = form.is_valid()
    
    # a create request with no form submission
    if create and not submit:
        return create_track(request=request, pid=pid, tid=tid)
    
    # get project related information
    project = authorize.get_project(user=user, pid=pid, write=False)
    data  = project.track_data()
    param = html.Params(tid=tid, pid=pid, title=title, data=data, imgname=None)
    
    # valid incoming form data data
    if submit:
        if valid:
            # valid submit data
            get  = form.cleaned_data.get
            name = get('name')
            text = request.POST['text']
            json = get('text')
            
            if preview:
                imgname, imgpath = webutil.cache_file(name=user.id, ext='png')
                multi = builder.preview(json)
                multi.save(imgpath)
                param.imgname = imgname
                return html.template( request=request, name='track-edit.html', param=param, form=form )
            elif create:
                track = authorize.create_track(user=user, pid=pid, name=name, json=json, text=text )
            else:
                track = authorize.update_track(user=user, name=name, tid=tid, json=json, text=text)
            return html.redirect("/project/view/%s/" % track.project.id)
        else:
            #invalid submit data, the form already contains the error messages
            return html.template( request=request, name='track-edit.html', param=param, form=form )
            
    
    # this is an edit track reuest, populate form accordingly
    track = authorize.get_track(user=user, tid=tid)
    form = TrackForm(dict(name=track.name, text=track.text))
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