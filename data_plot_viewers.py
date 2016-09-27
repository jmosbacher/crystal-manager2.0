import os
from traits.api import *
from traitsui.api import *
from traits.api import HasTraits
from traitsui.api import View, Item
from numpy import sin, cos, linspace, pi
from matplotlib.widgets import  RectangleSelector
from matplotlib.widgets import SpanSelector
from mpl_figure_editor import MPLFigureEditor, MPLInitHandler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class DataPlotEditorBase(HasTraits):

    figure = Instance(Figure, ())
    axs = List([])
    nplots = Int(1)


    view = View(Item('figure', editor=MPLFigureEditor(),
                     show_label=False),
                handler=MPLInitHandler,
                resizable=True)

    def __init__(self):
        super(DataPlotEditorBase, self).__init__()



    def mpl_setup(self):
        pass


    def remove_subplots(self):
        self.figure.clf()

    def remove_figure(self):
        plt.close(self.figure)

    def add_subplots(self, num):
        self.figure.patch.set_facecolor('none')
        self.axs = []
        for n in range(1, num + 1):
            self.axs.append(self.figure.add_subplot(num, 1, n, axisbg='#FFFFCC'))

    def clear_plots(self):
        for ax in self.axs:
            ax.cla()

    def set_title(self, title=' ', size=13):
        self.figure.suptitle(title,fontsize=size)

class IntegrationDataPlotEditor(DataPlotEditorBase):
    nplots = 3
    axvspn = List([])
    selections = List([])
    span = Any()


    def configure_selector(self):
        if len(self.axs):
            self.span = SpanSelector(self.axs[0], self.onselect, 'horizontal', useblit=True,
                             rectprops=dict(alpha=0.5, facecolor='red'))
        if self.figure is not None:
            self.figure.canvas.draw()

    def plot_data(self,data,plot_num,title=' '):
        self.axs[plot_num].plot(data[:,0],data[:,1],)
        #plt.pause(1)

    def clear_selections(self):
        self.selections = []
        for span in self.axvspn:
            try:
                span.remove()
            except:
                pass
        self.axvspn = []



    def onselect(self,xmin, xmax):
        if xmax-xmin == 0:
            return
        self.selections.append((xmin, xmax))
        for ax in self.axs:
            self.axvspn.append(ax.axvspan(xmin, xmax, color='red', alpha=0.4))
        if self.figure is not None:
            self.figure.canvas.draw()

    def redraw_selections(self):
        self.axvspn=[]
        for xmin,xmax in self.selections:
            for ax in self.axs:
                self.axvspn.append(ax.axvspan(xmin, xmax, color='red', alpha=0.4))
        if self.figure is not None:
            self.figure.canvas.draw()

    def mpl_setup(self):
        if len(self.axs) != self.nplots:
            self.add_subplots(self.nplots)
        self.configure_selector()


class FittingDataPlotEditor(DataPlotEditorBase):
    nplots = 2
    range_axvspn = Any()
    peaks_axvspn = List([])
    xrange = Tuple((0.0,0.0))
    peaks = List([])
    range_selector = Any() #Instance(SpanSelector)
    peaks_selector = Any() #(SpanSelector)
    editing = Enum('Peaks',['Range','Peaks'])


    def clear_spans(self,xrange=True,peaks=True):
        if xrange:
            try:
                self.range_axvspn.remove()
            except:
                pass

        if peaks:
            for axvspn in self.peaks_axvspn:
                try:
                    axvspn.remove()
                except:
                    pass

    def clear_selections(self):

        self.clear_spans(xrange=True,peaks=False)
        self.peaks = []
            #self.xrange = (0.0,0.0)



    def draw(self,xrange=True,peaks=True):
        if all([xrange, len(self.axs), len(self.xrange)]):
            self.range_axvspn = self.axs[0].axvspan(self.xrange[0], self.xrange[1], color='g', alpha=0.1)

        if all([peaks, len(self.axs)]):
            for xmin,xmax in self.peaks:
                self.peaks_axvspn.append(self.axs[0].axvspan(xmin, xmax, color='red', alpha=0.4))
        if self.figure is not None:
            self.figure.canvas.draw()

    def mpl_setup(self):
        self.add_subplots(self.nplots)
        self.configure_selector(peaks=True)
        #self.figure.canvas.draw()
        #self.activate_selector()

    def onselect(self,xmin,xmax):
        if self.editing=='Range':
            self.xrange = (xmin,xmax)
            self.clear_spans(peaks=False)
            self.draw(peaks=False)
            #self.figure.canvas.draw()

        elif self.editing=='Peaks':
            self.peaks.append((xmin,xmax))
            self.clear_spans(xrange=False)
            self.draw(xrange=False)
            #self.figure.canvas.draw()

    def configure_selector(self,xrange=False,peaks=False):
        self.peaks_selector = SpanSelector(self.axs[0], self.onselect, 'horizontal', useblit=True,
                                               rectprops=dict(alpha=0.5, facecolor='red'))
        self.peaks_selector.set_active(peaks)

        self.range_selector = SpanSelector(self.axs[0], self.onselect, 'horizontal', useblit=True,
                                     rectprops=dict(alpha=0.5, facecolor='g'))
        self.range_selector.set_active(xrange)

    def activate_selector(self,xrange=False,peaks=False):
        if self.peaks_selector is not None:
            self.peaks_selector.set_active(peaks)
        if self.range_selector is not None:
            self.range_selector.set_active(xrange)


    def _editing_changed(self,new):
        if new=='Range':
            self.configure_selector(xrange=True,peaks=False)
        elif new=='Peaks':
            self.configure_selector(xrange=False, peaks=True)


class SingleDataPlotEditor(DataPlotEditorBase):
    pass