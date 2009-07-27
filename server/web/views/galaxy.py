"""
Galaxy controller for GeneTrack.
"""
from server.web.views import data

import simplejson as json
from galaxy import web
from galaxy.web.base.controller import BaseController
from galaxy.model.orm import *

# main controller
class GeneTrackController( BaseController ):
    
    @web.expose
    def default(self, trans, msg='?',**kwds):
        return 'Invalid Genetrack action -> %s' % msg

    @web.expose
    def view(self, trans, id=123, auth=None, realm=None):
        return '123'
