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
from integration_results import IntegrationResultBase,ComparisonIntegrationResult, ExperimentIntegrationResult


class IntegrationToolBase(HasTraits):
    experiments = List(BaseExperiment)
    selected = Instance(BaseExperiment)
    int_results = List(IntegrationResultBase,[])
    has_selections = Property(Bool)

    #####       Plots     #####
    display = Instance(DataPlotEditorBase)

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

            VGroup(
                Group(Item(name='experiments', show_label=False,editor=ExperimentTableEditor()),
                      show_border=True, label='Data'),
                Group(Item(name='int_results', show_label=False,
                           editor=ListEditor(use_notebook=True,deletable=True,page_name='name'),),
                      show_border=True, label='Integration Results'),




            ),

        )

    )

    def _get_has_selections(self):
        if self.display is None:
            return False
        if len(self.display.selections):
            return True
        else:
            return False



    def _refresh_fired(self):
        self.display.clear_plots()
        self.selected.plot_1d(axs=self.display.axs)

    def integrate_all(self):
        raise NotImplementedError

    def store_results(self, results):
        raise NotImplementedError

    def _integrate_fired(self):
        results = self.integrate_all()
        self.store_results(results)

    def _clear_fired(self):
        self.display.clear_selections()


class ComparisonIntegrationTool(IntegrationToolBase):
    def _display_default(self):
        display = DataPlotEditorBase(nplots=3)
        # display.add_subplots(3)
        return display

    def store_results(self,results):

        for result in results:
            res = ComparisonIntegrationResult()
            min = 0.0
            max = 0.0
            res.int_range = (result.get('min',0.0),result.get('max',0.0))
            result_array = []
            for key,value in result.items():
                if key=='name':
                    res.name = value
                elif key=='min':
                    min = value
                elif key==max:
                    max=value
                else:
                    result_array.append([key, value.get('exp1',0.0),value.get('exp2',0.0),value.get('subtraction',0.0)])
            res.int_range = (min,max)
            res.results = np.asarray(result_array)
            self.int_results.append(res)


    def integrate_all(self):
        results = []
        for min, max in self.display.selections:
            result = {'name': self.selected.name, 'min': min, 'max': max}

            for meas in self.selected.exp1:
                if meas.ex_wl not in result.keys():
                    result[meas.ex_wl] = {}
                result[meas.ex_wl]['exp1'] = meas.integrate_range(min, max)

            for meas in self.selected.exp2:
                if meas.ex_wl not in result.keys():
                    result[meas.ex_wl] = {}
                results[meas.ex_wl]['exp2'] = meas.integrate_range(min, max)

            for meas in self.selected.subtraction:
                if meas.ex_wl not in result.keys():
                    results[meas.ex_wl] = {}
                result[meas.ex_wl]['subtraction'] = meas.integrate_range(min, max)

            results.append(result)
        return results