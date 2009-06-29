"""
Creates charts using the ChartDirector API

Requires ChartDirector to function.

NOTE: Features are drawn on layers, each drawing command generates a new layer 
that will be placed B{under} the previous one. This matters only when drawing 
multiple different different type of features on the same chart.

"""

from chartutil import *
import operator
import pychartdir

class BaseChart(object):
    """
    Contains the functionality that all charts must have. 
    This is an abstract class that cannot be instantiated.    
    """
    def __init__(self, options):
        """
        Requires an options parameter must be created with the L{ChartOptions} 
        function.  
        """
        self.o = options

    def init_axes(self):
        """
        Initializes the axes, margins, tick densities
        
        Inward ticks by default, vertical gridlines for evey X tick
        """
        # a shortcut
        o = self.o
        
        # apply xscale if specified
        if o.xscale:
            self.c.xAxis().setLinearScale(*o.xscale)
            self.c.xAxis().setIndent(0) # this fixes extra width for barlayer
            self.c.xAxis().setLabelStep(1000)

        # apply yscale (on the left)
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

    def custom_settings(self):
        """
        Contains custom options in subclasses
        """
        pass

    def init_plotarea(self):
        """
        Initializes the plot area that the chart will be drawn upon.

        The drawing area will be heigh minus top and bottom padding, 
        and width minus left and right padding.
        """
        o = self.o
        h = o.h - o.tpad - o.bpad
        w = o.w - o.lpad - o.rpad
        self.area = self.c.setPlotArea(o.lpad, o.tpad, w, h, o.bgColor, o.altBgColor, o.edgeColor, o.hGridColor, o.vGridColor)

    def hr(self, y=0, color=GREY, lw=1, label=None, lpos=10):
        """
        Adds a horizonal line at the coordinates specfied by the y parameter, 
        with a given color and line width. 
        The line streches over the entire xscale.

        If the label parameter is passed then writes it out above the line 
        in multiple locations
        """

        # line must be as long as the autoscaled chart
        assert self.o.xscale, "must have an xscale specified"
        
        if label:
            linecolor = self.c.dashLineColor(color, pychartdir.DashLine)
        else:
            linecolor = color

        line  = self.c.addLineLayer([y,y], color=linecolor)
        line.setLineWidth(lw)
        line.setXData(self.o.xscale)
        
        # adds evenly distributed labels above the horizonal line
        if label:
            lo, hi = self.o.xscale
            step   = (hi-lo)/6

            cx = range(lo, hi, step)
            cy = [ y ] * len(cx)
            labs = [ str(label) ] * len(cx)

            scatter = self.c.addScatterLayer(cx, cy, "", CIRCLESYMBOL, 0, 0xff3333, 0xff3333)
            scatter.addExtraField(labs)
            scatter.setDataLabelFormat("{field0}")
            textbox = scatter.setDataLabelStyle("arialbd.ttf", self.o.fontSize-2, color)
            textbox.setAlignment(CENTER)
            textbox.setPos(0, -lpos )

    def save(self, fname):
        "Saves the chart into a file"
        self.c.makeChart(fname)

    def show(self):
        "Displays the chart with Tk and PIL"
        plotting.show(chart=self.c)

