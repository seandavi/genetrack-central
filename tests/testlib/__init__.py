"""
Test utilities
"""

class SkipMessages(object):
    """
    A class that maintains the skipped messages
    """
    def __init__(self):
        self.messages = []

    def add(self, msg):
        self.messages.append( msg )

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        return iter(self.messages)


BASE_URL = 'http://127.0.0.1:8080'
PROJECT_LIST_URL = '%s/project/list/' % BASE_URL

TWILL_QUIET = True

SKIP_MESSAGES = SkipMessages()

from pathfix import test_dir as TEST_DIR
from testutil import *
from testoptions import *
