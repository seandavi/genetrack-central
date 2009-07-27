"""
List of GeneTrack models
"""
import os
from genetrack import logger, util, conf
from genetrack.server.web import status, jobs
from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import signals
from django.core.files import File

def to_stream(stream):
    """
    Utility function that turns a file name, or file stream into a 
    Django file stream
    """
    if isinstance(stream, File):
        return stream
    elif type(stream) == file:
        return File(stream)
    elif type(stream) in (str, unicode):
        return File(open(stream, 'rb'))   
    raise Exception('invalid stream type %s' % type(stream))

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
    
    def track_count(self):
        return Track.objects.filter(project=self).count()

    def refresh(self):
        "Refreshes statically maintained values"
        self.data_count = Data.objects.filter(project=self).count()
        self.save()

    @property
    def members(self):    
        return Member.objects.filter(project=self).select_related().all()

    def names_by_role(self, role):
        text  = ", ".join( sorted( [ m.user.get_full_name() for m in self.members if m.role==role ]))
        return text or 'None'

    @property
    def member_names(self):
        return self.names_by_role(role=status.MEMBER)
    
    @property
    def manager_names(self):
        return self.names_by_role(role=status.MANAGER)

    def track_data(self):
        "Data that is viewable in a track"
        return [ d for d in self.data_list() if d.status in status.VIEWABLE ]

    def data_list(self):
        "A list of all data in this project"
        return [ d for d in Data.objects.filter(project=self).order_by('-id') ]

class Member(models.Model):
    """
    Maintains membership information between a project and a user

    >>> user = User.objects.create(first_name='John', last_name='Doe', email='john')
    >>> proj = Project.objects.create(name="Project", info="some info", json=dict(value=1))
    >>> memb = Member(user=user, project=proj, role=status.MANAGER)
    >>> memb.role
    u'manager'
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
    >>> project, flag = Project.objects.get_or_create(name='Yeast Project 9')
    >>> data1 = Data.objects.create(name="one", owner=joe, project=project)
    >>> 
    >>> stream = conf.testdata('short-data.bed')
    >>> data1.store(stream)
    >>> project.data_count
    1
    >>> data1.status
    u'stored'
    >>> data1.delete()
    >>>
    >>> # project datacounts refreshed
    >>> project.data_count
    0
    """

    # one of the acceptable states
    choices = zip(status.ALL, status.ALL)

    uuid      = models.TextField()
    name      = models.TextField()
    ext       = models.TextField(null=True) # extension
    mime      = models.TextField(default='application/octetstream', null=True)
    info      = models.TextField(default='no information', null=True)
    status    = models.TextField(default=status.NEW, choices=choices)
    errors    = models.TextField(default='', null=True )
    tags      = JsonField( default={}, null=True)
    json      = JsonField( default={}, null=True)
    owner     = models.ForeignKey(User)
    project   = models.ForeignKey(Project, related_name='data')
    content   = models.FileField(upload_to='files/')
    tstamp    = models.DateField(auto_now_add=True)

    class Meta:
        ordering = [ 'id' ]

    def __str__(self):
        return 'Data %s' % self.name

    def path(self):
        if self.content:
            return self.content.path
        else:
            return None

    def result_count(self):
        return len(self.results.all())

    def short_result_list(self):
        return self.results.all().order_by('-id')[:3]

    def result_list(self):
        return self.results.all().order_by('-id') 

    def file_list(self):
        return [ r for r in self.result_list() if r.has_content() and not r.has_image()]

    def image_list(self):
        return [ r for r in self.result_list() if r.has_image() ]

    def get_size(self):
        "Nicer, human readable size"
        return util.nice_bytes(self.content.size)

    def is_ready(self):
        return self.status in status.READY
 
    def store(self, stream):
        """
        Stores a stream as the data content. The uuid will be the name
        of the file.
        """
        if not self.uuid:
            self.uuid = util.uuid()
        stream = to_stream(stream)
        self.content.save(self.uuid, stream)

    def has_errors(self):
        return self.status == status.ERROR
    
    def __hash__(self):
        return hash(self.id)

    def __cmp__(self, other):
        return cmp(self.id, other.id)