class XYChart(BaseChart):
    """
    Represents a chart that is drawn with X and Y coordinates.

    Example use:

    >>> options = ChartOptions()
    >>> xy = XYChart(options=options)
    >>> x = y = range(90)
    >>> xy.draw_line(x=x, y=y, color=RED, name='RED Line')
    >>> xy.draw_bars(x=x, y=y, color=BLUE, name='BLUE Bars')
    >>> xy.hr(y=10) 
    >>> # xy.show() #disabled during testing
    """
    def __init__(self, options):
        """
        XYChart will autoscale on the Y-scales if the yscale(2) parameters are not specified.
        """
        BaseChart.__init__(self, options=options)
        self.c = pychartdir.XYChart(self.o.w, self.o.h)
        self.c.setClipping()
        self.init_plotarea()
        self.init_axes()
        self.custom_settings()

    def draw(self, x, y, dtype, color=BLUE, name=None, lw=1, yaxis2=False):
        """
        Draws data on the chart.

        Parameter dtype may be 'LINE' or 'BARS'
        """
        
        if dtype == BARS:
            layer = self.c.addBarLayer(y, color=color, name=name)
            layer.setBarWidth(lw)
        elif dtype == LINE:
            layer = self.c.addLineLayer(y, color=color, name=name)
            layer.setLineWidth(lw)    
        else:
            raise Exception('Incorrect dtype=%s' % dtype)

        if yaxis2:
            layer.setUseYAxis(self.c.yAxis2())
        else:
            layer.setUseYAxis(self.c.yAxis())

        layer.setBorderColor(color)
        layer.setXData(x)
        self.add_legend(text=name)

    def draw_line(self, x, y, color=BLUE, name=None, lw=1, yaxis2=False):
        """
        Draws an XY line. If name is specified it will be added as legend. 
        If yaxis2 is True
        the right hand Y-axis will be used. lw specifies the line width.
        """
        return self.draw(x=x, y=y, color=color, name=name, lw=lw, yaxis2=yaxis2, dtype=LINE)

    def draw_bars(self, x, y, color=BLUE, name=None, lw=1, yaxis2=False):
        """
        Draws a bar graph. If name is specified it will be added as legend. 
        If yaxis2 is True
        the right hand Y-axis will be used. lw specifies the bar widths.
        """
        return self.draw(x=x, y=y, color=color, name=name, lw=lw, yaxis2=yaxis2, dtype=BARS)
    
    def add_legend(self, text):
        """
        Adds a legend to the chart.
        """
        if text:
            o = self.o
            legend = self.c.addLegend(o.lpad, o.tpad, 0, None, o.fontSize)
            legend.setBackground(TRANSPARENT)
            legend.setFontSize(o.fontSize)  

class TrackChart(XYChart):
    """
    Represents a chart that displays tracks
    Example use:
    
    """
    def custom_settings(self):        
        "Track specific settings"
        o = self.o
        
        # track colors
        self.c.xAxis().setColors(GREY, o.XAxisColor, BLACK, TRANSPARENT)

        # modify legend position
        legend = self.c.addLegend(o.lpad, o.h-30, 0, None, o.fontSize)
        legend.setBackground(TRANSPARENT)
        legend.setFontStyle("arialbd.ttf")
        legend.setFontSize(o.fontSize)
        self.c.setAntiAlias(False)
    
    def draw_special(self, data, dtype, labels=None, color=BLUE, name=None, lw=2, yc=0, lpos=0):
        """
        Draws a track:

        """

        o = self.o 

        # turns the incoming data into a single long list suitable for fast slicing 
        fast = []
        map(fast.extend, data) # mutate via extend

        # getting the labels
        labels = fast[2::3]

        if dtype == VECTOR:
            # the way this works is that uses a reference point to draw an arrow
            # of given lenght then rotates it into the right direction, see ChartDirector
            # VectorLayer for more info
            x  = fast[1::3] # reference on x
            y  = [ yc ] * len(data) # reference on y
            rc = [ e[1] - e[0] for e in data ] # lenghts on x
            ac = [ 90 ] * len(data) # angles
            vector = self.c.addVectorLayer(x, y, rc, ac, pychartdir.XAxisScale, color, name)
            vector.setArrowAlignment(TOPCENTER)
            vector.setArrowHead2(o.arrow_polygon)
            vector.setArrowHead(lw)
            vector.setLineWidth(lw)
        
        elif dtype == STRIPES:
            # stripes are secondary features superimposed on an exisiting 
            # segments, the coordinates are always relative to the start
            xdata = []
            op1 = operator.add
            op2 = operator.sub

            forw = o.stripe_coords
            revr = [ (-r[0], -r[1]) for r in forw ]
            for start, end, label in data:
                if start > end: 
                    stripes = forw
                else:
                    stripes = revr
                for x, y in stripes:
                    xdata.extend([ start-x, start-y, NOVALUE ])

            y = [ yc ] * len(xdata)
            striped = self.c.addLineLayer(y , color=color, name='')
            striped.setLineWidth(lw)
            striped.setXData(xdata)
            # stripes are secondary features, no label for them
            return
            
        elif dtype == SEGMENT:
            # segments are continous lines with NOVALUE between the end of one segment
            # and the start of the next segment (ChartDirector specific choice)
            # will mutate the fast list (that's why we needed it)
            # stripes will drawn before the segments so that are visible
            y = [ yc ] * len(fast)
            fast[2::3] = [ NOVALUE ] * len(labels)
            segment = self.c.addLineLayer(y , color=color, name=name)
            segment.setLineWidth(lw)
            segment.setXData(fast) 
        else:
            raise Exception('Incorrect dtype=%s' % dtype)

        # code to display labels
        # will center them above the interval, always cull (see util.py to ensure there is sufficient 
        # space to fit them in
        if self.o.show_labels:
            xpos  = [ (e[0]+e[1])/2.0 for e in data ]
            scatter = self.c.addScatterLayer(xpos, y, "", CIRCLESYMBOL, 0, 0xff3333, 0xff3333)
            scatter.addExtraField(labels)
            scatter.setDataLabelFormat("{field0}")
            textbox = scatter.setDataLabelStyle("arialbd.ttf", self.o.fontSize, color)
            textbox.setAlignment(CENTER)
            textbox.setPos(0, -(lw+2)+lpos )

    def draw_vectors(self, data, color=RED, name=None, lw=12, yc=0, lpos=0):
        "Draws vectors from triplet data"
        return self.draw_special(data=data, color=color, name=name, lw=lw, yc=yc, dtype=VECTOR, lpos=lpos)

    def draw_segments(self, data, color=BLUE, name=None, lw=12, yc=0, lpos=0):
        "Draws segments from triplet data"
        return self.draw_special(data=data, color=color, name=name, lw=lw, yc=yc, dtype=SEGMENT, lpos=lpos)

    def draw_stripes(self, data, color=GREEN, name=None, lw=12, yc=0, lpos=0):
        "Draws stripes from triplet data"
        #data = reorder(data)
        return self.draw_special(data=data, color=color, name=name, lw=lw, yc=yc, dtype=STRIPES, lpos=lpos)

