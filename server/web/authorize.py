import os
from genetrack import logger, util
from server.web import models, status
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.files import File

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

def get_data( user, did, write=True ):
    "Returns a project for a given user"
    try:
        data = models.Data.objects.get(id=did)
        member  = models.Member.objects.get( user=user, project=data.project )
        project = member.project
        project.role = member.role
        project.is_manager = (project.role == status.MANAGER)
        data.write_access = project.is_manager or (data.owner==user)
    except ObjectDoesNotExist, exc:
        logger.debug( exc )
        raise AccessError("You may not access this project")

    # write access check on by default
    if write and not data.write_access:
        logger.debug( 'write access with invalid role' )
        raise AccessError('You may not change this data')

    return data

def create_project( user, name, info='No info' ):
    """
    Creates a project and sets the user from the profile as the manager
    """
    project = models.Project.objects.create(name=name, info=info)
    member  = models.Member.objects.create(user=user, project=project, role=status.MANAGER)
    return project

def delete_data(user, pid, dids):
    "Deletes data from a project"
    project = get_project(user=user, pid=pid, write=False)  
    for did in dids:
        datum = models.Data.objects.get(id=did, project=project)
        if project.is_manager or datum.owner == user:
            datum.delete()
            user.message_set.create(message="Deleted data %s" % datum.name)
        else:
           user.message_set.create(message="May not delete data %s" % datum.name) 
    # update the data count    
    project.set_count()

def project_count(user):
    """
    Returns the number of projects a user has
    """
    if user.is_authenticated():
        return models.Member.objects.filter(user=user).count()
    else:
        return 0

def update_project( user, pid, name, info ):
    """
    Updates a project and sets the user from the profile as the manager
    """
    project = get_project(user=user, pid=pid, write=True) 
    models.Project.objects.filter(id=project.id).update(name=name, info=info)
    return project

def update_role(user, pid, action, uid):
    "Updates the role of a user 'uid' for project 'pid'"
    if not uid:
        return

    # fetch project and validate that is writable
    project = get_project(user=user, pid=pid, write=True) 

    # get the targeted user
    target = User.objects.get(id=uid)
    
    # user may not alter their own status
    if user.id == target.id:
        user.message_set.create(message="May not alter your own role!")
        return

    # information message
    user.message_set.create(message="Updated access for user %s" % target.get_full_name() ) 
 
    # remove all prior memberships for this user (should be one really)
    models.Member.objects.filter(user=target, project=project).all().delete()
    
    # find the roles
    roles = dict(addmanager=status.MANAGER, addmember=status.MEMBER)
    if action in roles:
        models.Member.objects.create(user=target, project=project, role=roles[action])

def create_data(user, pid, stream, name, info='no information', parent=None):
    """
    Creates a data entry from a django style stream (uploaded data)
    """
    proj = get_project(user=user, pid=pid, write=False) 
    data = models.Data( owner=user, project=proj, name=name, info=info)
    data.store(stream)    
    return data

if __name__ == '__main__':
    pass