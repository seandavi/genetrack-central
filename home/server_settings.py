"""
A copy of this settings file may be customized and loaded via 
DJANGO_SETTINGS_MODULE or the --settings parameter
"""
# Django settings for server project.
import sys, os, random, hashlib

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

# establish the current location
curr_dir  = os.path.dirname( __file__ )

# debug mode, set to False in production systems
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# set up the data specific directories relative to this file's location
HOME_DIR        = path_join(curr_dir)
TEMPLATE_PATH   = path_join(HOME_DIR, 'templates')
STATIC_DIR      = path_join(HOME_DIR, 'static')
STORAGE_DIR     = path_join(HOME_DIR, 'storage')
DATABASE_DIR    = path_join(HOME_DIR, 'db')
CACHE_DIR       = path_join(STATIC_DIR, 'cache')
THUMB_IMAGE_DIR = path_join(STATIC_DIR, 'thumbs')

# create some directories if missing
for dirname in (STORAGE_DIR, CACHE_DIR, DATABASE_DIR, THUMB_IMAGE_DIR):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)        

SITE_DOMAIN = '127.0.0.1:8080'
SITE_NAME = 'GeneTrack' 
SITE_ID = 1

EMAIL_HOST = "smtp.psu.edu"
#EMAIL_HOST_USER = "foo"
#EMAIL_HOST_PASSWORD = "bar"
DEFAULT_FROM_EMAIL  = "iua1@psu.edu"

ADMINS = (
    ('Istvan Albert', 'istvan.albert@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = path_join(DATABASE_DIR, 'genetrack.db') # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Allows setting the secret key externally
# It generates a secret key on first run if is missing 
# that is used as the admin password
secret_fname = path_join(HOME_DIR, 'SECRET-KEY')
if not os.path.isfile(secret_fname):
    value = str(random.getrandbits(128))
    value = hashlib.md5(value).hexdigest()
    fp = file(secret_fname, 'wt')
    fp.write(value)
    fp.close()

# loads up the secret key
SECRET_KEY = file(secret_fname).read().strip()

# tool secret for GALAXY integration, must match the value
# for the key tool_secret located in universe_wsgi.ini
GALAXY_TOOL_SECRET ="changethisinproduction"
GALAXY_TOOL_URL = "http://127.0.0.1:8080/tool_runner?tool_id=predict2genetrack"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
MEDIA_ROOT = STORAGE_DIR

# redirects here for login
LOGIN_URL = "/login"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# this settings allows adminstrators to log in as other users
# with the SECRET_KEY as password 
SUPERUSER_PASSWORD_OVERRIDE = True

AUTH_PROFILE_MODULE = "web.userprofile"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'genetrack.server.urls.urlconf'

TEMPLATE_DIRS = (
    TEMPLATE_PATH,

    # custom pages for password recovery
    path_join(TEMPLATE_PATH, 'password'),

    # pages for projects
    path_join(TEMPLATE_PATH, 'project'),
    
    # pages for projects
    path_join(TEMPLATE_PATH, 'data'),

    # custom pages for administration
    path_join(TEMPLATE_PATH, 'admin'),

    # custom pages for tracks
    path_join(TEMPLATE_PATH, 'track'),

    # custom template tags
    path_join(TEMPLATE_PATH, 'tags'),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.markup',
    'genetrack.server.web',
)
