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
FeatureWidget  = forms.TextInput( attrs={'size': '10', 'id': 'feature'}) 
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

def get_defaults( form ):
    "Extracts the initial values from a form"
    # not sure why this is not offered by Django forms right away
    store = {}
    for name, field in form.fields.items() :
        store[ name ] = field.initial
    return store

class NavbarForm( forms.Form ):
    """
    Encodes the navigation bar
    
    >>> n = NavbarForm(NAVBAR_DEFAULTS)
    >>> n.is_valid()
    True
    """
    move_left  = forms.CharField( widget=ButtonWidget, initial='<< Move left'  , required=False )
    move_right = forms.CharField( widget=ButtonWidget, initial='Move right >>' , required=False )
    zoom_in    = forms.CharField( widget=ButtonWidget, initial='Zoom in +' , required=False )
    zoom_out   = forms.CharField( widget=ButtonWidget, initial='Zoom out -', required=False )

NAVBAR_DEFAULTS = get_defaults( NavbarForm() )

class FitForm( forms.Form ):
    """
    Encodes fitting parameters
    
    >>> f = FitForm()
    >>> f.is_valid()
    False
    >>> f = FitForm(FIT_DEFAULTS)
    >>> f.is_valid()
    True
    """
    use_smoothing = forms.BooleanField( initial=False, required=False )
    sigma = forms.FloatField( initial=20, max_value=1000, min_value=0, widget=ImageWidget )
    smoothing_func = forms.ChoiceField( initial='GK', choices=[ ('GK', 'Gaussian kernel') ] )

FIT_DEFAULTS = get_defaults( FitForm() )

class PeakForm( forms.Form ):
    """
    Displays the navigation bar
    
    >>> p = PeakForm(PEAK_DEFAULTS)
    >>> p.is_valid()
    True
    """
    use_predictor = forms.BooleanField( initial=False, required=False )
    feature_width = forms.IntegerField( initial=147, max_value=2000, min_value=0, widget=ImageWidget )
    minimum_peak = forms.FloatField( initial=2, max_value=1000, min_value=0, widget=ImageWidget )
    pred_func = forms.ChoiceField( initial='FIX', choices=[ ('FIX', 'Fixed width'), ('TRS', 'Above threshold'), ('ALL', 'All maxima') ] )

PEAK_DEFAULTS = get_defaults( PeakForm() )

def make_form( chroms ):
    """
    Form class factory. 
    Creates a custom form bound to the chromosomal labels in the parameters
    Returns a form class that needs to be instantiated.
    
    >>> FormClass = make_form( [ 'chr1'] )
    >>> form = FormClass()
    >>> defaults = get_defaults( form )
    >>> defaults['chrom']
    'chr1'
    """

    chrom_choices  = [ (x,x) for x in chroms ]
    start_chrom = chroms[0]
    
    class SearchForm( forms.Form ):
        """
        The search form that gets displayed on each page
        """
        feature = forms.CharField( widget=FeatureWidget, initial=10000 )
        image_width = forms.IntegerField( initial=5000, max_value=20000, min_value=150, widget=ImageWidget )
        viewport_width = forms.IntegerField( initial=920, max_value=5000, min_value=100, widget=ImageWidget )
        zoom_value = forms.ChoiceField( initial=10000, choices=ZOOM_CHOICES )
        chrom  = forms.ChoiceField( initial=start_chrom , choices=chrom_choices )
        strand = forms.ChoiceField( initial='ALL', choices=[ ('ALL', 'Both strands'), ('SEP', 'Separate strands') ] )

    return SearchForm

# default search form
SEARCH_DEFAULTS = get_defaults( make_form(["chr1"])() )

ALL_DEFAULTS = dict( SEARCH_DEFAULTS )
ALL_DEFAULTS.update( FIT_DEFAULTS )
ALL_DEFAULTS.update( PEAK_DEFAULTS )


def test():
    "Module level testing"
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()