import testlib
import os, unittest, random
from django.test import utils
from django.db import connection
from django.conf import settings
from genetrack import conf, util, logger
from server.scripts import initializer
from server.web import html
from django.contrib.auth.models import User

class AuthorizeTest( unittest.TestCase ):
    """
    Tests the models
    """
    def setUp(self):
        "Setting up the tests database for data insert"
        self.old_name = settings.DATABASE_NAME
        utils.setup_test_environment()
        connection.creation.create_test_db(verbosity=0, autoclobber=True)
        options = util.Params(test_mode=True, delete_everything=False, flush=False, verbosity=0)
        fname = conf.testdata('test-users.csv')
        initializer.load_users(fname, options)
        

    def tearDown(self):
        "Tearing down the database after test"
        connection.creation.destroy_test_db(self.old_name, 0)
        utils.teardown_test_environment()
    
    def test_data_creation(self):
        """
        Create datasets
        """
        
        # it seems that importing it earlier messes up the test database setup
        from server.web import authorize

        john = User.objects.get(username='johndoe')
        project = authorize.create_project(user=john, name="Test project")
        stream = html.make_stream( conf.testdata('test-users.csv') )
        data = authorize.create_data(user=john, pid=project.id, stream=stream, name="Test data")


    def test_two(self):
        pass

def get_suite():
    "Returns the testsuite"
    tests  = [ 
        AuthorizeTest,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    logger.disable('DEBUG')
    unittest.TextTestRunner(verbosity=2).run( suite )