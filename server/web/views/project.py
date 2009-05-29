"""
Project related views
"""
from django.conf import settings
from genetrack import logger
from server.web import html
from server.web import models, authorize
from django.contrib.auth.decorators import login_required

@login_required
def listall(request):
    "Lists all projects"
    user = request.user
    projects = authorize.project_list(user)
    return html.template( request=request, name='project-list.html', projects=projects )

if __name__ == '__main__':
    pass    