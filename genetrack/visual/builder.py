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
    N1, N2 = 100, 100
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
            row['data'] = [(13, 22, 'Alpha'), (32, 57, 'Beta'), (112, 89, 'Delta'), (157, 193, 'Gamma')]
            
    return json

XYCHARTS = set(('BAR', 'LINE'))

# drawing functions
DRAW_FUNC = dict(
    BAR=tracks.draw_bars,
    LINE=tracks.draw_line,
    ORF=tracks.draw_arrow,
    SEGMENT=tracks.draw_segments,
    ZONES=tracks.draw_zones,
    MARKS=tracks.draw_marks,
)
def preview(text):
    "Generates a preview image"
    json = trackspec.parse(text)    
    
    json = populate(json)
    chart, opts, collect = None, None, []
    
    # collect globals
    collector = []
    for index, row in enumerate(json):

        target = row.get('target')
        glyph  = row.get('glyph')
        data   = row.get('data')
        color  = row.get('color', BLACK)
        xychart = glyph in XYCHARTS
        newtrack = (target is None)
        
        # generate the proper options
        opts = ChartOptions(init=row) if xychart else TrackOptions(init=row)
        
        # reuse last track
        chart = tracks.Track(options=opts) if newtrack else chart
        draw = DRAW_FUNC[glyph]
        
        # add global functions to the span
        if target == 'GLOBAL':
            collector.append( (draw, data, opts) )
        else:
            assert chart is not None, 'Chart may not be none %s' % row
            draw(track=chart, data=data, options=opts)
            
        if newtrack:
            # draw global targets
            for elem in collector:
                (func, d, o) = elem
                func(track=chart, data=d, options=o)
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
    
    #color=BLUE; glyph=ORF; data= 34555; tpad=0; h=200; arrow=10; lw=10
    #color=SPRING_GREEN 50; glyph=ORF; data= 34555; offset=-1; target=last; 
    #color=LIGHT_GREEN 80; glyph=ZONES; data= 34555; offset=2; target=global
    #color=PERU; glyph=ORF; data= 34555
    
    color=olive 50%; glyph=ZONES; data= 34555; target=global
    
    #color=ORANGE; glyph=BAR; data=8946; topx=1; tpad=0; target=global
    
    color=NAVY; glyph=BAR; data=8946; topx=1; tpad=40; grid=no
    
    color=RED; glyph=LINE; data=15664; tpad=0; target=last; lw=10

    color=BLUE 20%; glyph=SEGMENT; data= 34555;bpad=1; grid=no
    
    color=BLUE 20%; glyph=SEGMENT; data= 34555;h=200; offset=-1; label_offset=-15; legend=Orf1 tracks for the win; bgcolor=GREY 80%; grid=no
    
    color=RED 20%; glyph=ORF; data= 34555;  offset=2; arrow=10; rotate=-90; lw=50; target=last; show_labels=0; 
    
    #color=ORANGE; glyph=BAR; data=8946; topx=1; tpad=0
    #color=BLUE 10%; glyph=LINE; data=15664; tpad=0; target=last
    
    
    #color=GOLD 50%; glyph=ZONES; data=15664; target=global
    
    
    #color=NAVY; glyph=BAR; data=8946; tpad=0
    #color=SKY 10%; glyph=LINE; data=15664; topx=0; target=last; 
    """
    preview(text)



