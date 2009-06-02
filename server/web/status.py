"""
Commonly used constants
"""

MEMBER  = 'member'
MANAGER = 'manager'

#
# data constants
#
DATA_NEW      = 'data-new'
DATA_RUNNING  = 'data-running'
DATA_WAITING  = 'data-waiting'
DATA_INDEXED  = 'data-indexed'
DATA_INTERVAL = 'data-interval'
DATA_ERROR    = 'data-error'
DATA_UNSUPPORTED = 'data-unsupported'

# data that can be marked as ready
DATA_READY    = set( [ DATA_INDEXED, DATA_UNSUPPORTED, DATA_ERROR, DATA_INTERVAL] )
DATA_VIEWABLE = set( [ DATA_INDEXED ]  )

#
# job constants
#
INDEXING_JOB = 'Indexing-Job'
SUMMARY_JOB  = 'Summary-Job'
PEAK_PREDICTION_JOB   = 'Peak-Prediction-Job'


DEFAULT_PROJECT_INFO = """
Enter the project info here. 

By adding a special markup you may format your text as *italics* or **bold**.

Here is an example on how to make lists (start each line with the - sign):

- List item 1
- List item 2
"""