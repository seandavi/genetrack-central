"""
Specifies constants used in drawing the charts. 
"""
import os, sys
from genetrack import conf, logger

# arrow polygon heads
ARROW_POLYGON1 = [ -5, 0, 0, 0, 5, -0, 0, 5 ]
ARROW_POLYGON2 = [ -6, 0, 0, 0, 6, -0, 0, 6 ]

# nucleosome specific intervals relative to the start site of the nucleosome
STRIPE_COORDS = [(0, 4), (9, 14), (19, 25), (30, 35), (40, 45), (50, 56), (61, 66), (71, 76), (81, 86), (91, 97), (102, 107), (112, 117), (122, 128), (133, 138), (143, 147)]

# toned colors, chartdirector specific
BLUE, RED, GREEN = 0x0000DD, 0xDD0000, 0x00DD00 
GREY, LIGHT, BLACK = 0xCECECE, 0xEFEFEF, 0x000000
WHITE, PURPLE, ORANGE = 0xFFFFFF, 0x990066, 0xFF3300
TEAL, CRIMSON, GOLD = 0x009999, 0xDC143C,  0xFFD700
NAVY, SIENNA = 0x000080, 0xA0522D 
LIGHT_GREEN, SPRING_GREEN, YELLOW_GREEN = 0x33FF00, 0x00FF7F, 0x9ACD32

# indicates transparent color (chardirector specific)
TRANSPARENT = 4278190080

class Options(object):
    """
    A class that provides attribute based access to a dictionary
    
    >>> p = Options(a=1 ,b=2, c=3)
    >>> (p.a, p.b, p.c)
    (1, 2, 3)
    """
    defaults = dict()
    def __init__(self, init={}, **kwds):
        self.update(self.defaults)
        self.update(init)
        self.update(kwds)

    def update(self, data):
        "Updates the internal dictionary"
        self.__dict__.update(data)

class ChartOptions(Options):
    """
    Represents parameters used to customize a chart. 
    Populates and returns an M{Options} class instance that provides a 
    namespace for chart options. Uses the variable naming convention that 
    M{ChartDirector} internally uses. See the M{ChartDirector}
    docs for reference. 

    The yscale and yscale2 parameters represent dual Y-axes (left and right).

    >>> opts = ChartOptions( xyz=123, h=50 )
    >>> opts.w, opts.h, opts.lw, opts.xyz
    (800, 50, 1, 123)
    """
    defaults = dict( 
        
        # widht, height
        w=800, h=200, 
        
        # padding: top, bottom, right, left
        tpad=20, bpad=20, rpad=60, lpad=60, 
        
        # labels and axis position
        show_labels = True, 
        ylabel  = 'Y-Label', 
        ylabel2 = '',
        xlabel  = 'X-Label',
        legend  = '',
        # location of the X axis
        XAxisOnTop  = 0, 

        # set the default scales
        xscale=[1,100], 
        yscale=[], 
        yscale2=[],
        yaxis2='',
        
        # colors
        color = BLACK,
        hGridColor=-1, vGridColor=GREY,
        fgColor=BLACK, bgColor=WHITE, altBgColor=-1, edgeColor=GREY, 
        XAxisColor=BLACK, YTickColor=BLACK, barColor=BLACK,

        # fontsizes and linewidth
        fontSize=13, 
        fontType="arialbd.ttf",
        lw=1,
        offset=0,
        label_offset = 0,
        # used for for glyph drawing
        arrow_polygon = ARROW_POLYGON2, 
    )
    
class TrackOptions( ChartOptions ):
    """
    Returns the default track options
    >>> opts = TrackOptions( xyz='abc' )
    >>> opts.w, opts.h, opts.lw, opts.xyz
    (800, 60, 12, 'abc')
    """
    custom = dict( 
        lw=12,
        XAxisColor=TRANSPARENT, YTickColor=TRANSPARENT, 
        tpad=0, bpad=1, h=60,
        yscale=[-10, 10],
        xlabel=None
    ) 
    defaults = dict(ChartOptions.defaults) 
    defaults.update(custom)

def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

if __name__ == "__main__":
    test()
