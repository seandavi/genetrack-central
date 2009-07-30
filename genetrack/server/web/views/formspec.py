"""
Contains form specification.

Due to the dynamic content that needs to be displayed some 
form specficators/validators need to be genereated on the fly.
"""

from itertools import starmap
from django import forms
from genetrack import logger, util

# needs a custom class to create a submit widget
class SubmitWidget( forms.widgets.Input) :
    input_type = 'submit'

# custom widgets
ButtonWidget   = SubmitWidget( attrs={'class': 'nav_btn'} ) 
LocusWidget    = forms.TextInput( attrs={'size': '10', 'id': 'locus'}) 
ImageWidget    = forms.TextInput( attrs={'size': '4'}) 

# generate zoom levels with user friendly numbers
ZOOM_LEVELS  = "50 100 250 500 1000 2500 5000 10000 25000 50000 100000 250000 500000 1000000".split()
ZOOM_CHOICES = map(lambda x: (x, util.commify(x) ), ZOOM_LEVELS)

def zoom_change(value, step):
    """
    Gets the next zoom level, either up or down

    >>> levels = [(100, 1), (100, -1), (1000000, 1)]
    >>> it = starmap( zoom_change, levels )
    >>> list(it)
    [250, 50, 1000000]
    """
    global ZOOM_LEVELS
    try:
        index = ZOOM_LEVELS.index( str(value) )
        index += step
        index = index if index>0 else 0
        return int(ZOOM_LEVELS[index])
    except (ValueError, IndexError):
        return value

def zoom_in(value):
    return zoom_change(value, -1)

def zoom_out(value):
    return zoom_change(value, +1)

def test():
    "Module level testing"
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()