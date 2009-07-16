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
    N1, N2 = 50, 50
    y = range(N1) + [ random.randint(1,100) for x in range(N2) ]
    x = range(len(y))
    return (x, y)

T = test_bar()

def populate(json):
    "Fetches the data and populates the json value"
    # make a copy to avoid possibly mutating a database object
    for row in json:
        if row['glyph'] in( 'BAR', 'LINE'):
            row['data'] = T
        else:
            row['data'] = [(10, 20, 'Alpha'), (30, 50, 'Beta'), (100, 80, 'Delta'), (150, 190, 'Gamma')]
            
    return json

XYCHARTS = set(('BAR', 'LINE'))

# drawing functions
DRAW_FUNC = dict(
    BAR=tracks.draw_bars,
    LINE=tracks.draw_line,
    ORF=tracks.draw_arrow,
    SEGMENT=tracks.draw_bars,
    ZONES=tracks.draw_zones,
    MARKS=tracks.draw_marks,
)
def preview(text):
    "Generates a preview image"
    json = trackspec.parse(text)    
    
    json = populate(json)
    chart, opts, collect = None, None, []
    
    # collect globals
    span = []
    for index, row in enumerate(json):

        target = row.get('target')
        glyph  = row.get('glyph')
        data   = row.get('data')
        color  = row.get('color', BLACK)
        xychart = glyph in XYCHARTS
        newtrack = (chart is None) or (target is None)
        
        # generate the proper options
        opts = ChartOptions(init=row) if xychart else TrackOptions(init=row)
        
        # reuse last track
        chart = tracks.Track(options=opts) if newtrack else chart
        draw = DRAW_FUNC[glyph]
        draw(track=chart, data=data, options=opts)
        
        # apply all spanning functions
        for func in span:
            (func, c, d, o) = elem
            func(track=c, data=d, options=o)
        
        # add global functions to the span
        if target == 'global':
            span.append( (draw, chart, data, opts) ) 
        
        if newtrack:   
            collect.append( chart )
            
    # general options
    collect = filter(None, collect)
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
    
    color=BLUE; glyph=ORF; data= 34555; tpad=30; h=200
    color=SPRING_GREEN 50; glyph=ORF; data= 34555; tpad=30; h=200
    
    color=RED; glyph=BAR; data=8946; topx=1; tpad=20
    
    #color=BLUE 10%; glyph=LINE; data=15664; target=same
    #color=GOLD 50%; glyph=ZONES; data=15664; target=global
    
    
    color=NAVY; glyph=BAR; data=8946;
    #color=SKY 10%; glyph=LINE; data=15664; topx=0; target=same; 
    """
    preview(text)



