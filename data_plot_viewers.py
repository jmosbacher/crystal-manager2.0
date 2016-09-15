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


class DataPlotEditorBase(HasTraits):

    figure = Instance(Figure, ())
    axs = List([])
    axvspn = List([])
    selections = List([])
    span = Any()

    view = View(Item('figure', editor=MPLFigureEditor(),
                     show_label=False),
                handler=MPLInitHandler,
                resizable=True)

    def __init__(self,nplots):
        self.nplots = nplots
        super(DataPlotEditorBase, self).__init__()

    def add_subplots(self,num):
        for n in range(1,num+1):
            self.axs.append(self.figure.add_subplot(num,n,1, axisbg='#FFFFCC'))
        if len(self.axs):
            self.span = SpanSelector(self.axs[0], self.onselect, 'horizontal', useblit=True,
                             rectprops=dict(alpha=0.5, facecolor='red'))
        self.figure.canvas.draw()

    def plot_data(self,data,plot_num,title=' '):
        self.axs[plot_num].plot(data[:,0],data[:,1],)

    def clear_selections(self):
        self.selections = []
        for span in self.axvspn:
            span.remove()
        self.axvspn = []

    def clear_plots(self):
        for ax in self.axs:
            ax.cla()


    def onselect(self,xmin, xmax):
        if xmax-xmin == 0:
            return
        self.selections.append((xmin, xmax))
        for ax in self.axs:
            self.axvspn.append(ax.axvspan(xmin, xmax, color='red', alpha=0.4))
        self.figure.canvas.draw()

    def mpl_setup(self):
        self.add_subplots(self.nplots)



class SingleDataPlotEditor(DataPlotEditorBase):
    pass