"""
Project related views
"""
from django.conf import settings
from django import forms
from genetrack import logger
from server.web import html, status
from server.web import models, authorize
from django.contrib.auth.decorators import login_required

class ProjectForm(forms.Form):
    "For project editing"    
    name = forms.CharField( initial='New Project', widget=forms.TextInput(attrs={'size':'75', 'class':"textinput"}))
    info = forms.CharField( initial=status.DEFAULT_PROJECT_INFO, widget=forms.Textarea(attrs={ 'cols':'80', 'rows':'15','class':"textinput" }))

@login_required
def listall(request):
    "Lists all projects"
    params = html.Params()
    projects = authorize.project_list(request.user)
    params.project_count = authorize.project_count(request.user)
    return html.template( request=request, name='project-list.html', projects=projects, params=params )

@login_required
def share(request, pid):
    "Lists all projects"
    user = request.user
    projects = authorize.project_list(user)
    return html.template( request=request, name='project-list.html', projects=projects )

@login_required
def delete(request, pid):
    "Deletes a project (with confirmation)"
    user = request.user
    project = authorize.get_project(user=user, pid=pid, write=True)    
    if 'delete' in request.POST:
        project.delete()
        user.message_set.create(message="Project deletion complete")
        return html.redirect("/project/list/") 
    else:        
        return html.template( request=request, name='project-delete.html', project=project)
    
@login_required
def edit(request, pid):
    "Updates or creates a project"
    user = request.user
    
    form = ProjectForm( request.POST )   
    
    if form.is_valid():
        # incoming data
        get = form.cleaned_data.get
        if pid == 'new':
            project = authorize.create_project(user=user, name=get('name'), info=get('info') )
            return html.redirect("/project/list/")
        else:
            authorize.update_project(user=user, pid=pid, name=get('name'), info=get('info') )
            return html.redirect("/project/view/%s/" % pid)
    else:
        # no form data sent
        if pid == 'new':
            title = 'Create New Project'
            form = ProjectForm( )            
        else:
            title = 'Edit Project'
            project = authorize.get_project(user=user, pid=pid)
            form = ProjectForm( dict(name=project.name, info=project.info) )        
        return html.template( request=request, name='project-edit.html', pid=pid, title=title, form=form )
 
@login_required
def view(request, pid):
    "Lists all projects"
    project = authorize.get_project(user=request.user, pid=pid, write=False)
    return html.template( request=request, name='project-view.html', project=project)


if __name__ == '__main__':
    pass    