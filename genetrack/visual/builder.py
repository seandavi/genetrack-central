"""
Builds a multiplot from a track specification file
"""
import parsing, trackdef
from trackutil import *
import random
from genetrack import logger

class LiveData(object):
    "A data object that returns values when asked for it"
    pass
    
def test_xy(seed):
    "Generate real-looking but randomized dataset"
    random.seed(seed)
    xc = range(0, 2000, 30)
    yc = [ 0 ] * len(xc)
    # fill in some regions with random values, 
    # attempts to emulate read distribution
    func = lambda x: random.randint(1, 20)
    for i in range(0, len(yc)-5, 10):
        yc[i:i+5] = map(func, range(5))
    return (xc, yc)

def populate_preview(json, xscale=(0,2000)):
    "Populates a json datastructure with preview data"
    # mutates elements in place
    for row in json:
        row['xscale'] = xscale
        if row['style'] in parsing.XY_STYLES:
            row['data'] = test_xy(hash(row['data']))
        elif row['style'] == 'EXON':
            row['data'] = [ (1480, 1550, '1'), (1600, 1700, '2'), (1750, 1830, '3'), (1890, 1930, '4') ]
        else:
            row['data'] = [(130, 220, 'A'), (320, 570, 'B'), (1120, 890, 'C'), (1480, 1930, 'D')]
    return json

# drawing functions
DRAW_FUNC = dict(
    BAR=trackdef.draw_bars,
    LINE=trackdef.draw_line,
    ORF=trackdef.draw_arrow,
    ARROW=trackdef.draw_arrow,
    SEGMENT=trackdef.draw_segments,
    EXON=trackdef.draw_segments,
    ZONE=trackdef.draw_zones,
    MARK=trackdef.draw_marks,
    STEP=trackdef.draw_steps,
    AREA=trackdef.draw_area,
    SCATTER=trackdef.draw_scatter,
    READS = trackdef.draw_bars,
)

# sanity check to ensure all the spec functions have callbacks
__style_diffs = parsing.STYLES - set(DRAW_FUNC.keys())
assert not __style_diffs, 'some styles were not defined -> %s' % ', '.join(__style_diffs)

def build_trackdef(json, debug=False):
    "Generates a preview image"
    chart, opts, collect = None, None, []
    
    # collect globals
    collector = []
    for index, row in enumerate(json):

        target = row.get('target')
        style  = row.get('style')
        data   = row.get('data')
        color  = row.get('color', BLACK)
        xychart = style in parsing.XY_STYLES
        newtrack = (target is None) or  (chart is None)
        
        # generate the proper options
        opts = ChartOptions(init=row) if xychart else TrackOptions(init=row)
        
        # reuse last track
        chart = trackdef.Track(options=opts) if newtrack else chart
        draw = DRAW_FUNC[style]
        
        # add global functions to the span
        if target == 'GLOBAL':
            collector.append( (draw, data, opts) )
        
        if chart is None:
            raise Exception('First chart target is set to ')
        
        draw(track=chart, data=data, options=opts)
        
        if newtrack:
            # draw the global targets on new trackdef
            for elem in collector:
                (func, d, o) = elem
                func(track=chart, data=d, options=o)
            collect.append( chart )
            
    # general options
    collect = filter(None, collect)
    m = trackdef.MultiTrack(tracks=collect)
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
    
    
    color=BLACK 50%; style=BAR; data=1; topx=1; tpad=40; grid=no; lw=5; scaling=1; newaxis=0
    color=olive 50%; style=ZONE; data=1; target=global
    color=NAVY; style=STEP; data=1; tpad=0; lw=2; target=last
    color=RED; style=SCATTER; data=1; tpad=0; lw=10;  target=last; spline=1

    #color=ORANGE; style=BAR; data=8946; topx=1; tpad=0; target=global
    
    
    #color=BLUE 10%; style=ORF; data=1; tpad=0;  newaxis=-10; offset=10
    
    
    
    #color=RED; style=SCATTER; data=15664; tpad=0; lw=10;  target=last; spline=1

    color=BLUE 50%; style=SEGMENT; data= 34555;bpad=0; grid=no
    
    color=BLUE 10%; style=EXON; data=1;h=200; label_offset=-15; target=last
    

    color=BLACK 50%; style=AREA; data=1; topx=1; tpad=0; bpad=40; lw=10; topx=0
    color=ORANGE 50%; style=AREA; data=2; target=last
    
    
   
    #color=RED 20%; style=ORF; data= 34555;  offset=2; arrow=10; rotate=-90; lw=50; target=last; show_labels=0; 
    
    #color=ORANGE; style=BAR; data=8946; topx=1; tpad=0
    #color=BLUE 10%; style=LINE; data=15664; tpad=0; target=last
    
    
    #color=GOLD 50%; style=ZONE; data=15664; target=global
    
    
    #color=NAVY; style=BAR; data=8946; tpad=0
    #color=SKY 10%; style=LINE; data=15664; topx=0; target=last; 
    """
    
    json = parsing.parse(text)

    json = populate_preview(json)

    build_trackdef(json, debug=True)



