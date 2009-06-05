"""
Functional tests via twill
"""
import os, unittest, random
import testlib

from genetrack import logger

import twill
from twill import commands as tc
from StringIO import StringIO

from django.conf import settings

# django specific handlers
from django.test import TestCase, utils
from django.core.servers.basehttp import AdminMediaHandler
from django.core.handlers.wsgi import WSGIHandler

def twill_setup():
    app = AdminMediaHandler(WSGIHandler())
    twill.add_wsgi_intercept("127.0.0.1", 8080, lambda: app)

def twill_teardown():
    twill.remove_wsgi_intercept('127.0.0.1', 8080)

def twill_quiet():
    # suppress normal output of twill.. You don't want to 
    # call this if you want an interactive session
    if testlib.TWILL_QUIET:
        twill.set_output(StringIO())

class TwillTest( TestCase ):
    """
    Base class for twill tests
    """
    fixtures = [ 'test-fixture.json' ]

    def setUp(self):
        twill_setup()
        twill_quiet()
    
    def tearDown(self):
        twill_teardown()

class BaseTest( TwillTest ): 
    """
    Basic functionality of the site. Also does link checking
    """
    def test_main(self):
        #testing main page
        tc.go( testlib.BASE_URL )
        tc.code(200)
        tc.find("GeneTrack") 
        tc.find("You are not logged in") 

    def test_404(self):
        # testing 404 errors
        tc.go( testlib.BASE_URL )
        tc.go( "./nosuchurl" )
        tc.code(404)
        
class ServerTest( TwillTest ):
    """
    Full server test.
    """
    fixtures = [ 'test-fixture.json' ]
    
    def setUp(self):
        TwillTest.setUp(self)
        self.login()

    def tearDown(self):
        self.logout()
        TwillTest.tearDown(self)

    def login(self, name='admin', passwd='1'):
        "Performs a login"
        tc.go( testlib.BASE_URL )
        tc.follow('Log in now')
        tc.find("Please log in") 
        tc.code(200)
        
        # logs in on every test
        tc.fv("1", "email", name)
        tc.fv("1", "password", passwd)
        tc.submit('0')
        tc.code(200)
        tc.find("Logged in as") 

    def logout(self):
        "Performs a logout"
        tc.go( testlib.PROJECT_LIST_URL )
        tc.code(200)
        tc.go("/logout/")
        tc.code(200)
        tc.find("You are not logged in")

    def test_project_actions(self):
        
        # main page
        tc.go( testlib.PROJECT_LIST_URL )
        tc.find("Logged in as") 

        # default project list
        tc.find("Fly data 19") 
        tc.find("Human HELA 16") 
        tc.find("Mouse project HBB 1") 

        # create a new project
        name = "Rainbow Connection - New Project"
        tc.follow('New Project')
        tc.code(200)
        tc.find("Create New Project")
        tc.fv("1", "name", name )
        tc.fv("1", "info", "Some *markup* goes here")
        tc.submit()
        tc.code(200)
        tc.find(name)

        # visit this new project
        tc.follow(name)
        tc.code(200)
        tc.find("Project: %s" % name)

        # edit and rename project
        newname = "Iguana Garden - New Project"
        tc.follow("Edit")
        tc.find("Edit Project")
        tc.fv("1", "name", newname )
        tc.fv("1", "info", "Some other *markup* goes here")
        tc.submit()
        tc.code(200)
        tc.notfind(name)
        tc.find(newname)

        # delete the project
        tc.follow("Delete")
        tc.find("You are removing")
        tc.fv("1", "delete", True)
        tc.submit()
        tc.code(200)
        tc.find("Project deletion complete")
        tc.notfind(name)
        tc.notfind(newname)

    def test_project_member_sharing(self):

        # tests sharing as a member
        tc.go( testlib.PROJECT_LIST_URL )
        tc.find("Logged in as") 
        
        # a project list with member access
        tc.find("Fly data 19") 
        tc.follow("Fly data 19")
        tc.follow("Sharing")
        tc.find("Current members")
        
        # members may not add access
        tc.notfind("Add access")
        tc.follow("<< return to project")
        tc.find("Project: Fly data 19") 

    def test_project_manager_sharing(self):
        # test sharing as a manager

        # main page
        tc.go( testlib.PROJECT_LIST_URL )
        tc.find("Logged in as") 
        
        # default project list
        tc.find("Yeast mutant RAV 17") 
        tc.follow("Yeast mutant RAV 17")
        tc.follow("Sharing")
        tc.find("Current members")
        tc.find("Add access")

        # search for then add Demo User to this project
        tc.fv("1", "text", "demo" )
        tc.submit()
        tc.code(200)
        tc.find("Demo User")
        tc.follow("add as member")
        tc.find("Demo User")

        # back to the project view
        tc.follow("<< return to project")
        tc.find("Yeast mutant RAV 17") 


    def test_project_access(self):  
        # verifies project access

        # may view this project
        tc.go("/project/view/19/")
        tc.code(200)

        # may not edit it
        tc.go("/project/edit/19/")
        tc.code(500)

        # may not delete it
        tc.go("/project/delete/19/")
        tc.code(500)

        # project does not exist (will return no access)
        tc.go("/project/view/190/")
        tc.code(500)

def get_suite():
    "Returns the testsuite"
    return testlib.make_suite( [] )

def local_suite():
    "Returns the testsuite"
    tests  = [ 
        BaseTest,
        ServerTest,
    ]
    return testlib.make_suite( tests )

def test_runner( suite, verbosity=0 ):
    "Runs the functional tests on a test database"
    from django.db import connection
    
    old_name = settings.DATABASE_NAME
    utils.setup_test_environment()
    connection.creation.create_test_db(verbosity=verbosity, autoclobber=True)
    result = unittest.TextTestRunner(verbosity=2).run(suite) 
    connection.creation.destroy_test_db(old_name, verbosity)
    utils.teardown_test_environment()
    
if __name__ == '__main__':
    logger.info("executing functional tests")
    suite = local_suite()
    test_runner( suite, verbosity=0)
