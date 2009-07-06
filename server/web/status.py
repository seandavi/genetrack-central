"""
Commonly used constants
"""

MEMBER  = u'member'
MANAGER = u'manager'

#
# data constants
#
NEW        = u'new'
RUNNING    = u'running'
UPLOADING  = u'uploading'
WAITING    = u'waiting'
INDEXED    = u'indexed'
INTERVAL   = u'interval'
ERROR      = u'joberror'
STORED     = u'stored'

#
# data that can be marked as ready
#
INPROGRESS = set( [NEW, RUNNING, UPLOADING, WAITING] )
READY = set( [ INDEXED, INTERVAL, STORED, ERROR, ] )
VIEWABLE = set( [ INDEXED, INTERVAL ]  )

#
# all possible states
#
ALL = INPROGRESS | READY

#
# job constants
#
INDEXING_JOB = u'Indexing-Job'
SUMMARY_JOB  = u'Summary-Job'
PEAK_PREDICTION_JOB   = u'Peak-Prediction-Job'


DEFAULT_PROJECT_INFO = """
Project managers may change the project info with the Edit link.

By adding a special markup text may be formatted as *italics* or **bold**.

Here is an example on how to make lists:

- List item 1
- List item 2
"""