"""
Data related views
"""
import os
from django.conf import settings
from django import forms
from genetrack import logger, conf
from server.web import html, status
from server.web import models, authorize
from server.web import login_required, private_login_required

class DataForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='Data name', widget=forms.TextInput(attrs=dict(size=80)))
    info = forms.CharField( initial='Data info', widget=forms.Textarea(attrs={'cols':60, 'rows':10, 'class':'text'}))

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
        return html.redirect("/data/view/%s/" % data.id)
    else:    
        return html.template( request=request, name='data-edit.html', did=did, form=form )
        
def chop_dirname(name):
    "Removes directory from the name."
    # some browsers may send the full pathname
    name = name.replace("\\", "/")
    name = os.path.basename( name )
    return name

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
                    name = chop_dirname( stream.name )
                    logger.info('%s uploaded file %s' % (user.username, name) )
                    authorize.create_data(user=user, pid=pid, stream=stream, name=name, info='no information')

            user.message_set.create(message="Uploaded %s files" % count)

    return html.response('SUCCESS\n')

@login_required
def upload_start(request, pid):
    "Renders the upload page"
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=False)    
    return html.template( request=request, name='data-upload.html', project=project)

@login_required
def view(request, did):
    "Renders the data view page"
    user = request.user
    data = authorize.get_data(user=user, did=did)    
    param = html.Params(file_list=data.file_list(), image_list= data.image_list())
    return html.template( request=request, name='data-view.html', data=data, param=param)

@login_required
def getresult(request, rid, target):
    "Retreives a result"
    user = request.user
    result = authorize.get_result(user=user, rid=rid)
    if target == 'content':
        return html.download_stream(filename=result.content.path, name=result.name, asfile=True)
    elif target == 'image':
        return html.download_stream(filename=result.image.path, name=result.name, mimetype='image/png', asfile=False)
    else:
        raise Exception('unknown target=%s' % target)

if __name__ == '__main__':
    pass    