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
    
class Track(TrackBase):
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
# some code duplication accross drawing functions, mostly to speed it up

def unwind(data):
    "Unwinds a data into a segment array"
    fast = []
    map(fast.extend, data)
    labels = fast[2::3]
    fast[2::3] = [ NOVALUE ] * len(labels)
    return fast, labels

def draw_bars(track, data, options=None):
    "Draws bars data=(x,y)"
    o = options or track.o
    x, y = data
    layer = track.c.addBarLayer(y, color=o.color, name=o.legend)
    layer.setBarWidth(o.lw)
    layer.setBorderColor(o.color)
    
    # select axes
    axis = track.c.yAxis2() if o.yaxis2 else track.c.yAxis()
    layer.setUseYAxis(axis)
    layer.setXData(x)
    track.add_legend(o.legend)

def draw_line(track, data, options=None):
    "Draws lines data=(x,y)"
    o = options or track.o
    x, y = data
    layer = track.c.addLineLayer(y, color=o.color, name=o.legend)
    layer.setLineWidth(o.lw)
    
    # select axes
    axis = track.c.yAxis2() if o.yaxis2 else track.c.yAxis()
    layer.setUseYAxis(axis)
    layer.setXData(x)
    track.add_legend(o.legend)
    
def draw_segments(track, data, options=None):
    """
    Draws a seqment from a list of data in the form
    (start, end, label)
    """
        
    o = options or track.o
    fast, labels  = unwind(data)
    y = [ options.offset ] * len(fast) # vertical coordinate
    
    layer = track.c.addLineLayer(y , color=o.color, name=o.legend)
    layer.setLineWidth(o.lw)
    layer.setXData(fast)
    
    # drawing the labels
    if options.show_labels:
        midpoints = [ (e[0] + e[1])/2.0 for e in data ]
        draw_labels(track=track, x=midpoints, y=y, labels=labels, options=o)

def draw_arrow(track, data, options=None):
    """
    Draws a seqment from a list of data in the form
    (start, end, label)
    """
    o = options or track.o
    fast, labels  = unwind(data)
    
    # the way this works is that uses a reference point to draw an arrow
    # of given lenght then rotates it into the right direction, see ChartDirector
    # VectorLayer for more info
    x  = fast[1::3] # reference on x
    y  = [ options.offset ] * len(data) # vertical coordinate
    rc = [ e[1] - e[0] for e in data ] # lenghts on x
    ac = [ 90 ] * len(data) # rotation angles
    
    # create the vector layer
    layer = track.c.addVectorLayer(x, y, rc, ac, XAxisScale, o.color, o.legend)
    layer.setArrowAlignment(TOPCENTER)
    layer.setArrowHead2(o.arrow_polygon)
    layer.setArrowHead(o.lw)
    layer.setLineWidth(o.lw)
    layer.setXData(x)
    
    # drawing the labels
    if options.show_labels:
        midpoints = [ (e[0] + e[1])/2.0 for e in data ]
        draw_labels(track=track, x=midpoints, y=y, labels=labels, options=o)

def draw_labels(track, x, y, labels, options):
    "Draws labels at an offset"
    o = options
    scatter = track.c.addScatterLayer(x, y, "", CIRCLESYMBOL, 0, 0xff3333, 0xff3333)
    scatter.addExtraField(labels)
    scatter.setDataLabelFormat("{field0}")
    textbox = scatter.setDataLabelStyle(o.fontType, o.fontSize, o.color)
    textbox.setAlignment(CENTER)
    if o.label_offset:
        textbox.setPos(0, -o.label_offset )
    else:
        textbox.setPos(0, -(o.lw + 2))
        

class TrackManager(object):
    pass
        
def test():
    from server.web import models
    data_id = 1
    data_path = models.Data.objects.get(id=data_id).content.path
    
    init= dict(color=RED, glyph='AUTO', data=data_id, data_path=data_path, xscale=(-10,110) )

    # general options
    opts = ChartOptions(init=init, ylabel='Bars', legend='Bar Legend', ylabel2="Line" )
    
    y = range(50)+range(50, 1,-1)
    x = range(len(y))
    
    data = ( x, y )
    
    track = Track(opts)
        
    arropts = ChartOptions(yaxis2=True, legend='Arrows', color=NAVY, offset=40, lw=10)
    arrdata = ( (10, 20, 'A'), (30, 50, 'B'), (100, 80, 'C') )
    draw_arrow(track=track, data=arrdata, options=arropts)
    
    
    segopts = ChartOptions(yaxis2=True, legend='Segments', color=0xAA0D2940, offset=20, lw=15, label_offset=-15)
    segdata = ( (10, 20, 'A'), (30, 50, 'B'), (100, 80, 'C') )
    draw_segments(track=track, data=segdata, options=segopts)
    
    baropts = ChartOptions(color=RED, legend='Bar Legend', ylabel2="Line" )
    draw_bars(track=track, data=data, options=baropts)
    
    lineopts = ChartOptions(yaxis2=True, legend='Line Legend', color=BLUE)
    draw_line(track=track, data=data, options=lineopts)
    
    
    
    
    
    track.show()
    
if __name__ == '__main__':
    test()