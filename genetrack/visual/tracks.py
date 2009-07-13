"""
Track specification.
"""

# lots of constants and other names
from itertools import *
from chartutil import *
from genetrack import logger

class TrackBase(object):
    """
    Contains the functionality that all charts must have. 
    This is an abstract class that cannot be instantiated.    
    """
    def __init__(self, options):
        """
        Requires an options parameter must be created with the L{ChartOptions} 
        function.  
        """
        self.o, self.c = options, None
        
        # hopefull this will permit easier backend changes
        self.init_chart()
        self.init_area()
        self.init_axes()
        self.init_finalize()
    
class XYTrack(TrackBase):
    """
    Representation of a track
    """
    def init_finalize(self):
        "Called last after all other intialization steps have completed"
        # used mainly in subclasses
    
    def init_chart(self):
        "Initializes the main chart"
        self.c = pychartdir.XYChart(self.o.w, self.o.h)
        self.c.setClipping()
        
    def init_area(self):
        """
        Initializes the plot boundaries that the chart will be drawn upon.

        The drawing area will be:
        
            - heigh minus top + bottom padding, 
            - and width minus left + right padding.
        """
        o = self.o
        h = o.h - o.tpad - o.bpad
        w = o.w - o.lpad - o.rpad
        self.area = self.c.setPlotArea(o.lpad, o.tpad, w, h, o.bgColor, o.altBgColor, o.edgeColor, o.hGridColor, o.vGridColor)

    def init_axes(self):
        """
        Initializes the axes, margins, tick densities
        
        Inward ticks by default, vertical gridlines for evey X tick
        """
        # a shortcut
        o = self.o
        
        # apply xscale on the bottom
        if o.xscale:
            # the xscale is a tuple (lo, hi)
            self.c.xAxis().setLinearScale(*o.xscale)
            self.c.xAxis().setIndent(0) # this fixes extra width for barlayer
            self.c.xAxis().setLabelStep(1000)

        # apply vertical yscale on the left
        if o.yscale:
            self.c.yAxis().setLinearScale(*o.yscale)
            self.c.yAxis().setRounding(False, False);
        
        # apply a second (dual) y scale (on the right)
        if o.yscale2:
            self.c.yAxis2().setLinearScale(*o.yscale2)
            self.c.yAxis2().setRounding(False, False);
        
        # set label, font and tick density for both y axes
        hsize = o.fontSize/2
        for axis in [ self.c.yAxis(), self.c.yAxis2() ]:
            axis.setMargin(hsize, hsize)
            axis.setTickDensity(o.h/10) 
            axis.setLabelStyle(o.fontType, o.fontSize)
            axis.setTickLength(-5)
            axis.setColors(GREY, o.YTickColor, BLACK, BLACK)

        # setting the titles
        self.c.yAxis().setTitle(o.ylabel, '', o.fontSize)
        self.c.yAxis2().setTitle(o.ylabel2, '', o.fontSize).setFontAngle(270)

        # setting up the x-axis
        self.c.xAxis().setAutoScale(0, 0, 0)
        self.c.xAxis().setRounding(False, False);
        self.c.xAxis().setLabelStyle(o.fontType, o.fontSize)
        self.c.xAxis().setTickDensity(o.w/20)
        self.c.xAxis().setTickLength(-5)
        self.c.xAxis().setColors(GREY, o.XAxisColor, BLACK, TRANSPARENT)
        self.c.setXAxisOnTop(o.XAxisOnTop)
        
    def show(self):
        "Draw itself on the screen requires PIL"
        show_plot(self.c)

    def add_legend(self, legend):
        "Adds a legend to the chart."
        if legend:
            o = self.o
            legend = self.c.addLegend(o.lpad, o.tpad, 0, None, o.fontSize)
            legend.setBackground(TRANSPARENT)
            legend.setFontSize(o.fontSize)

# Drawing functions take indentical parameters and operate on a data object
# that have x,y attributes (labels for seqments)
#
# some code duplication accross drawing functions, 
def draw_bars(track, data, options=None):
    "Draws bars data.y vs data.x"
    o = options or track.o
    layer = track.c.addBarLayer(data.y, color=o.color, name=o.legend)
    layer.setBarWidth(o.lw)
    layer.setBorderColor(o.color)
    
    # switch axes
    axis = track.c.yAxis2() if o.yaxis2 else track.c.yAxis()
        
    layer.setUseYAxis(axis)
    layer.setXData(data.x)
    track.add_legend(o.legend)

def draw_line(track, data, options=None):
    "Draws lines data.y vs data.x"
    o = options or track.o
    layer = track.c.addLineLayer(data.y, color=o.color, name=o.legend)
    layer.setLineWidth(o.lw)
    
    # switch axes
    axis = track.c.yAxis2() if o.yaxis2 else track.c.yAxis()
        
    layer.setUseYAxis(axis)
    layer.setXData(data.x)
    track.add_legend(o.legend)

def unwind(data):
    "Unwinds a data into a segment array"
    fast = []
    map(fast.extend, data)
    labels = fast[2::3]
    fast[2::3] = [ NOVALUE ] * len(labels)
    return fast, labels
    
def draw_segments(track, data, options=None):
    """
    Draws a seqment from a list of data in the form
    (start, end, label)
    """
        
    o = options or track.o
    fast, labels  = unwind(data)
    y = [ options.offset ] * (3*len(fast))
    
    layer = track.c.addLineLayer(y , color=o.color, name=o.legend)
    layer.setLineWidth(o.lw)
    layer.setXData(fast)
    
class TrackManager(object):
    pass
        
def test():
    from server.web import models
    data_id = 1
    data_path = models.Data.objects.get(id=data_id).content.path
    
    init= dict(color=RED, glyph='AUTO', data=data_id, data_path=data_path, xscale=(0,100) )

    # general options
    opts = ChartOptions(init=init, ylabel='Bars', legend='Bar Legend', ylabel2="Line" )
    
    y = range(50)+range(50, 1,-1)
    x = range(len(y))
    
    data = Options( x=x, y=y )
    
    track = XYTrack(opts)
    baropts = ChartOptions(color=RED, legend='Bar Legend', ylabel2="Line" )
    draw_bars(track=track, data=data, options=baropts)
    
    lineopts = ChartOptions(yaxis2=True, legend='Line Legend', color=BLUE)
    draw_line(track=track, data=data, options=lineopts)
    
    segopts = ChartOptions(yaxis2=True, legend='Segments', color=GOLD, offset=10, lw=10)
    
    data = ( (10, 20, 'A'), (30, 50, 'B'), (80, 100), 'C' )
    draw_segments(track=track, data=data, options=segopts)
    
    
    track.show()
    
if __name__ == '__main__':
    test()