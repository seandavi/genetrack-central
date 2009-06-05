"""
Commonly used constants
"""

MEMBER  = 'member'
MANAGER = 'manager'

#
# data constants
#
DATA_NEW        = 'new'
DATA_RUNNING    = 'running'
DATA_UPLOADING  = 'uploading'
DATA_WAITING    = 'waiting'
DATA_LINEAR     = 'linear'
DATA_INTERVAL   = 'interval'
DATA_ERROR      = 'error'
DATA_UNSUPPORTED = 'unsupported'

# data that can be marked as ready
DATA_READY    = set( [ DATA_LINEAR, DATA_INTERVAL, DATA_UNSUPPORTED, DATA_ERROR, ] )
DATA_VIEWABLE = set( [ DATA_LINEAR, DATA_INTERVAL ]  )

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