"""
Track specification using ChartDirector. 
"""

# lots of constants and other names
from itertools import *
from trackdefs import *
from genetrack import logger
from StringIO import StringIO

import pychartdir
# load and set the chartdirector license
CHARTDIRECTOR_LICENSE = os.getenv('CHARTDIRECTOR_LICENSE', '')
if CHARTDIRECTOR_LICENSE:
    pychartdir.setLicenseCode( CHARTDIRECTOR_LICENSE ) 
else:
    logger.warn('chartdirector license not found')
    
# a few handy constants
TRANSPARENT  = pychartdir.Transparent
TOPCENTER    = pychartdir.TopCenter
NOVALUE      = pychartdir.NoValue
CIRCLESYMBOL = pychartdir.CircleSymbol
CROSS        = pychartdir.CrossShape(0.1)
CENTER       = pychartdir.Center
PNG          = pychartdir.PNG

def save(chart, fname):
    "Saves a chart to a file."
    chart.makeChart(fname)

def show(chart):
    """
    Helper class that displays chart image in a Tk window. 
    Clicking on the image quits the application. Requires the PIL library.
    """
    import Tkinter
    from PIL import ImageTk, Image

    output = StringIO()
    output.write( chart.makeChart2( PNG ) )
    output.seek(0) # rewind
    root  = Tkinter.Tk()
    image = ImageTk.PhotoImage( image=Image.open( output ) )
    Tkinter.Button(image=image, command=root.quit).pack()
    root.mainloop()
    
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
        self.h = o.h - o.tpad - o.bpad
        self.w = o.w - o.lpad - o.rpad
        self.area = self.c.setPlotArea(o.lpad, o.tpad, self.w, self.h, o.bgColor, o.altBgColor, o.edgeColor, o.hGridColor, o.vGridColor)

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
        show(self.c)

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

def unwind_segments(data):
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
    fast, labels  = unwind_segments(data)
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
    fast, labels  = unwind_segments(data)
    
    # the way this works is that uses a reference point to draw an arrow
    # of given lenght then rotates it into the right direction, see ChartDirector
    # VectorLayer for more info
    x  = fast[1::3] # reference on x
    y  = [ options.offset ] * len(data) # vertical coordinate
    rc = [ e[1] - e[0] for e in data ] # lenghts on x
    ac = [ 90 ] * len(data) # rotation angles
    
    # create the vector layer
    layer = track.c.addVectorLayer(x, y, rc, ac, pychartdir.XAxisScale, o.color, o.legend)
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
    "Draws labels the x,y coordinates"
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
        
def draw_zones(track, data, options):
    "Shades the background"
    for x in data:
        track.c.xAxis().addZone(x[0], x[1], options.color);
    
def draw_marks(track, data, options):
    "Draws marks"
    for x in data:
        track.c.xAxis().addMark(x, options.color);

class MultiTrack(object):
    "Represents multiple tracks merged into a single image"
    def __init__(self, options, tracks=[]):
        self.o = options
        self.tracks = []
        self.w = self.o.lpad + self.o.w + self.o.rpad
        self.h = self.o.tpad + sum([ t.o.h for t in tracks ]) + self.o.bpad
        self.c = pychartdir.MultiChart( self.w, self.h)    

        # add each track to the multichart
        ypos = self.o.tpad
        for track in tracks:
            self.c.addChart(self.o.lpad, ypos-20, track.c)
            ypos += track.o.h
        
    def draw(self):
        pass
    
    def show(self):
        "Draw itself on the screen requires PIL"
        show(self.c)   
        
def test():
    from server.web import models
    data_id = 1
    data_path = models.Data.objects.get(id=data_id).content.path
    
    init= dict(color=RED, glyph='AUTO', data=data_id, data_path=data_path, xscale=(-10,110) )

    # general options
    opts = ChartOptions(init=init, ylabel='Bars', legend='Bar Legend', ylabel2="Line", tpad=20 )
    
    y = range(50)+range(50, 1,-1)
    x = range(len(y))
    
    data = ( x, y )
    
    opts1 = ChartOptions(init=init, ylabel='Bars', ylabel2="Line", bpad=1, tpad=20, XAxisOnTop=1 )
    track1 = Track(opts1)
    
    opts2 = TrackOptions(init=init, ylabel='', tpad=0 )
    track2 = Track(opts2)
    
    opts3 = TrackOptions(init=init, ylabel='', tpad=0 )
    track3 = Track(opts3)
    
    arropts = ChartOptions(yaxis2=True, legend='Arrows', color=NAVY, offset=0, lw=10)
    arrdata = ( (10, 20, 'A'), (30, 50, 'B'), (100, 80, 'C') )
    draw_arrow(track=track2, data=arrdata, options=arropts)
    draw_arrow(track=track3, data=arrdata, options=arropts)
    
    segopts = ChartOptions(yaxis2=True, legend='Segments', color=0xAA0D2940, offset=20, lw=15, label_offset=-15)
    segdata = ( (10, 20, 'A'), (30, 50, 'B'), (100, 80, 'C') )
    
    
    baropts = ChartOptions(color=RED, legend='Bar Legend', ylabel2="Line" )
    draw_bars(track=track1, data=data, options=baropts)
    
    lineopts = ChartOptions(yaxis2=True, legend='Line Legend', color=BLUE)
    draw_line(track=track1, data=data, options=lineopts)
    
    # layout must ba last
    draw_zones(track=track1, data=segdata, options=lineopts)
    
    draw_marks( track=track1, options=lineopts, data=[ 55 ])
    tracks= [ track1, track2, track3 ]
    m = MultiTrack(options=opts, tracks=tracks)
    
    m.show()
    
if __name__ == '__main__':
    import time
    now = time.time()
    for i in range(1):
        test()
    #print time.time()-now
    