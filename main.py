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
from project import Project, ProjectTableEditor

from saving import CanSaveMixin
from handlers import MainSaveHandler
try:
    import cPickle as pickle
except:
    import pickle



class MainApplication(CanSaveMixin):
    """

    """
    #####       File Menu      #####
    save_a = Action(name = 'Save Workspace', action = 'save')
    save_as_a = Action(name = 'Save As', action = 'saveAs')
    load_all = Action(name = 'Reload', action = 'Reload',enabled_when='filepath')
    load_from_a = Action(name = 'Load from File', action = 'loadProject')
    comp_int_tool = Action(name='Comparison Integration Tool', action='comp_integration_tool')
    exp_int_tool = Action(name='Experiment Integration Tool', action='exp_integration_tool')
    comp_tool = Action(name='Comparison Tool', action='comp_tool')

    #####       Autosave Menu      #####
    cfg_autosave = Action(name = 'Configure Autosave', action = 'cfg_autosave')
    autosave = Bool(False)
    autosaveInterval = Int(300)


    #####       Data      #####
    projects = List(Project)
    selected = Instance(Project)

    #####       UI      #####
    status = Str('Autosave Disabled')
    import_selected = Action(name = 'Add data', action = 'import_selected')
    merge_selected = Action(name = 'Merge Selected', action = 'merge_selected')
    rem_selected = Action(name = 'Remove', action = 'rem_selected')
    add_new = Action(name = 'New Project', action = 'add_new')
    edit = Action(name = 'Open', action = 'edit')



    #edit = Button('Edit')

    #####       GUI View     #####
    traits_view = View(
            HSplit(

                Item(name='projects', show_label=False, editor=ProjectTableEditor(selected='selected',
                    edit_view = View(


                                    Item(name='name', label='Name'),
                                    Item(name='comments', label='Comments', springy=True),


                            )),
                     width=0.35),

            Group(Item(name='selected',show_label=False,style='custom')),

            ),

        title='Spectrum Project Manager',
        scrollable=True,
        resizable=True,
        height=800,
        width=1280,
        handler=MainSaveHandler(),
        menubar=MenuBar(
            Menu(save_a, save_as_a,cfg_autosave, load_all, load_from_a,
                 name='File'),
            Menu(exp_int_tool,comp_tool,comp_int_tool,
                name='Tools'),

                        ),
        toolbar = ToolBar(add_new, rem_selected,edit  ),
        statusbar=[StatusItem(name='status', width=0.5), ],
    )


    #####       Initialization Methods      #####
    def _projects_default(self):
        return [Project(main=self)]

    def _selected_default(self):
        if len(self.projects):
            return self.projects[0]

    #####       Methods      #####
    def _rem_selected(self):
        self.projects.remove(self.selected)

    def _add_new(self):
        new = Project(main=self)
        self.projects.append(new)
        self.selected = new

    def _edit(self):
        self.selected.edit_traits()

    def save(self):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        stat = self.status
        self.status = 'Saving...'
        with open(self.filepath,'wb') as f:
            pickle.dump(self.projects, f)
        self.status = stat

    def load(self):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        with open(self.filepath, 'rb') as f:
            self.projects = pickle.load(f)

    def _anytrait_changed(self):
        self.dirty = True

if __name__ == '__main__':
    app = MainApplication()
    app.configure_traits()