from genetrack.server.web import status

def detect(data, ext, JobClass ):

    if ext in ['gtrack', ]:
        data.status = status.WAITING               
        json = dict(type=status.INDEXING_JOB, data_id=data.id)
        job  = JobClass(owner=data.owner, name=status.INDEXING_JOB, json=json, status=data.status)
        job.save()
    else:
        data.status = status.STORED

    data.save()

if __name__== '__main__':
    pass