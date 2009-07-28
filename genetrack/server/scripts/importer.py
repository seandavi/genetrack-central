"""
Genetrack file transformer. 

The program may be invoked in multiple ways. As a standalone script::

    python importer

As a python module::

    python -m server.scripts.importer

Or in other python scripts::

>>>
>>> from server.scripts import importer
>>> importer.execute()
>>>

Run the script with no parameters to see the options that it takes.

**Observed runtime**: insertion rate of 6 million lines per minute

"""
import os, sys, csv
from genetrack import logger
from genetrack.server.web import models
from django.conf import settings

def execute(options):
    """
    Creates a transform from a genetrack input file
    """
    data = models.Data.objects.get(id=options.dataid)
    results = models.Result(name=options.name, info=options.info, data=data)
    results.store(content=options.content, image=options.image)

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog -i inputfile"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-d', action="store", 
        dest="dataid", type='int', default=0,
        help="the target data id (required)"
    )

    # setting the input file name
    parser.add_option(
        '-f', action="store", 
        dest="content", type='str', default=None,
        help="the input data"
    )

    # setting the input file name
    parser.add_option(
        '-i', action="store", 
        dest="image", type='str', default=None,
        help="the input image"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    #name
    parser.add_option(
        '--name', action="store", 
        dest="name", type="str", default="No name", 
        help="the imported results name",
    )

    #name
    parser.add_option(
        '--info', action="store", 
        dest="info", type="str", default="No info", 
        help="the imported result information",
    )

    

    options, args = parser.parse_args()

    # set verbosity
    logger.disable( options.verbosity )

    # missing input file name
    if not (options.content or options.image):
        parser.print_help()
    else:
        execute(options=options)
