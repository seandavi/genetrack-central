"""
Data related views
"""
import os
from django.conf import settings
from django import forms
from genetrack import logger
from server.web import html, status
from server.web import models, authorize
from django.contrib.auth.decorators import login_required

class DataForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='New Project', widget=forms.TextInput(attrs=dict(size=80)))
    tags = forms.CharField( initial='Tag1, Tag2, Tag3', widget=forms.TextInput(attrs=dict(size=80)))
    info = forms.CharField( initial='Project Info', widget=forms.Textarea(attrs=dict(cols=60, rows=3)))

@login_required
def action(request, pid):
    "Delete or other actions"
    key  = 'delete-ids'
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=False)

    if 'delete' in request.GET:
        # instant deletes with GET
        dids = request.GET.getlist('did')
        authorize.delete_data(user=user, pid=pid, dids=dids)
        return html.redirect( "/project/view/%s/" % pid )

    elif 'delete' in request.POST:
        dids = request.session[key]
        del request.session[key]                
        authorize.delete_data(user=user, pid=pid, dids=dids)
        return html.redirect( "/project/view/%s/" % pid ) 
    else:
        dids = request.POST.getlist('did')
        url   = "/data/action/%s/" % pid 
        info = 'deleting %s datasets' % len(dids)
        request.session[ key ] = dids
        return html.template( request=request, name='confirm.html', info=info, user=user )


@login_required
def download(request, did):
    "Edits an existing project"
    user = request.user
    try:
        data = models.Data.objects.get(id=did)
        project = authorize.get_project(user=user, pid=data.project.id, write=False)
    except ObjectDoesNotExist, exc:
        raise authorize.AccessError()
    
    return html.download(data)


@login_required
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
        form = DataForm( dict(name=data.name, info=data.info, tags=data.text_tags() ) )        
        return html.template( request=request, name='data-edit.html', did=did, user=user, form=form )
    
    # form submission
    form = DataForm( request.POST )  
    if form.is_valid():
        get  = form.cleaned_data.get      
        tags = str( get('tags') )
        tags = util.tagsplit( tags )
        data.name = get('name')
        data.info = get('info')
        data.tags = tags
        data.save()
        return html.redirect("/project/view/%s/" % data.project.id)
    else:    
        return html.template( request=request, name='data-edit.html', did=did, user=user, form=form )
        
@login_required
def summary(request, did):
    "Redirects to the summary page"
    user = request.user
    data = authorize.get_data(user=user, did=did)
    
    template = request.POST.get('template')
    
    if template:
        data.delete_summary()
        jobutil.SummaryJob.create( data=data, models=models, template=template)

    if data.has_summary():
        return html.redirect("/static/summary/%s/index.html" % data.uuid)    
    else:
        return html.redirect("/project/view/%s" % data.project.id)    

def chop_dirname(name):
    "Removes directory from the name."
    # some browsers may send the full pathname
    name = name.replace("\\", "/")
    name = os.path.basename( name )
    return name

def upload_processor(request, pid):
    "Handles the actual data upload"
    user = request.user
    if user.is_authenticated():
        if 'upload' in request.POST:
            # take at most 50 files
            count = 0
            for i in range(50):
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
    return html.template( request=request, name='data-view.html', data=data)


if __name__ == '__main__':
    pass    