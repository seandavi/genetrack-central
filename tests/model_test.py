import testlib
import os, unittest, random
from django.test import utils
from django.db import connection
from django.conf import settings
from genetrack import conf, util, logger
from genetrack.scripts import initializer

class ModelTest( unittest.TestCase ):
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
        logger.disable('INFO') # too many user created messages
        initializer.load_users(fname, options)
        logger.disable(None)

    def tearDown(self):
        "Tearing down the database after test"
        connection.creation.destroy_test_db(self.old_name, 0)
        utils.teardown_test_environment()
    
    def test_one(self):
        pass

    def test_two(self):
        pass

def get_suite():
    "Returns the testsuite"
    tests  = [ 
        ModelTest,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    logger.disable(None)
    unittest.TextTestRunner(verbosity=2).run( suite )