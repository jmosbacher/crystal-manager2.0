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
import numpy as np
import random
import pandas as pd
from file_selector import FileSelectionTool, FolderSelectionTool
from measurement import SpectrumMeasurement, BaseMeasurement
from auxilary_functions import color_map, wl_to_rgb, organize_data, read_ascii_file,import_group, import_folder
#from crystal import Crystal
from pyface.api import confirm, error, YES, CANCEL
try:
    import cPickle as pickle
except:
    import pickle


class AutoImportToolHandler(Handler):

    def import_data(self,info,group):
        org_data = info.object.import_data(group)
        if org_data is not None:
            if len(org_data):
                code = confirm(info.ui.control, 'Data imported successfully, continue importing? Press Cancel to discard data',
                               title="Import more data?", cancel=True)

                if code == CANCEL:
                    return
                else:
                    info.object.store_data(org_data)
                    if code == YES:
                        return
                    else:
                        info.ui.dispose()
        else:
            error(None, 'Data extraction unsuccessful', title='No Data')

    def object_import_all_changed(self,info):
        self.import_data(info,info.object.selector.filtered_names)


    def import_selected_changed(self,info):
        self.import_data(info,info.object.selector.selected)


class AutoImportToolBase(HasTraits):
    experiment = Any() #Instance(Crystal)
    selector = Instance(FileSelectionTool)
    delimiter = Str(' ')
    data_folder = Str('ascii')
    #mode = Enum(['New Measurement', 'Append to Selected'])
    import_selected = Button(name='Import Selected',action='import_selected_fired')
    import_all = Button(name='Import All')
    folders = Bool(False)

    view = View(
        VGroup(
        Group(
            Item(name='selector',show_label=False,style='custom'),
        show_border=True,label='Files to import'),
        HGroup(
            Item(name='delimiter', label='Delimiter', ),
            Item(name='data_folder', label='Data Folder',enabled_when='folders==True' ),
            Item(name='import_selected', show_label=False, ),
            Item(name='import_all', show_label=False, ),
        ),
        ),
        buttons=['OK'],
        kind='modal',
        handler=AutoImportToolHandler(),
    )


    def __init__(self):
        raise NotImplementedError

    def _selector_default(self):
        raise NotImplementedError

    def store_data(self,org_data):
        raise NotImplementedError

    def import_data(self, group):
        raise NotImplementedError

class AutoSpectrumImportTool(AutoImportToolBase):
    def __init__(self, experiment):
        HasTraits.__init__(self)
        self.experiment = experiment
        #self.kind = 'Spectrum'

    def _selector_default(self):
        return FileSelectionTool()

    def import_data(self, group):
        org_data = import_group(self.selector.dir,group,delimiter=self.delimiter)
        return org_data

    def store_data(self, org_data):
        for name, data in org_data.items():
            new = self.experiment.add_new()
            new.name = name
            try:
                ex_wl = eval(name.split('in')[0])
                if isinstance(ex_wl, (float, int)):
                    new.ex_wl = ex_wl
            except:
                pass
            new.signal = data.get('sig', ([], []))[0]
            new.bg = data.get('bgd', ([], []))[0]
            new.ref = data.get('ref', ([], []))[0]
            new.file_data = {}
            new.file_data['sig'] = data.get('sig', ([], []))[1]
            new.file_data['bgd'] = data.get('bgd', ([], []))[1]
            new.file_data['ref'] = data.get('ref', ([], []))[1]


class AutoExperimentImportTool(AutoImportToolBase):
    project = Any() #Instance(Crystal)

    def __init__(self, project):
        HasTraits.__init__(self)
        self.project = project
        self.folders = True

    def _selector_default(self):
        return FolderSelectionTool()

    def import_data(self, group):
        all_data = {}
        for name in group:
            path = os.path.join(self.selector.dir,[name,self.data_folder])
            all_data[name] = import_folder(path,delimiter=self.delimiter)
        return all_data

    def store_data(self,all_data):
        for f_name, org_data in all_data.items():
            experiment = self.project.add_new()
            experiment.name = f_name
            experiment.crystal_name = '_'.join(f_name.split('_')[1:3])
            for name, data in org_data.items():
                new = experiment.add_new()
                new.name = name
                try:
                    ex_wl = eval(name.split('in')[0])
                    if isinstance(ex_wl, (float, int)):
                        new.ex_wl = ex_wl
                except:
                    pass
                new.signal = data.get('sig',([],[]))[0]
                new.bg = data.get('bgd', ([],[]))[0]
                new.ref = data.get('ref', ([],[]))[0]
                new.file_data = {}
                new.file_data['sig'] = data.get('sig', ([], []))[1]
                new.file_data['bgd'] = data.get('bgd', ([], []))[1]
                new.file_data['ref'] = data.get('ref', ([], []))[1]
