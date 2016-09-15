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
from auxilary_functions import wl_to_rgb
import numpy as np
import random
import pandas as pd
from measurement import BaseMeasurement, SpectrumMeasurement, MeasurementTableEditor, ArrayViewer
from data_importing import AutoSpectrumImportTool
from auxilary_functions import merge_spectrums
try:
    import cPickle as pickle
except:
    import pickle


class BaseExperiment(HasTraits):
    __kind__ = 'Base'
    main = Any()
    name = Str('Name')
    date = Date()
    crystal_name = Str('')

    measurements = List(BaseMeasurement)
    selected = Instance(BaseMeasurement)



class SpectrumExperiment(BaseExperiment):
    __kind__ = 'Spectrum'
    #####       Data      #####

    ex_wl_range = Property(Tuple)
    em_wl_range = Property(Tuple)
    measurement_cnt = Property(Int)

    #####       UI      #####
    add_type = Enum(['Spectrum', 'Raman', 'Anealing'])
    add_meas = Button('Add Measurements')
    edit = Button('Open')
    remove = Button('Remove Selected')
    select_all = Button('Select All')
    unselect_all = Button('Un-select All')
    plot_selected = Button('Plot Selected')
    merge = Button('Merge')
    # import_exp = Button('Import Experiment')
    #comp_sel = Button('Compare selected')
    show_file_data = Button('File data')
    sort_by_wl = Button('Sort by WL')
    auto_merge = Button('Merge by WL')

    scale = Float(1)
    scale_what = Enum('Selected',['All','Selected'])
    rescale = Button('Rescale')

    show_signal = Button('View Signal')
    show_bg = Button('View BG')
    show_binned = Button('View Binned')

    #####       Flags      #####
    is_selected = Bool(False)
    has_measurements = Property()

    #####       GUI View     #####
    view = View(

        VGroup(



            HGroup(
                    Item(name='select_all', show_label=False),
                    Item(name='unselect_all', show_label=False),
                    Item(name='remove', show_label=False,enabled_when='selected'),
                    Item(name='sort_by_wl', show_label=False),
                    Item(name='merge', show_label=False),
                    Item(name='plot_selected', show_label=False, enabled_when='selected'),
                    Item(name='auto_merge', show_label=False,),
                    Item(name='show_file_data', show_label=False, enabled_when='selected'),
                    #Item(name='add_type', show_label=False),
                    Item(name='add_meas', show_label=False),
                    Item(name='scale', label='Scale'),
                    Item(name='scale_what', show_label=False),
                    Item(name='rescale', show_label=False),
                  ),
            HGroup(

                Item(name='plot_selected', show_label=False, enabled_when='selected'),
                Item(name='show_binned', show_label=False, enabled_when='selected'),
                Item(name='show_signal', show_label=False, enabled_when='selected'),
                Item(name='show_bg', show_label=False, enabled_when='selected'),
                Item(name='show_file_data', show_label=False, enabled_when='selected'),


            ),
            Group(
                Item(name='measurements', show_label=False, editor=MeasurementTableEditor(selected='selected')),
                show_border=True, label='Datasets'),

                #Item(name='selected', style='custom', show_label=False),



            show_border=True, label='Measurements'),
        title='Experiment Editor',
        buttons=['OK'],
        kind='nonmodal',
        scrollable=True,
        resizable=True,
        height=800,
        width=1000,

    )

    #####       Initialization Methods      #####
    def __init__(self, **kargs):
        HasTraits.__init__(self)
        self.main = kargs.get('main', None)

    def _anytrait_changed(self):
        if self.main is None:
            return
        self.main.dirty = True

    def _get_ex_wl_range(self):
        wls = [10000, 0]
        for exp in self.measurements:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.ex_wl, wls[0]))
                wls[1] = round(max(exp.ex_wl, wls[1]))
        return tuple(wls)

    def _get_em_wl_range(self):
        wls = [10000, 0]
        for exp in self.measurements:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.em_wl[0], wls[0]))
                wls[1] = round(max(exp.em_wl[1], wls[1]))
        return tuple(wls)

    def _get_measurement_cnt(self):
        return len(self.measurements)

    def _get_has_measurements(self):
        if self.measurements is None:
            return False
        if len(self.measurements):
            return True
        else:
            return False

    def _sort_by_wl_fired(self):
        def wl(spectrum):
            return spectrum.ex_wl,spectrum.em_wl[0]
        self.measurements.sort(key=wl)

    def _add_meas_fired(self):
        self.import_data()

    def _rescale_fired(self):

        for meas in self.measurements:
            if self.scale_what == 'All':
                meas.rescale(self.scale)
            elif self.scale_what=='Selected':
                if meas.is_selected:
                    meas.rescale(self.scale)

    def _auto_merge_fired(self):
        def wl_key(spectrum):
            return spectrum.ex_wl,spectrum.em_wl[0]

        organized = {}
        for meas in self.measurements:
            wl = meas.ex_wl
            if wl in organized.keys():
                organized[wl].append(meas)
            else:
                organized[wl] = [meas]
        for wl, measurments in organized.items():
            if len(measurments)>1:
                self.merge_group(sorted(measurments,key=wl_key))

    def _show_file_data_fired(self):
        self.selected.show_file_data()

    def import_data(self):
        tool = AutoSpectrumImportTool(self)
        tool.edit_traits()

    def _selected_default(self):
        return SpectrumMeasurement(main=self.main)

    def _show_binned_fired(self):
        data = self.selected.bin_data()
        view = ArrayViewer(data=data)
        view.edit_traits()

    def _show_signal_fired(self):
        view = ArrayViewer(data=self.selected.signal)
        view.edit_traits()

    def _show_bg_fired(self):
        view = ArrayViewer(data=self.selected.bg)
        view.edit_traits()


    #####       Private Methods      #####
    def _edit_fired(self):
        self.selected.edit_traits()

    def _remove_fired(self):
        self.measurements.remove(self.selected)

    def _plot_selected_fired(self):
        cnt = 0
        for meas in self.measurements:
            if meas.is_selected:
                meas.plot_data()
                cnt+=1
        if not cnt:
            self.selected.plot_data()

    def _select_all_fired(self):
        for exp in self.measurements:
            exp.is_selected = True

    def _unselect_all_fired(self):
        for exp in self.measurements:
            exp.is_selected = False

    def _merge_fired(self):
        def wl_key(spectrum):
            return spectrum.ex_wl,spectrum.em_wl[0]
        for_merge = []
        for meas in self.measurements:
            if meas.is_selected and meas.__kind__=='Spectrum':
                for_merge.append(meas)
        if len(for_merge):
            self.merge_group(sorted(for_merge,key=wl_key))


    #####      Public Methods      #####
    def merge_group(self,for_merge):
        main = for_merge[0]
        rest = for_merge[1:]
        for meas in rest:
            main = merge_spectrums(main, meas)
            self.measurements.remove(meas)
        main.is_selected = False

    def add_measurement(self):
        new = SpectrumMeasurement(main=self.main)
        self.measurements.append(new)
        self.selected = new
        return new

    def save_to_file(self,path):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path,'wb') as f:
            pickle.dump(self.measurements, f)

    def load_from_file(self):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path, 'rb') as f:
            self.measurements = pickle.load(f)

    def make_dataframe(self):
        data = {}
        for exp in self.measurements:
            data[exp.ex_wl] = exp.create_series()
        return pd.DataFrame(data)

    def save_pandas(self,path):
        df = self.make_dataframe()
        result = df.to_csv(path)
        return result

    def plot_1d(self,kind,ax=None,title=''):
        plt.figure()
        for exp in self.measurements:
            if exp.__kind__ == kind:
                exp.plot_data(ax)
        plt.title(title)
        plt.show()

        """
        df = self.make_dataframe()
        ax = df.plot()
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Counts')
        plt.show()
        """


    def plot_2d(self,kind,title=''):
        jet = plt.get_cmap('jet')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for data in self.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                xs = sig[:,0]
                ys = np.array([data.ex_wl]*len(sig[:,0]))
                cNorm = colors.Normalize(vmin=min(sig[:,1]), vmax=max(sig[:,1]))
                scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
                cs = scalarMap.to_rgba(sig[:,1])
                ax.scatter(xs,ys,color=cs)

        plt.title(title)
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Excitation Wavelength')
        plt.show()

    def plot_3d(self,alpha,kind,title=''):
        """

        :return:
        """
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        def cc(arg):
            return colorConverter.to_rgba(arg, alpha=0.6)
        #col_options = [cc('r'), cc('g'), cc('b'), cc('y')]

        verts = []
        colors = []
        zs = []
        wl_range = [3000,0]
        cnt_range = [0,10]
        for data in self.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                #print sig
                if len(sig):
                    zs.append(data.ex_wl)
                    if min(sig[:,1])!=0:
                        sig[:,1] = sig[:,1] - min(sig[:,1])
                    sig[-1, 1] = sig[0, 1] = 0
                    verts.append(sig)
                    colors.append(data.color)
                wl_range = [min(wl_range[0],min(sig[:,0])),max(wl_range[1],max(sig[:,0]))]
                cnt_range = [min(cnt_range[0], min(sig[:, 1])), max(cnt_range[1], max(sig[:, 1]))]
        poly = PolyCollection(verts,closed=False, facecolors=colors) #

        poly.set_alpha(alpha)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        ax.set_xlabel('Emission')
        ax.set_xlim3d(wl_range)
        ax.set_ylabel('Excitation')
        ax.set_ylim3d(min(zs)-10, max(zs)+10)
        ax.set_zlabel('Counts')
        ax.set_zlim3d(cnt_range)
        plt.title(title)
        plt.show()



class ExperimentTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.08, horizontal_alignment='center', ),
                ObjectColumn(name = 'name',label = 'Name',width = 0.25,horizontal_alignment = 'left',editable=True),

                ObjectColumn(name='crystal_name', label='Crystal', width=0.25, horizontal_alignment='left', editable=True),

                ObjectColumn(name = 'ex_wl_range',label = 'Excitation WLs',horizontal_alignment = 'center',
                             width = 0.13,editable=False),

                ObjectColumn(name = 'em_wl_range',label = 'Emission WLs',width = 0.13,
                             horizontal_alignment = 'center',editable=False),
                #ObjectColumn(name = 'em_pol',label = 'Emission POL',width = 0.08,horizontal_alignment = 'center'),

                ObjectColumn(name='measurement_cnt', label='Datasets', width=0.08,
                             horizontal_alignment='center',editable=False),

                ObjectColumn(name='desc', label='Description', width=0.08,
                             horizontal_alignment='center', editable=False),
              ]

    auto_size = True
    sortable = False
    editable = True

