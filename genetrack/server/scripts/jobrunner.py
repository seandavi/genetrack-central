import time
from functools import partial
from genetrack import logger
from genetrack.server.web import models, status
from genetrack.server.web.jobs import jobdefs

def get_data(job, attr='data_id'):
    "Returns a data"
    data_id = job.json.get(attr)
    if data_id:
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
    targets = filter(None, targets) # keep nonempty targets
    for target in targets:
        set_status(obj=target, status=status.ERROR, errmsg=errmsg)

def execute(limit=1):
    """
    Executes a job
    """

    # no locking here for now, TODO
    jobs = models.Job.objects.filter(status=status.WAITING).order_by('id')[0:limit]
    for job in jobs:
        #logger.info( 'executing %s' % job)
        set_status(job, status=status.RUNNING)
    else:
        logger.info('no jobs are waiting')

    # run the selected jobs        
    for job in jobs:
        logger.info( 'executing %s' % job)
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

    usage = "usage: %prog [ --server ] [ --delay 2 ]"

    parser = logger.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '--delay', action="store", 
        dest="delay", type='int', default=0,
        help="delay running for these many seconds"
    )

    # setting the input file name
    parser.add_option(
        '--limit', action="store", 
        dest="limit", type='int', default=1,
        help="how many jobs to run in parallel"
    )

    # flushes all content away, drops all database content!
    parser.add_option(
        '--server', action="store_true", 
        dest="server", default=False, 
        help="runs as a server and invokes the jobrunner at every delay seconds",
    )

    # parse the argument list
    options, args = parser.parse_args()

    logger.disable(options.verbosity)

    # missing file names
    if options.server and not options.delay:
        parser.print_help()
    else:
        if options.server:
            logger.info('server mode, delay=%ss' % options.delay)
        while 1:
            # this is used to start multiple jobs with cron (at every minute but
            # having them actually start up at smaller increments
            time.sleep(options.delay)
            execute(limit=options.limit)
            if not options.server:
                break
            else:
                logger.debug( 'jobserver waiting %ss' % options.delay)