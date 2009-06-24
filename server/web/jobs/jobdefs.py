from genetrack import hdflib, logger
from server.web import status

def set_status(obj, status, errmsg=''):
    "Sets the status on an object that has status and errors fields."
    obj.status = status
    obj.errors = errmsg
    obj.save()

class StatusUpdate:    
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwds):
        data = kwds.get('data')
        if data:
            set_status(data, status=status.RUNNING)                    
            result = self.func(*args, **kwds)
            set_status(data, status=status.INDEXED)
        else:
            result = self.func(*args)
        
        return result

@StatusUpdate
def indexing_job(data):
    from genetrack.scripts import hdf_loader
    hdf_loader.transform(inpname=data.content.path)
