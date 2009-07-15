"""
Builds a multiplot from a track specification file
"""
import trackspec, tracks
from trackutil import *
import random

class LiveData(object):
    "A data object that returns values when asked for it"
    def bar(self, xvals):
        pass
def test_bar():
    return range(50) + [ random.randint(1,100) for x in range(50) ]
    
def populate(json):
    "Fetches the data and populates the json value"
    # make a copy to avoid possibly mutating a database object
    for row in json:
        if row['glyph'] == 'BAR':
            row['data'] = test_bar()
        else:
            row['data'] = [(10, 20, 'Alpha'), (30, 50, 'Beta'), (100, 80, 'Delta'), (150, 190, 'Gamma')]
            
    return json

def preview(text):
    "Generates a preview image"
    json = trackspec.parse(text)    
    
    json = populate(json)
    chart, collect = None, []
    for row in json:
        target = row.get('target')
        if not target:
            chart = tracks.Track()
            collect.append( chart )
            
    # general options
    m = tracks.MultiTrack(tracks=collect)
    m.show()
    return m
    
def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

    
if __name__ == "__main__":
    test()
    text = """
    color=RED; glyph=BAR; data=8946; row=new;
    color=BLUE; glyph=ORF; data= 34555; row=same
    color=GOLD; glyph=ZONES; data=15664;        
    glyph=AAA; color=#DD0000 10%; data=123
    """
    preview(text)



