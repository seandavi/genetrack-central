# Django settings for server project.
import sys, os

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

# establish the current location
curr_dir  = os.path.dirname( __file__ )

# set up the data specific directories relative to this file's location
TEMPLATE_PATH = path_join( curr_dir, 'data', 'templates')
DATA_DIR = path_join( curr_dir, 'data')
STATIC_DIR = path_join( DATA_DIR, 'static')
STORAGE_DIR = path_join( DATA_DIR, 'storage')
DATABASE_DIR = path_join(  DATA_DIR, 'db')


# debug mode set to on if a sentinel file is present
DEBUG = os.path.isfile(path_join(curr_dir, 'debug-mode'))

TEMPLATE_DEBUG = DEBUG

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

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_DOMAIN = '127.0.0.1:8080'
SITE_NAME = 'GeneTrack' 
SITE_ID = 1

EMAIL_HOST = "smtp.psu.edu"
#EMAIL_HOST_USER = "foo"
#EMAIL_HOST_PASSWORD = "bar"
DEFAULT_FROM_EMAIL  = "iua1@psu.edu"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

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

# allows setting the secret key externally
# make it long and unique, and don't share it with anybody.
# it will be used as the default admin password
secret_fname=path_join(curr_dir, 'secret-key')
if os.path.isfile(secret_fname):
    # file must have only one line
    SECRET_KEY = file(secret_fname).read().strip()
else:
    # you can set the secret key directly
    SECRET_KEY = '1' # this value is for debuggin only

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

ROOT_URLCONF = 'server.urls.urlconf'

TEMPLATE_DIRS = (
    TEMPLATE_PATH,

    # custom pages for password recovery
    path_join(TEMPLATE_PATH, 'password'),

    # pages for projects
    path_join(TEMPLATE_PATH, 'project'),

    # custom pages for administration
    path_join(TEMPLATE_PATH, 'admin'),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.markup',
    'server.web',
)
