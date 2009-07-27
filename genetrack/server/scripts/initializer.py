"""
Initializes the active database with users. 
Will only load users that do not already exist.
Users will need to reset their passwords or the 
admin user will need to change these. Usage::

    python -m genetrack.scripts.initializer <userfile>

The userfile is a comma separated file with columns for username, email etc.
See the server/data/init/initial-users.csv file for more details.

"""
from genetrack import logger
import csv, os, sys
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.management import setup_environ, call_command  

def flush_database():
    "Delets all entries"
    logger.info( "flushing the database" )
    #Data.objects.all().delete()
    call_command( 'flush' ) 

def fix_site_settings():
    """
    On first run the site information may not be correct. 
    This function updates the site to the correct values
    """
    site, flag = Site.objects.get_or_create( id=settings.SITE_ID )
    if site.domain != settings.SITE_DOMAIN:
        site.domain, site.name=settings.SITE_DOMAIN, settings.SITE_NAME
        logger.debug('modifying site domain:%s name: %s' % (site.domain, site.name) )
        site.save()

def user_dict():
    "Returns a dictionary with all existing users keyed by username"
    users = dict( (user.username, user) for user in User.objects.all() )
    return users

def load_users(fname, options):
    "Loads users into the database"

    if not os.path.isfile(fname):
        logger.error('file not found %s' % fname)
        return

    if options.flush:
        "Resets the database with fresh values"
        flush_database()

    # alters site settings
    fix_site_settings()

    # this will be the admin password
    passwd = settings.SECRET_KEY

    # check the lenght of secret key in non debug modes
    if not settings.DEBUG and len(passwd) < 5:
        msg = 'The value of the SECRET_KEY setting is too short. Please make it longer!'
        logger.error(msg)
        sys.exit()
    
    # shorcut to user creatgion
    user_get = User.objects.get_or_create

    # read the file and create the users based on the data in it
    stream = file(fname)
    for row in csv.DictReader( stream ):
        username, email, first_name, last_name = row['username'], row['email'], row['first_name'], row['last_name']
        is_superuser = (row['is_superuser'] == 'yes')
        user, flag = user_get(username=username, email=email, first_name=first_name, last_name=last_name, is_superuser=is_superuser, is_staff=is_superuser)
        if flag:
            logger.debug( 'created user: %s' % user.get_full_name() )
            if username in ('admin', 'demo', 'public'):
                # admin user will get the secret key as password
                user.set_password(passwd)
            else:
                if options.test_mode:
                    # in testmode we will set known passwords
                    # used during functional testing
                    user.set_password( passwd + 'X')
                else:
                    # all other users will need to reset their passwords 
                    user.set_unusable_password()
            user.save()

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog userfile "

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-u', '--users', action="store", 
        dest="users", type='str', default=None,
        help="the input file name that contain initial users (required)"
    )

    # verbosity can be 0 or 1(increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    # flushes all content away, drops all database content!
    parser.add_option(
        '--delete_everything', action="store_true", 
        dest="flush", default=False, 
        help="flushes the database removing everyting that it contains!",
    )

    # flushes all content away, drops all database content!
    parser.add_option(
        '--test_mode', action="store_true", 
        dest="test_mode", default=False, 
        help="turns on testmode for all users!",
    )

    # parse the argument list
    options, args = parser.parse_args()

    # set verbosity
    if options.verbosity > 0:
        logger.disable(None)

    # missing file names
    if not args or len(args)>1:
        parser.print_help()
    else:
       
        load_users(fname=args[0], options=options)
