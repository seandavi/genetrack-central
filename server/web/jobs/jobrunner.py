import time
from genetrack import logger
from server.web import models, status

def get_data(job):
    "Returns a data"
    data_id = job.json.get('data_id')
    if data_id:
        print data_id
        return models.Data.objects.get(id=data_id)
    else:
        return None

def set_error(errmsg, targets):
    "Sets the error status and message on valid targets"
    def set(t):
        t.status = status.ERROR
        t.errors = str(errmsg)
        t.save()
    
    targets = map(set, filter(None, targets))


def execute(sleep=0, limit=1):
    
    # this is used to start multiple jobs with cron (at every minute
    # the
    if sleep:
        time.sleep(sleep)

    # no locking for now, could be a problem
    jobs = models.Job.objects.filter(status=status.WAITING).order_by('id')[0:limit]
    for job in jobs:
        job.status = status.RUNNING
        job.save()
    
    # run the selected jobs        
    for job in jobs:
        jobtype = job.json.get('type')
        data = get_data(job)

        try:
            if jobtype == status.INDEXING_JOB:
                data.status = status.RUNNING
                data.save()
                print "runing the indexing job"
            else:
                raise Exception ("unknown jobtype")
        
        except Exception, exc:
            logger.error(exc)
            set_error(exc, (data, job))

if __name__== '__main__':
    execute()