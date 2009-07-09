"""
Track specification.
"""

# lots of constants and other names
from chartutil import *
from genetrack import logger

class Base(object):
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
    
class XYTrack(Base):
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

class BarTrack(XYTrack):
    "Implements a bar graph"
    def draw(self, data, options=None):
        # may override 
        o = options or self.o
        layer = self.c.addBarLayer(data.y, color=o.color, name=o.ylabel)
        layer.setBarWidth(o.lw)
        layer.setBorderColor(o.color)
        
        # switch axes
        if o.yaxis2:
            axis = self.c.yAxis2()
        else:    
            axis = self.c.yAxis()
            
        layer.setUseYAxis(axis)
        layer.setXData(data.x)
        #self.add_legend(text=o.name)
        
class TrackManager(object):
    pass
        
def test():
    from server.web import models
    data_id = 1
    data_path = models.Data.objects.get(id=data_id).content.path
    
    data = dict(color=RED, glyph='AUTO', data=data_id, data_path=data_path)

    options = ChartOptions(init=data, yaxis2=2)
    data = Options( x=range(100), y=range(100) )
    track = BarTrack(options)
    track.draw(data=data)
    track.show()
    
if __name__ == '__main__':
    test()