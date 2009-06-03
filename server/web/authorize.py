import os
from genetrack import logger
from server.web import models, status
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class AccessError(Exception):
     def __init__(self, msg='Invalid access'):
        Exception.__init__(self, msg)

def project_list(user):
    "Returns all projects by a user"
    members  = models.Member.objects.filter( user=user ).select_related().all()
    projects = []
    for member in members:
        p = member.project
        p.role = member.role
        p.is_manager = (p.role == status.MANAGER)
        projects.append( p )
    projects = sorted( projects, key=lambda elem: elem.id, reverse=True )
    return projects

def get_project( user, pid, write=True ):
    "Returns a project for a given user"
    try:
        member  = models.Member.objects.get( user=user, project__id=pid )
        project = member.project
        project.role = member.role
        project.is_manager = (project.role == status.MANAGER)
    except ObjectDoesNotExist, exc:
        logger.debug( exc )
        raise AccessError("You may not access this project")

    # write access check on by default
    if write and not project.is_manager:
        logger.debug( 'write access with invalid role' )
        raise AccessError('You may not change this project')
        
    return member.project

def project_count(user):
    """
    Returns the number of projects a user has
    """
    if user.is_authenticated():
        return models.Member.objects.filter(user=user).count()
    else:
        return 0

def create_project( user, name, info ):
    """
    Creates a project and sets the user from the profile as the manager
    """
    project = models.Project.objects.create(name=name, info=info)
    member  = models.Member.objects.create(user=user, project=project, role=status.MANAGER)
    user.message_set.create(message="Created a new project")
    return project

def update_project( user, pid, name, info ):
    """
    Updates a project and sets the user from the profile as the manager
    """
    project = get_project(user=user, pid=pid, write=True) 
    models.Project.objects.filter(id=project.id).update(name=name, info=info)
    return project

if __name__ == '__main__':
    pass