class MultiChart(object):
    """
    Merges multiple charts passed in the P{charts} list into a single chart
    """
    def __init__(self, options, charts=[]):
        self.o = options
        assert charts, 'Need to draw at least one chart'
        first = charts[0]

        # adds one last chart for a closing feature
        last_opts = ChartOptions(tpad=0, bpad=0, w=self.o.w, h=1, bgColor=BLACK, \
            altBgColor=RED, edgeColor=BLACK, hGridColor=TRANSPARENT, vGridColor=TRANSPARENT, ylabel='')
        last_chart = TrackChart(options=last_opts)
        charts.append(last_chart)

        self.charts = charts
        self.w = self.o.lpad + self.o.w + self.o.rpad
        self.h = self.o.tpad + sum([ chart.o.h for chart in charts ]) + self.o.bpad 
        self.c = pychartdir.MultiChart( self.w, self.h)

        ypos = self.o.tpad
        for chart in self.charts:
            self.c.addChart(self.o.lpad, ypos, chart.c)
            ypos += chart.o.h
    
    def save(self, fname):
        self.c.makeChart(fname)

    def show(self):
        show_plot(chart=self.c)

def test(verbose=0):
    "Performs module level testing"
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE, verbose=verbose)

if __name__ == "__main__":
    test()


    if 1:
        xscale = [0,100]
    
        charts = []
        options1 = ChartOptions(
            edgeColor=GREY, XAxisOnTop=1, ylabel='Data', bpad=0, xscale=xscale)

        # testing the XYchart            
        x = y = range(90)
        xy = XYChart(options=options1 )
        xy.draw_line(x=x, y=y, color=RED, name='RED Line')
        xy.draw_bars(x=x, y=y, color=BLUE, name='BLUE Bars')
        xy.hr(y=10) 
        charts.append(xy)

        # setup custom stripes            
        data = [ (10, 30, 'A'), (40, 60, 'B'), (90, 70, 'C') ]
        stripe_coords = [ (0,2), (10,12), (18,20) ]
        options2 = TrackOptions(edgeColor=GREY, h=100, xscale=xscale, 
            stripe_coords=stripe_coords, ylabel='ORF', yscale=[-10, 10])
        tr = TrackChart(options=options2)
        tr.draw_stripes(data=data, yc=3, lw=2)
        tr.draw_vectors(data=data, color=RED, yc=3)
        tr.hr(y=3)
        tr.draw_segments(data=data, yc=-3, lpos=28)
        tr.hr(y=-3, label='AAA', color=RED)

        charts.append(tr)
        charts.append(tr)
        
        # show off multichart
        options3 = TrackOptions()
        m = MultiChart(options=options3, charts=charts)
        m.show()
        #m.save('a.png')