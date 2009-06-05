"""
List of GeneTrack models
"""
import os
from genetrack import logger, util
from server.web import status
from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import signals

class JsonField(models.TextField):
    """
    JsonField is a generic textfield that neatly 
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

        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        elif value is not None:
            logger.warn('incorrect json value %s' % value)

        return super(JsonField, self).get_db_prep_save(value)

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
    json = JsonField(default="", null=True)

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
    json = JsonField(default="", null=True)
    data_count = models.IntegerField(default=0)
    class Meta:
        ordering = [ 'name' ]

    def __str__(self):
        return "Project: %s" % self.name
    
    def set_count(self):
        self.count = Data.objects.filter(project=self).count()

    def add_data(self, child, parent=None):
        "Adds a data to a project tree"
        tree, flag = ProjectTree.objects.get_or_create(project=self, child=child, parent=parent)
        if not flag:
            logger.warn('data %s is already in project %s' % (child, self))

    def data_list(self):
        "A list of all data in this project"
        return [ p.child for p in ProjectTree.objects.filter(project=self) ]

    def data_tree(self):
        "A tree of data"
        tree = {}
        pairs = [ (p.parent, p.child) for p in ProjectTree.objects.filter(project=self) ]
       
        return tree


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

class Data( models.Model ):
    """
    Data representation

    >>> joe, flag = User.objects.get_or_create(username='joe')
    >>> project, flag = Project.objects.get_or_create(name='Yeast Project')
    >>>
    >>> data1 = Data.objects.create(name="one", owner=joe, project=project)
    >>> data2 = Data.objects.create(name="two", owner=joe, project=project)
    >>> 
    >>> data1.status
    u'new'
    >>> data1.delete()
    """
    name     = models.TextField()
    uuid     = models.TextField()
    info     = models.TextField( default='no information' )
    status   = models.TextField( default=status.DATA_NEW )
    errormsg = models.TextField( default='' )
    tags     = JsonField( default={}, null=True)
    json     = JsonField( default={}, null=True)
    size     = models.IntegerField(default=0)
    owner    = models.ForeignKey(User)
    project  = models.ForeignKey(Project)
    tstamp   = models.DateField(auto_now_add=True)
  
    class Meta:
        ordering = [ 'id' ]

    def __str__(self):
        return 'Data %s' % self.name

    def path(self):
        return util.path_join(settings.FILE_DIR, '%s.dat' % self.uuid)

    def index(self):
        return util.path_join(settings.INDEX_DIR, '%s.idx' % self.uuid)

    def get_size(self):
        "Nicer, human readable size"
        return util.nice_bytes(self.size)

    def is_ready(self):
        return self.status in status.DATA_READY
 
    def has_errors(self):
        return self.status == status.DATA_ERROR
    
class ProjectTree( models.Model ):
    """
    Represents a parent-child relationship between data.

    Parents with value null indicate tree roots within a project

    >>> joe, flag = User.objects.get_or_create(username='joe')
    >>> project, flag = Project.objects.get_or_create(name='Yeast Project')
    >>>
    >>> data1 = Data.objects.create(name="one", owner=joe, project=project)
    >>> data2 = Data.objects.create(name="two", owner=joe, project=project)
    >>> data3 = Data.objects.create(name="three", owner=joe, project=project)
    >>> 
    >>> project.add_data(child=data1)
    >>> project.add_data(child=data2)
    >>> project.add_data(child=data3, parent=data2)
    >>>
    >>> project.data_list()
    [<Data: Data one>, <Data: Data two>, <Data: Data three>]
    >>>
    """
    project = models.ForeignKey( Project, related_name='tree' ) 
    child = models.ForeignKey( Data, related_name='children')
    # parent is null for a root data
    parent = models.ForeignKey( Data, related_name='parent', null=True )
 
   
   
class ProjectAdmin(admin.ModelAdmin):
    list_display = [ 'name' ]

class MemberAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'project' ]

class DataAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'project' ]

class ProjectTreeAdmin(admin.ModelAdmin):
    list_display = [ 'parent', 'child' ]

admin.site.register( Project, ProjectAdmin )
admin.site.register( Member, MemberAdmin )
admin.site.register( Data, DataAdmin )
admin.site.register( ProjectTree, ProjectTreeAdmin )


#
# Signal setup
#
# here we set up signals, that get trigger when various database events take place
def data_create_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for data to create an index
    """
    
    # populate the unique id if does not exist
    if not instance.uuid:
        instance.uuid = util.uuid()
        instance.save()

def data_delete_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post delete hook to remove a files related to a data
    """
    try:
        # remove data and index paths if exist
        paths = [ instance.path(), instance.index() ]
        for path in paths:
            if os.path.isfile(path):
                os.remove( path )
        #logger.info( 'removed %s' % instance )
    except Exception, exc:
        logger.error( '%s' % exc )

def user_profile_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for creating user profiles
    """
    try:
        instance.get_profile()
    except ObjectDoesNotExist, exc:
        #logger.debug( 'creating a user profile for %s' % instance.username )
        UserProfile.objects.create( user=instance )

signals.post_save.connect( data_create_trigger, sender=Data )
signals.post_delete.connect( data_delete_trigger, sender=Data )
signals.post_save.connect( user_profile_trigger, sender=User )