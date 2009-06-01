"""
List of GeneTrack models
"""
from genetrack import logger
from server.web import status
from types import NoneType
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import signals

class JSONField(models.TextField):
    """
    JSONField is a generic textfield that neatly 
    serializes/unserializes JSON objects seamlessly
    from : http://www.djangosnippets.org/snippets/1478/
    """

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """
        Convert our string value to JSON after we load it from the DB
        """
        if not value:
            return None
        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        elif value is not None:
            logger.warn('incorrect json value %s' % value)

        return super(JSONField, self).get_db_prep_save(value)

class UserProfile( models.Model ):
    """
    Stores user options

    >>> user = User.objects.create(first_name='Jane', last_name='Doe', username='jane', email='jane')
    >>> prof = user.get_profile()
    >>> prof.json = dict( message='Hello world' )
    >>> prof.save()
    >>>
    >>> # now retrieve the profile
    >>> json = User.objects.get(username='jane').get_profile().json
    >>> json['message']
    u'Hello world'
    """
    user = models.ForeignKey(User, unique=True)
    json = JSONField(default="", null=True)

class Project( models.Model ):
    """
    Project representation

    >>> proj = Project.objects.create(name="Project", info="some info", json=dict(value=1))
    >>> proj.json
    {'value': 1}
    >>> proj.json = dict(message="Hello World")
    >>> proj.save()
    >>> proj.json
    {'message': 'Hello World'}
    """
    name = models.TextField()
    info = models.TextField( default='no information' )
    is_public = models.BooleanField( default=False )
    tstamp = models.DateField(auto_now_add=True)
    json = JSONField(default="", null=True)

    class Meta:
        ordering = [ 'name' ]

    def __str__(self):
        return "Project: %s" % self.name

class Member( models.Model ):
    """
    Maintains membership information between a project and a user

    >>> user = User.objects.create(first_name='John', last_name='Doe', email='john')
    >>> proj = Project.objects.create(name="Project", info="some info", json=dict(value=1))
    >>> memb = Member(user=user, project=proj, role=status.MANAGER)
    >>> memb.role
    'manager'
    """
    roles   = [ status.MANAGER, status.MEMBER ]
    choices = zip(roles, roles)

    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    role = models.CharField(max_length=100, choices=choices, default=status.MEMBER)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        ordering = [ 'project__id' ]

    def __unicode__(self):
        return u'Member: %s, %s (%s)' % (self.user, self.project, self.role)

class ProjectAdmin(admin.ModelAdmin):
    list_display = [ 'name' ]

class MemberAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'project' ]


admin.site.register( Project, ProjectAdmin )
admin.site.register( Member, MemberAdmin )

#admin.site.register( models.DataTree, DataTreeAdmin )


#
# Signal setup
#
# here we set up signals, that get trigger when various 
# database events take place
#

def user_profile_create(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for creating user profiles
    """
    try:
        instance.get_profile()
    except ObjectDoesNotExist, exc:
        #logger.debug( 'creating a user profile for %s' % instance.username )
        UserProfile.objects.create( user=instance )

signals.post_save.connect( user_profile_create, sender=User )