class Result(models.Model):
    """
    Datasets that are derived from an existing data. 

    >>> joe, flag = User.objects.get_or_create(username='joe')
    >>> project, flag = Project.objects.get_or_create(name='Yeast Project')
    >>>
    >>> data1, flag = Data.objects.get_or_create(name="Data 123", owner=joe, project=project)
    >>>
    >>> # the stream may be filename or an open file stream
    >>> stream = open(conf.testdata('short-data.bed'))
    >>> result = Result(data=data1, name='Result 123')
    >>> result.store( content=stream )
    >>> result.data.name
    'Data 123'
    >>> data1.results.all()[0].name
    u'Result 123'
    >>> result.delete()
    """
    name  = models.TextField(default='Title', null=True)
    mime  = models.TextField(default='application/octetstream', null=True)
    info  = models.TextField(default='info', null=True)
    uuid  = models.TextField()
    data  = models.ForeignKey(Data, related_name='results')
    content = models.FileField(upload_to='results')
    image = models.FileField(upload_to='images')

    def store(self, content, image=None):
        """
        Stores a stream as the data content. The uuid will be the name
        of the file.
        """
        if not self.uuid:
            self.uuid = util.uuid()
            self.save()
        if content:
            content = to_stream(content)
            self.content.save(self.uuid, content)
        if image:
            image = to_stream(image)
            self.image.save(self.uuid, image)
        
    def has_image(self):
        return bool(self.image)

    def has_content(self):
        return bool(self.content)

    @property
    def thumbname(self):
        "Thumbnail image name"
        return "t-%s.png" % self.uuid
    
    @property
    def thumbpath(self):
        "Thumbnail image path"
        return conf.path_join(settings.THUMB_IMAGE_DIR, self.thumbname)

class Job(models.Model):
    """
    Job representation 

    >>> joe, flag = User.objects.get_or_create(username='joe')
    """
    choices = zip(status.ALL, status.ALL)

    name   = models.TextField(default='Title', null=True)
    info   = models.TextField(default='info', null=True)
    errors = models.TextField(default='', null=True )
    owner  = models.ForeignKey(User)
    json   = JsonField(default="", null=True)
    status = models.TextField(default=status.NEW, choices=choices)

    def __str__(self):
        return "<Job id=%s: json=%s>" % (self.id, self.json)

class Track(models.Model):
    """
    Represents a set of tracks
    """
    class Meta:
        ordering = ["-id"]

    uuid = models.TextField()
    name = models.TextField()
    json = JsonField(default="", null=True)
    text = models.TextField(default="", null=True)
    owner = models.ForeignKey(User)
    project = models.ForeignKey(Project, related_name='tracks')    
    tstamp = models.DateField(auto_now_add=True)

    # allows the customization of the Track page
    template = models.TextField(default="base-track.html", null=True)
    footer = models.TextField(default="", null=True)
    
#
# Administration classes
#
class ProjectAdmin(admin.ModelAdmin):
    list_display = [ 'name' ]

class MemberAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'project' ]

class DataAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'project' ]

class ResultAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'data' ]

class JobAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'owner' ]

admin.site.register( Project, ProjectAdmin )
admin.site.register( Member, MemberAdmin )
admin.site.register( Data, DataAdmin )
admin.site.register( Result, ResultAdmin )
admin.site.register( Job, JobAdmin )

#
# Signal setup
#
# here we set up signals, that get trigger when various database events take place

def data_save_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for data
    """

    # update project datacounts
    instance.project.refresh()

    # detect extensions and trigger indexing jobs whenever necessary
    ext = os.path.splitext(instance.name)[1].lstrip('.')
    if ext != instance.ext:
        instance.ext = ext
        jobs.detect(data=instance, ext=ext, JobClass=Job)
        instance.save()

def result_save_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for results, creates the thumbnails
    """
    if instance.image:
        try:
            # requires PIL
            size = 300, 300
            import Image  
            img = Image.open(instance.image.path)
            img.thumbnail(size, Image.ANTIALIAS)
            img.save(instance.thumbpath)
        except Exception, exc:
            logger.error(exc)

def data_delete_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post delete hook for data
    """
    # update project datacounts
    instance.project.refresh()

def user_profile_trigger(sender, instance, signal, *args, **kwargs):
    """
    Post save hook for creating user profiles
    """
    try:
        instance.get_profile()
    except ObjectDoesNotExist, exc:
        #logger.debug( 'creating a user profile for %s' % instance.username )
        UserProfile.objects.create( user=instance )

#signals.post_delete.connect( data_delete_trigger, sender=Data )
signals.post_save.connect( data_save_trigger, sender=Data )

signals.post_save.connect( result_save_trigger, sender=Result )

signals.post_delete.connect( data_delete_trigger, sender=Data )

signals.post_save.connect( user_profile_trigger, sender=User )