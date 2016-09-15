import os
from traits.api import *
from traitsui.api import *
from traitsui.extras.checkbox_column import CheckboxColumn
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import colorConverter

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from auxilary_functions import wl_to_rgb, subtract_data_arrays
from file_selector import string_list_editor
from viewers import DictEditor
import numpy as np
import random
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle
from experiment import SpectrumExperiment,BaseExperiment, ExperimentTableEditor
from measurement import SpectrumMeasurement
from compare_experiments import ExperimentComparison
from data_plot_viewers import DataPlotEditorBase
from integration_results import IntegrationResult

class IntegrationToolBase(HasTraits):
    comparisons = List()
    int_results = List(IntegrationResult)
    has_selections = Property(Bool)

    #####       Plots     #####
    display = Instance(DataPlotEditorBase)
    # exp1_ax = Instance(Axes)
    # exp2_ax = Instance(Axes)
    # subtraction_ax = Instance(Axes)

    #####       GUI     #####
    integrate = Button('Integrate Selections')
    clear = Button('Clear Selections')
    refresh = Button('Refresh')

    view = View(
        HSplit(
            VGroup(
                HGroup(Item(name='integrate', show_label=False, enabled_when='has_selections'),
                       Item(name='clear', show_label=False, enabled_when='has_selections'),
                       Item(name='refresh', show_label=False),
                       ),
                Group(Item(name='display', show_label=False),
                      show_border=True, label='Plots'),

            ),

            VGroup()

        )

    )

    def _get_has_selections(self):
        if self.display is None:
            return False
        if len(self.display.selections):
            return True
        else:
            return False

    def _display_default(self):
        display = DataPlotEditorBase(nplots=3)
        # display.add_subplots(3)
        return display

    def _refresh_fired(self):
        self.display.clear_plots()
        self.selected.plot_1d()

class ComparisonIntegrationTool(IntegrationToolBase):
    selected = Instance(ExperimentComparison)