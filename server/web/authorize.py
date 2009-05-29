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