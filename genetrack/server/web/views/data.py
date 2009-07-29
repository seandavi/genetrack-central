"""
Data related views
"""
import os, mimetypes
from django.conf import settings
from django import forms
from genetrack import logger, conf
from genetrack.server.web import html, status
from genetrack.server.web import models, authorize
from genetrack.server.web import login_required, private_login_required

class DataForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='Data name', widget=forms.TextInput(attrs=dict(size=80)))
    info = forms.CharField( initial='Data info', widget=forms.Textarea(attrs={'cols':60, 'rows':10, 'class':'text'}))

class ResultForm(forms.Form):
    "For project editing"    
    content = forms.FileField(required=False)
    image = forms.FileField(required=False)

    def clean(self):
        # the form must have either content or image present
        cleaned_data = self.cleaned_data
        content = cleaned_data.get("content")
        image = cleaned_data.get("image")
        if not(content or image):
                raise forms.ValidationError("At least on of the fiels must be present")

        # Always return the full collection of cleaned data.
        return cleaned_data


@private_login_required
def action(request, pid):
    "Data related actions"
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=False)

    action = request.REQUEST.get('action')

    if action == u'delete':
        # delete request
        dids = request.REQUEST.getlist('did')
        authorize.delete_data(user=user, pid=pid, dids=dids)
    else:
        user.message_set.create(message="no valid action was selected")

    return html.redirect( "/project/view/%s/" % pid )


@login_required
def download(request, did):
    "Edits an existing project"
    user = request.user
    try:
        data = models.Data.objects.get(id=did)
        project = authorize.get_project(user=user, pid=data.project.id, write=False)
    except ObjectDoesNotExist, exc:
        raise authorize.AccessError("may not access this data")
    
    return html.download_data(data)

@private_login_required
def edit(request, did):
    "Updates or creates a project"
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
        return html.redirect("/data/details/%s/" % data.id)
    else:    
        return html.template( request=request, name='data-edit.html', did=did, form=form )

def upload_processor(request, pid):
    "Handles the actual data upload"
    user = request.user
    if user.is_authenticated() and user.username!='public':
        if 'upload' in request.POST:
            count = 0
            for i in range(50): # take at most 50 files
                key = 'File%s' % i
                if key in request.FILES:
                    count += 1
                    stream = request.FILES[key]
                    name = html.chop_dirname( stream.name )
                    logger.debug('%s uploaded file %s' % (user.username, name) )
                    authorize.create_data(user=user, pid=pid, stream=stream, name=name, info='no information')

            user.message_set.create(message="Uploaded %s files" % count)
        if 'simple' in request.POST:
            return html.redirect("/project/view/%s/" % pid)

    # this is needed only because the JUPload applet makes a HEAD request        
    return html.response('SUCCESS\n')

@private_login_required
def upload_start(request, pid):
    "Renders the upload page"
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=False)    
    return html.template( request=request, name='data-upload.html', project=project)

@private_login_required
def upload_simple(request, pid):
    "Renders the upload page"
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=False)    
    return html.template( request=request, name='data-upload-simple.html', project=project)

@login_required
def details(request, did):
    "Renders the data view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params(file_list=data.file_list(), image_list= data.image_list())
    return html.template( request=request, name='data-details.html', data=data, param=param)

@login_required
def result_get(request, rid, target):
    "Retreives a result"
    user = request.user
    result = authorize.get_result(user=user, rid=rid)
    if target == 'content':
        return html.download_stream(filename=result.content.path, name=result.name, asfile=True, mimetype=result.mime)
    elif target == 'image':
        return html.download_stream(filename=result.image.path, name=result.name, mimetype='image/png', asfile=False)
    else:
        raise Exception('unknown target=%s' % target)

@private_login_required
def result_upload(request, did):
    "Uploads a result"
    user = request.user
    
    data = authorize.get_data(user=user, did=did)
    project = authorize.get_project(user=user, pid=data.project.id, write=False)


    # no submission, default page
    if 'submit' not in request.POST:
        form = ResultForm()        
        return html.template( request=request, name='result-upload.html', data=data, form=form )
    
    # actual form submission
    form = ResultForm( request.POST, request.FILES )  
    if form.is_valid():
        get = form.cleaned_data.get   
        authorize.create_result(user=user, data=data, content=get('content'), image=get('image'))        
        return html.redirect("/data/details/%s/" % data.id)
    else:    
        # error messages will be generated
        user.message_set.create(message="Some form fields could NOT be validated.")
        return html.template( request=request, name='result-upload.html', data=data, form=form )
        

@private_login_required
def result_delete(request, rid):
    "Uploads a result"
    user = request.user
    
    result = authorize.get_result(user=user, rid=rid)
    project = authorize.get_project(user=user, pid=result.data.project.id, write=True)
    result.delete()
    user.message_set.create(message="Result %s deleted" % result.name)
    return html.redirect("/data/details/%s/" % result.data.id)

if __name__ == '__main__':
    pass