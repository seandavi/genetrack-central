import os, unittest, random
import testlib

import twill
from twill import commands as tc
from StringIO import StringIO

# django specific handlers
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

class ServerTest( unittest.TestCase ):
    'basic sequence class tests'
    
    def setUp(self):
        twill_setup()

    def tearDown(self):
        twill_teardown()


    def test_all(self):
        "Server access"
        twill_quiet()
        tc.go( testlib.BASE_URL )
        tc.code(200)
        tc.find("GeneTrack") 

    def test_fail(self):
        "Server access"
        #1/0

        
def get_suite():
    "Returns the testsuite"
    tests  = [ 
        ServerTest,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run( suite )
