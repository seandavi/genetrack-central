import time
from functools import partial
from genetrack import logger
from server.web import models, status
import jobdefs

def get_data(job):
    "Returns a data"
    data_id = job.json.get('data_id')
    if data_id:
        print data_id
        return models.Data.objects.get(id=data_id)
    else:
        return None

def set_status(obj, status, errmsg=''):
    "Sets the status on an object that has status and errors fields."
    obj.status = status
    obj.errors = str(errmsg)
    obj.save()

def set_error(errmsg, targets):
    "Sets the error status and message on valid targets"
    set2 = partial(set_status, status=status.ERROR, errmsg=errmsg)
    targets = map(set2, filter(None, targets))

def execute(sleep=0, limit=1):
    
    # this is used to start multiple jobs with cron (at every minute
    if sleep:
        time.sleep(sleep)

    # no locking for now, could be a problem
    jobs = models.Job.objects.filter(status=status.WAITING).order_by('id')[0:limit]
    for job in jobs:
        set_status(job, status=status.RUNNING)
    
    # run the selected jobs        
    for job in jobs:
        jobtype = job.json.get('type')
        data = get_data(job)
        try:
            if jobtype == status.INDEXING_JOB:
                jobdefs.indexing_job(data=data)
            else:
                raise Exception ("unknown jobtype")
            job.delete()
        except Exception, exc:
            logger.error(exc)
            set_error(exc, (data, job))
        
if __name__== '__main__':
    execute()