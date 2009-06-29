"""
Commonly used constants
"""

MEMBER  = 'member'
MANAGER = 'manager'

#
# data constants
#
NEW        = 'new'
RUNNING    = 'running'
UPLOADING  = 'uploading'
WAITING    = 'waiting'
INDEXED    = 'indexed'
INTERVAL   = 'interval'
ERROR      = 'joberror'
STORED     = 'stored'

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
INDEXING_JOB = 'Indexing-Job'
SUMMARY_JOB  = 'Summary-Job'
PEAK_PREDICTION_JOB   = 'Peak-Prediction-Job'


DEFAULT_PROJECT_INFO = """
Project managers may change the project info with the Edit link.

By adding a special markup text may be formatted as *italics* or **bold**.

Here is an example on how to make lists:

- List item 1
- List item 2
"""