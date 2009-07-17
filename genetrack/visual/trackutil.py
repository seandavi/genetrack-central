"""
Specifies constants and utilities used in drawing the charts. 
"""
import os, sys

# arrow polygon heads
ARROW_POLYGON1 = [ -5, 0, 0, 0, 5, -0, 0, 5 ]
ARROW_POLYGON2 = [ -6, 0, 0, 0, 6, -0, 0, 6 ]

# various arrowhead polygons
ARROWS = {}
for i in range(1, 30):
    ARROWS[str(i)] = [ -i, 0, 0, 0, i, -0, 0, i ]

_VALID_GLYPHS = set( "AUTO BAR LINE ORF INTERVAL BOOKMARK" )

_VALID_COLORS = dict(
    BLUE=0x0000DD,  RED=0xDD0000,     GREEN =0x00DD00,
    GREY=0xCECECE,  LIGHT=0xEFEFEF,   BLACK=0x000000,
    WHITE=0xFFFFFF, PURPLE=0x990066,  ORANGE=0xFF3300, 
    TEAL= 0x009999, CRIMSON=0xDC143C, GOLD=0xFFD700,
    NAVY=0x000080,  SIENNA=0xA0522D,  LIGHT_GREEN=0x33FF00, 
    SPRING_GREEN=0x00FF7F, YELLOW_GREEN=0x9ACD32,
    WHEAT=0xD8D8BF, TOMATO=0xFF6347, SKY=0x3299CC, ROYAL_BLUE=0x4169E1,
    SILVER=0xC0C0C0, ORCHID=0xDB70DB, HOTPINK=0xFF69B4, AQUAMARINE=0x70DB93,
    VIOLET=0x4F2F4F, OLIVE=0x808000, PERU=0xCD853F, SLATE=0x6A5ACD,

    # indicates transparent color (chardirector specific)
    TRANSPARENT = 4278190080
)

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

    def __contains__(self, value):
        return value in self.__dict__
    
    def __getitem__(self, key):
        return self.__dict__[key]
        
# loads valid colors into the namespace
COLORS = Options(init=_VALID_COLORS)

TRANSPARENT = COLORS.TRANSPARENT
RED   = COLORS.RED
BLACK = COLORS.BLACK
WHITE = COLORS.WHITE
GREY  = COLORS.GREY

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
        tpad=10, bpad=0, rpad=60, lpad=60, 
        
        # labels and axis position
        show_labels = True, 
        ylabel  = '', 
        ylabel2 = '',
        xlabel  = '',
        legend  = '',
        # location of the X axis
        topx = 1, 

        # set the default scales
        xscale=[1,200], 
        yscale=[], 
        yscale2=[],
        yaxis2='',
        
        # colors
        color = BLACK,
        bgcolor=WHITE,
        grid = 1,
        hGridColor=-1, vGridColor=GREY,
        altBgColor=-1, edgeColor=GREY, 
        XAxisColor=BLACK, YTickColor=BLACK, barColor=BLACK,

        # fontsizes and linewidth
        fontSize=13, 
        fontType="arialbd.ttf",
        lw=1,
        offset=0,
        rotate=0,
        label_offset = 0,
        # used for for glyph drawing
        arrow = ARROWS['5'],
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
        tpad=0, bpad=0, h=60,
        yscale=[-10, 10],
        xlabel=None
    ) 
    defaults = dict(ChartOptions.defaults) 
    defaults.update(custom)

def split(text, sep):
    "Split and strip whitespace in one call"
    return map(strip, text.split(sep))
    
def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

if __name__ == "__main__":
    test()
