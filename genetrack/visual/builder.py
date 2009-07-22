"""
Builds a multiplot from a track specification file
"""
import trackspec, tracks
from trackutil import *
import random

class LiveData(object):
    "A data object that returns values when asked for it"
    pass

class PreviewData(LiveData):

    def text_xy(self, lo, hi, skip=10):
        xc = xrange(lo, hi, skip)
        yc = [ 0 ] * len(xc)
        # fill in some regions with random values, 
        # attempts to emulate read distribution
        func = lambda x: random.randint(1, 20)
        for i in range(0, len(yc)-5, 20):
            yc[i:i+5] = map(func, range(5))
        return (xc, yc)

    
def test_xy(seed):
    random.seed(seed)
    xc = range(0, 1000, 5)
    yc = [ 0 ] * len(xc)
    # fill in some regions with random values, 
    # attempts to emulate read distribution
    func = lambda x: random.randint(1, 20)
    for i in range(0, len(yc)-5, 10):
        yc[i:i+5] = map(func, range(5))
    print xc
    print yc
    return (xc, yc)

def populate_preview(json):
    "Fetches the data and populates the json value"
    # make a copy to avoid possibly mutating a database object
    for row in json:
        if row['style'] in trackspec.XY_STYLES:
            row['data'] = test_xy(hash(row['data']))
        elif row['style'] == 'EXON':
            row['data'] = [ (148, 155, '1'), (160, 170, '2'), (175, 183, '3'), (189, 193, '4') ]
        else:
            row['data'] = [(13, 22, 'Alpha'), (32, 57, 'Beta'), (112, 89, 'Delta'), (148, 193, 'Gamma')]
            
    return json

# drawing functions
DRAW_FUNC = dict(
    BAR=tracks.draw_bars,
    LINE=tracks.draw_line,
    ORF=tracks.draw_arrow,
    ARROW=tracks.draw_arrow,
    SEGMENT=tracks.draw_segments,
    EXON=tracks.draw_segments,
    ZONE=tracks.draw_zones,
    MARK=tracks.draw_marks,
    COVERAGE=tracks.draw_steps,
    SCATTER=tracks.draw_scatter,
)

def build_tracks(json, debug=None):
    "Generates a preview image"
        
    
    
    chart, opts, collect = None, None, []
    
    # collect globals
    collector = []
    for index, row in enumerate(json):

        target = row.get('target')
        style  = row.get('style')
        data   = row.get('data')
        color  = row.get('color', BLACK)
        xychart = style in trackspec.XY_STYLES
        newtrack = (target is None)
        
        # generate the proper options
        opts = ChartOptions(init=row) if xychart else TrackOptions(init=row)
        
        # reuse last track
        chart = tracks.Track(options=opts) if newtrack else chart
        draw = DRAW_FUNC[style]
        
        # add global functions to the span
        if target == 'GLOBAL':
            collector.append( (draw, data, opts) )
        
        if chart is None:
            print 'Invalid chart order, empty chart'
            continue
        
        
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
    if debug:
        m.show()
    return m
    
def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )
    
if __name__ == "__main__":
    test()
    text = """
    
    #color=BLUE; style=ORF; data= 34555; tpad=0; h=200; arrow=10; lw=10
    #color=SPRING_GREEN 50; style=ORF; data= 34555; offset=-1; target=last; 
    #color=LIGHT_GREEN 80; style=ZONES; data= 34555; offset=2; target=global
    #color=PERU; style=ORF; data= 34555
    
    color=olive 50%; style=ZONE; data=1; target=global
    color=BLACK 50%; style=BAR; data=1; topx=1; tpad=40; grid=no; lw=10; scaling=1; newaxis=0
    color=NAVY; style=COVERAGE; data=1; tpad=0; lw=2; target=last
    color=RED; style=SCATTER; data=1; tpad=0; lw=10;  target=last; spline=1

    #color=ORANGE; style=BAR; data=8946; topx=1; tpad=0; target=global
    
   
    
    #color=BLUE 10%; style=ORF; data=1; tpad=0; target=last; newaxis=-10; offset=10
    
    
    
    #color=RED; style=SCATTER; data=15664; tpad=0; lw=10;  target=last; spline=1

    #color=BLUE 20%; style=SEGMENT; data= 34555;bpad=1; grid=no
    
    #color=BLUE 20%; style=SEGMENT; data=1;h=200; offset=-1; label_offset=-15; legend=Orf1 tracks for the win; bgcolor=GREY 80%; grid=no
    
    #color=RED 20%; style=ORF; data= 34555;  offset=2; arrow=10; rotate=-90; lw=50; target=last; show_labels=0; 
    
    #color=ORANGE; style=BAR; data=8946; topx=1; tpad=0
    #color=BLUE 10%; style=LINE; data=15664; tpad=0; target=last
    
    
    #color=GOLD 50%; style=ZONE; data=15664; target=global
    
    
    #color=NAVY; style=BAR; data=8946; tpad=0
    #color=SKY 10%; style=LINE; data=15664; topx=0; target=last; 
    """
    
    json = trackspec.parse(text)

    json = populate_preview(json)

    build_tracks(json, debug=True)



