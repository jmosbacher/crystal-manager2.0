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
    project = Any()
    experiments = List(BaseExperiment)
    selected = Instance(BaseExperiment)
    int_results = List(IntegrationResultBase)
    has_selections = Property(Bool)

    #####       Plots     #####
    display = Instance(DataPlotEditorBase)

    #####       GUI     #####
    integrate = Button('Integrate Selections')
    clear = Button('Clear Selections')
    refresh = Button('Refresh')
    save = Button('Save Results')
    select_range = Button('Select Range')

    view = View(
        HSplit(
            VGroup(
                HGroup(Item(name='select_range', show_label=False, ),
                       Item(name='integrate', show_label=False, ),
                       Item(name='clear', show_label=False, ),
                       Item(name='refresh', show_label=False),
                       show_border=True, label='Control'),
                Group(Item(name='display', style='custom',show_label=False),
                      show_border=True, label='Plots'),

            ),

            VGroup(
                Group(Item(name='experiments', show_label=False,editor=ExperimentTableEditor(selected='selected')),
                      show_border=True, label='Data'),
                Group(Item(name='int_results', show_label=False,style='custom',
                           editor=ListEditor(use_notebook=True,deletable=True,page_name='.name'),),
                      show_border=True, label='Integration Results'),




            ),

        ),
    buttons = ['OK'],
    title = 'Comparison Integration Tool',
    kind = 'nonmodal',

    scrollable = True,
    resizable = True,
    height = 800,
    width = 1200,
    )

    def _get_has_selections(self):
        if self.display is None:
            return False
        if len(self.display.selections):
            return True
        else:
            return False


    def _select_range_fired(self):
        self.display.clear_selections()
        self.display.mpl_setup()

    def _refresh_fired(self):
        self.display.clear_plots()
        self.display.clear_selections()
        self.selected.plot_1d(axs=self.display.axs,legend=False)
        self.set_titles()
        self.display.configure_selector()

    def _selected_changed(self):
        self.display.clear_plots()
        self.display.clear_selections()
        self.selected.plot_1d(axs=self.display.axs,legend=False)
        self.set_titles()
        self.display.configure_selector()

    def integrate_all(self):
        raise NotImplementedError

    def store_results(self, results):
        raise NotImplementedError

    def set_titles(self):
        raise NotImplementedError

    def save_results(self):
        raise NotImplementedError

    def _integrate_fired(self):
        results = self.integrate_all()
        self.store_results(results)

    def _clear_fired(self):
        self.display.clear_selections()
        self.display.configure_selector()

    def _save_fired(self):
        self.save_results()

    def _int_results_default(self):
        raise NotImplementedError


class ComparisonIntegrationTool(IntegrationToolBase):
    def __init__(self,project):
        super(ComparisonIntegrationTool, self).__init__()
        self.project = project
        self.experiments = project.comparisons
        self.int_results = project.comp_int_results

    def _display_default(self):
        display = DataPlotEditorBase(nplots=3)
        # display.add_subplots(3)
        return display
    def set_titles(self):
        pass

    def store_results(self,results):
        if self.int_results[0].name=='empty':
            self.int_results = []

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
            res.results = np.asarray(sorted(result_array))
            self.int_results.append(res)


    def integrate_all(self):
        results = []
        for n,(min, max) in enumerate(self.display.selections):
            result = {'name': self.selected.name+str(n), 'min': min, 'max': max}

            for meas in self.selected.exp1.measurements:
                if meas.ex_wl not in result.keys():
                    result[meas.ex_wl] = {}
                result[meas.ex_wl]['exp1'] = meas.integrate_bg_corrected(min, max)

            for meas in self.selected.exp2.measurements:
                if meas.ex_wl not in result.keys():
                    result[meas.ex_wl] = {}
                results[meas.ex_wl]['exp2'] = meas.integrate_bg_corrected(min, max)

            for meas in self.selected.subtraction.measurements:
                if meas.ex_wl not in result.keys():
                    results[meas.ex_wl] = {}
                result[meas.ex_wl]['subtraction'] = meas.integrate_bg_corrected(min, max)

            results.append(result)
        return results

    def _int_results_default(self):
        return [ComparisonIntegrationResult()]

    def save_results(self):
        if self.project is not None:
            self.project.comp_int_results = self.int_results

class ExperimentIntegrationTool(IntegrationToolBase):

    def __init__(self,project):
        super(ExperimentIntegrationTool, self).__init__()
        self.project = project
        self.experiments = project.experiments
        self.int_results = project.exp_int_results


    def _display_default(self):
        display = DataPlotEditorBase(nplots=3)
        # display.add_subplots(3)
        return display


    def set_titles(self):
        if len(self.display.axs):
            self.display.axs[0].set_title('Signal',fontsize=12)
            self.display.axs[1].set_title('Background',fontsize=12)
            self.display.axs[2].set_title('Reference',fontsize=12)

    def store_results(self, results):

        for result in results:
            res = ExperimentIntegrationResult()
            min = 0.0
            max = 0.0
            res.int_range = (result.get('min', 0.0), result.get('max', 0.0))
            result_array = []
            for key, value in result.items():
                if key == 'name':
                    res.name = value
                elif key == 'min':
                    min = value
                elif key == 'max':
                    max = value
                else:
                    result_array.append(
                        [key, value.get('sig', 0.0), value.get('bg', 0.0), value.get('ref', 0.0)])
            res.int_range = (min, max)
            res.results = np.asarray(sorted(result_array))
            self.int_results.append(res)

    def integrate_all(self):
        results = []
        for min, max in self.display.selections:
            result = {'name': self.selected.name, 'min': min, 'max': max}

            for meas in self.selected.measurements:
                if meas.ex_wl not in result.keys():
                    result[meas.ex_wl] = {}
                result[meas.ex_wl]['sig'] = meas.integrate_signal(min, max)
                result[meas.ex_wl]['bg'] = meas.integrate_bg(min, max)
                result[meas.ex_wl]['ref'] = meas.integrate_ref(min, max)
            if len(result.items()):
                results.append(result)
        return results

    def _int_results_default(self):
        return [ExperimentIntegrationResult()]

    def save_results(self):
        if self.project is not None:
            self.project.exp_int_results = self.int_results