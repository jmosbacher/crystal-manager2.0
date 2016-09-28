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
from experiment import SpectrumExperiment
from measurement import SpectrumMeasurement
from saving import CanSaveMixin
from handlers import MainSaveHandler
from traitsui.qt4.tree_editor \
    import NewAction, CopyAction, CutAction, \
           PasteAction, DeleteAction, RenameAction


class WorkSpace(HasTraits):
    name = Str('New Worksapce')
    projects = List(Project)
    selected = Instance(Project)



project_tree_editor = TreeEditor(

    nodes=[
        TreeNode(node_for=[WorkSpace],
                 auto_open=True,
                 children='projects',
                 label='name',
                 view=View(Group('name',
                                 orientation='vertical',
                                 show_left=True))),

        TreeNode(node_for=[Project],
                 auto_open=True,
                 children='experiments',
                 label='=Experiments',

                 add=[SpectrumExperiment]),

        TreeNode(node_for=[SpectrumExperiment],
                 auto_open=True,
                 children='measurements',
                 label='name',


                 add=[SpectrumMeasurement]),
        TreeNode(node_for=[SpectrumMeasurement],
                 auto_open=True,
                 label='name',

                                )
    ]

)

'''
                 menu=Menu(NewAction,
                           Separator(),
                           CopyAction,
                           CutAction,
                           PasteAction,
                           Separator(),
                           DeleteAction,
                           Separator(),
                           RenameAction),
'''
### Unit Tests ###



class Blah(HasTraits):
    workspace = Instance(WorkSpace)

    view = View(Item('workspace',editor=project_tree_editor))

    def _workspace_default(self):
        work = WorkSpace()
        projects = [Project(name='Project 1'), Project(name='Project 2'), Project(name='Project 3')]
        for project in projects:
            for name in ['Exp 1', 'Exp 2', 'Exp 3']:
                exp = project.add_new_experiment()
                exp.name = name
                for namee in ['Meas 1', 'Meas 2', 'Meas 3']:
                    meas = exp.add_measurement()
                    meas.name = namee
        work.projects = projects
        return work

test = Blah()
test.configure_traits()
