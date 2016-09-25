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
from experiment import SpectrumExperiment, ExperimentTableEditor


class PlottingToolBase(HasTraits):
    experiments = List(SpectrumExperiment)
    selected = Instance(SpectrumExperiment)
    figure1 = Instance(Figure, ())
    figure2 = Instance(Figure, ())
    figure3 = Instance(Figure, ())
    figure4 = Instance(Figure, ())
    #plot_selected = Button('Plot Selected')


class PlottingTool3D(PlottingToolBase):
    view = View(
        HSplit(
            Item(name='experiments', show_label=False, editor=ExperimentTableEditor(selected='selected'), width=0.3),
            VGroup(
                HGroup(
                    Group(Item('figure1', editor=MPLFigureEditor(), show_label=False),
                          show_border=True, label='Wire Plot'),
                    Group(Item('figure2', editor=MPLFigureEditor(), show_label=False),
                          show_border=True, label='Mixed'),
                    ),
                HGroup(
                    Group(Item('figure3', editor=MPLFigureEditor(), show_label=False),
                          show_border=True, label='Contour'),
                    Group(Item('figure4', editor=MPLFigureEditor(), show_label=False),
                          show_border=True, label='Surface'),
                ),

            ),

        ),

        handler = MPLInitHandler,
        resizable = True,
    )

    def __init__(self,project):
        super(PlottingTool3D, self).__init__()
        self.experiments = project.experiments

    def mpl_setup(self):
        self.figure1.patch.set_facecolor('none')
        self.figure2.patch.set_facecolor('none')
        self.figure3.patch.set_facecolor('none')
        self.figure4.patch.set_facecolor('none')

    def _selected_changed(self):
        self.figure1.clf()
        self.figure2.clf()
        self.figure3.clf()
        self.figure4.clf()

        self.selected.plot_3d_wires(figure=self.figure1,title=self.selected.name)
        self.selected.plot_3d_mixed(figure=self.figure2,title=self.selected.name)
        self.selected.plot_3d_contour(figure=self.figure3,title=self.selected.name)
        self.selected.plot_3d_surf(figure=self.figure4,title=self.selected.name)

        #self.figure1.set_tight_layout(True)
       # self.figure2.set_tight_layout(True)
        #self.figure3.set_tight_layout(True)
        #self.figure4.set_tight_layout(True)
        #plt.tight_layout()
