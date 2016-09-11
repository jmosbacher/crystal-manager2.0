import os
from traits.api import *
from traitsui.api import *
from traitsui.extras.checkbox_column import CheckboxColumn
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from auxilary_functions import wl_to_rgb, avg_data_array, bin_data_dict
from file_selector import string_list_editor
import numpy as np
import random
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle

class FileDataViewer(HasTraits):
    data = Dict({'sig':[], 'bgd':[], 'ref':[]})
    sig_data = List()
    bgd_data = List()
    ref_data = List()

    view = View(
        VGroup(
            Group(Item(name='sig_data',editor=string_list_editor, show_label=False),show_border=True,label='Signal File'),

            Group(Item(name='bgd_data',editor=string_list_editor, show_label=False ),show_border=True,label='Background File'),
            Group(Item(name='ref_data',editor=string_list_editor, show_label=False  ),show_border=True,label='Reference File'),


        ),
        title = 'Supplemental file data',
        scrollable = True,
        resizable = True,


    )


class BaseMeasurement(HasTraits):
    __kind__ = 'Base'
    main = Any()
    name = Str('Name')
    date = Date()
    summary = Property(Str)

    notes = Str('')
    notebook = Int(1)
    page = Int()

    is_selected = Bool(False)

    def __init__(self, **kargs):
        HasTraits.__init__(self)
        self.main = kargs.get('main', None)

    def _anytrait_changed(self):
        if self.main is None:
            return
        self.main.dirty = True

    def _get_summary(self):
        raise NotImplemented


class SpectrumMeasurement(BaseMeasurement):
    __kind__ = 'Spectrum'

    #####       User Input      #####
    duration = Int(0)

    ex_pol = Int()  # Excitation Polarization
    em_pol = Int()  # Emission Polarization

    ex_wl = Float()  # Excitation Wavelength
    em_wl = Tuple((0.0, 0.0), cols=2, labels=['Min', 'Max'])  # Emission Wavelength

    exposure = Int(1)
    e_per_count = Int(1)  # electrons per ADC count

    #####       Extracted Data      #####
    signal = Array()
    bg = Array()
    ref = Array()
    file_data = Dict()

    #####       Flags      #####
    has_sig = Property(Bool) #Bool(False)
    has_bg = Property(Bool) #Bool(False)
    has_ref = Property(Bool) #Bool(False)
    color = Property() #Tuple(0.0, 0.0, 0.0)  # Enum(['r', 'g', 'b', 'y', 'g', 'k','m','c','k'])

    #####       Calculated Data      #####


    #####       UI      #####


    #####       GUI layout      #####
    view = View(
        VGroup(

            HGroup(
                Item(name='ex_pol', label='Excitation POL'),
                Item(name='ex_wl', label='Excitation WL'),
                show_border=True, label='Excitation'),

            HGroup(
                Item(name='em_pol', label='Emission POL'),
                Item(name='em_wl', label='Emission WL'),
                Item(name='e_per_count', label='e/count'),
                Item(name='color', label='Plot Color'),
                show_border=True, label='Emission'),

        ),

    )

    #####       Methods      #####


    def _get_summary(self):
        report = 'Excitation: %d nm'%self.ex_wl + ' | Emission Range: %d:%d nm'%self.em_wl
        return report

    def _get_has_sig(self):
        if len(self.signal):
            return True
        else:
            return False
    def _get_color(self):
        return wl_to_rgb(self.ex_wl)

    def _get_has_bg(self):
        if len(self.bg):
            return True
        else:
            return False

    def _get_has_ref(self):
        if len(self.ref):
            return True
        else:
            return False

    def _signal_default(self):
        return np.array([])

    def _signal_changed(self):
        if len(self.signal) > 1:
            self.em_wl = (round(min(self.signal[:, 0])), round(max(self.signal[:, 0])))

    def _bg_default(self):
        return np.array([])

    def create_series(self):
        """

        :return:
        """
        sig = self.bin_data()
        return pd.Series(sig[:, 1], index=sig[:, 0], name=self.ex_wl)

    def bin_bg(self):
        """

        :return:
        """
        binned = {}
        if self.has_bg:
            averaged = avg_data_array(self.bg)
            binned = bin_data_dict(averaged)

        return binned



    def bin_data(self,rem_bg=True):
        """
        :return:
        """
        if not self.has_sig:
            return np.zeros((1,2))

        averaged = avg_data_array(self.signal)
        binned = bin_data_dict(averaged)

        if rem_bg:
            avg_bg = self.bin_bg()
        else:
            avg_bg = {}
        final = []
        for wl, sig in binned.items():
            final.append([wl, sig-avg_bg.get(wl,0.0)])
        # print sorted(averaged)

        return np.array(sorted(final))

    def integrate_range(self,min,max):
        signal = self.bin_data()
        in_range = []
        for wl,sig in signal:
            if wl<=max and wl>=min:
                in_range.append(sig)
        result = np.sum(in_range)
        return result


    def plot_data(self,ax=None,legend=True):
        if self.has_sig:
            ser = self.create_series()
            ax = ser.plot(color=self.color, label=str(self.ex_wl), legend=legend, ax=ax)
            if ax is not None:
                ax.set_xlabel('Emission Wavelength')
                ax.set_ylabel('Counts')
            else:
                plt.show()

    def show_file_data(self):
        viewer = FileDataViewer()
        viewer.sig_data = self.file_data['sig']
        viewer.bgd_data = self.file_data['bgd']
        viewer.ref_data = self.file_data['ref']
        viewer.edit_traits()


class AnealingMeasurement(BaseMeasurement):
    __kind__ = 'Anealing'
    temperature = Int(0)
    heating_time = Int(0)
    view = View(
        VGroup(

            HGroup(
                Item(name='temperature', label='Temperature'),
                Item(name='heating_time', label='Heating time'),
                show_border=True, label='Anealing Details'),

        ),

)

class MeasurementTableEditor(TableEditor):

    columns = [
               CheckboxColumn(name='is_selected', label='', width=0.05, horizontal_alignment='center', ),
               ObjectColumn(name='name', label='Name', horizontal_alignment='left', width=0.25),
               ObjectColumn(name='summary', label='Details', width=0.3, horizontal_alignment='center', ),
               ObjectColumn(name='date', label='Date', horizontal_alignment='left', width=0.25),
               ObjectColumn(name='__kind__', label='Type', width=0.25, horizontal_alignment='center'),


               ]

    auto_size = True
    sortable = False
    editable = False
