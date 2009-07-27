"""
Populates the active server instance with various test datasets
"""
import random
from genetrack import conf, logger
from genetrack.server.web.models import *
from genetrack.server.web import authorize, status

from django.contrib.auth.models import User

# the user used to populate the data
user = User.objects.get(email='admin')

# potential project names
project_names = [
    'Mouse project HBB %s', 
    'Yeast mutant RAV %s', 
    'Yeast mutant RAP2 %s', 
    'Fly data DR2%s', 
    'Human HELA 16 %s',
    'Human HELA 17 %s',
]

# generates projects

def generate(n=5):

    projects = []
    for i in range(1, n):
        name = random.choice(project_names) % i
        info = 'some info=%s' % i
        project = authorize.create_project(user=user, name=name, info=info)
        projects.append(project)
        logger.info('creating %s' % name)

    # data names
    data_names = ( 'short-good-input.gtrack', 'short-data.bed')
    
    # visualization names
    track_names = ( 'differential expression', 'HELA subtract', 'Default track')
    

    # a subset of projects get data, visualization and results added to them
    subset = projects[-1:]
    for project in subset:
        
        # create some tracks for this project
        for tname in track_names:
            json = dict()
            track = authorize.create_track(user=user, pid=project.id, name=tname, json=json )
            logger.info('creating track %s' % track.name)
        
        assert (project.track_count(), len(track_names))

        # upload some data names        
        for name in data_names:
            logger.info('uploading data %s' % name)
            stream = File( open(conf.testdata(name)) )
            data = authorize.create_data(user=user, pid=project.id, stream=stream, name=name, info='test data')
            
            # create some  results
            logger.info('adding results content and image')
            stream1 = File( open(conf.testdata('short-results.txt')) )
            image1  = File( open(conf.testdata('readcounts.png'),'rb') )
            result1 = authorize.create_result( user=user, data=data, content=stream1, image=image1)

            image2  = File( open(conf.testdata('shift.png'), 'rb') )
            result2 = authorize.create_result( user=user, data=data, content=None, image=image2)
                
if __name__ == '__main__':
    generate()

