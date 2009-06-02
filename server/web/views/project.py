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
    user = request.user
    projects = authorize.project_list(user)
    return html.template( request=request, name='project-list.html', projects=projects )

@login_required
def edit(request, pid):
    "Updates or creates a project"
    user = request.user
    
    form = ProjectForm( request.POST )   
    
    if form.is_valid():
        # incoming data
        get = form.cleaned_data.get
        if pid == 'new':
            authorize.create_project(user=user, name=get('name'), info=get('info') )
        else:
            authorize.update_project(user=user, pid=pid, name=get('name'), info=get('info') )
        return html.redirect("/project/list/")
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
 
if __name__ == '__main__':
    pass    