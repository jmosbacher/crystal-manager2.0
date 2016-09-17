import os
from traits.api import *
from traitsui.api import *
from traitsui.ui_editors.array_view_editor import ArrayViewEditor
from pyface.api import FileDialog, confirm, error, YES, CANCEL
import numpy as np
from saving import BaseSaveHandler
from auxilary_functions import data_array_to_text_file


class IntegrationResultBaseHandler(BaseSaveHandler):
    extension = Str('int')

    def object_save_data_changed(self, info):
        fileDialog = FileDialog(action='save as', title='Save As',
                                wildcard=self.wildcard,
                                parent=info.ui.control)

        fileDialog.open()
        if fileDialog.path == '' or fileDialog.return_code == CANCEL:
            return False
        else:
            data_array_to_text_file(path=fileDialog.path,array=info.object.results,headers=info.object.headers,fmt=info.object.save_fmt)


class IntegrationResultBase(HasTraits):
    name = Str('Results')
    int_range = Tuple((0.0,0.0),labels=['Min','Max'],cols=2)
    results = Array()

class ComparisonIntegrationResult(IntegrationResultBase):
    headers = ['Excitation WL', 'Counts 1st', 'Counts 2nd', 'Counts Subtraction']
    save_data = Button('Export Data') #Action(name = 'Export', action = 'save_data')
    save_fmt = Enum(['plain', 'simple', 'grid', 'fancy_grid', 'pipe','orgtbl','rst','mediawiki','html', 'latex', 'latex_booktabs'])

    view = View(
        VGroup(
            HGroup(Item(name='int_range', label='Integration Range', style='readonly'),
                   ),
            HGroup(
                Item(name='save_data', editor=ButtonEditor(label='Export Data')),
                Item(name='save_fmt', label='Format'),
            ),
            Group(Item('results',
                 show_label=False,
                 editor=ArrayViewEditor(titles=['Excitation WL', 'Counts 1st', 'Counts 2nd', 'Counts Subtraction'],
                                        format='%g',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        )),
                  show_border=True,label='Results'),

        ),



    handler=IntegrationResultBaseHandler(),

    )

    def _results_default(self):
        return np.asarray([[0.0,0.0,0.0,0.0]]*4)

class ExperimentIntegrationResult(IntegrationResultBase):
    headers = ['Excitation WL', 'Counts Signal', 'Counts BG', 'Counts REF']
    save_data = Button('Export Data') #Action(name = 'Export Data', action = 'save_data')
    save_fmt = Enum(['plain', 'simple', 'grid', 'fancy_grid', 'pipe','orgtbl','rst','mediawiki','html', 'latex', 'latex_booktabs'])

    view = View(
        VGroup(
            HGroup(Item(name='int_range', label='Integration Range', style='readonly'),

                   ),
            HGroup(
                Item(name='save_data', editor=ButtonEditor(label='Export Data')),
                Item(name='save_fmt', label='Format'),
            ),
            Group(Item('results',
                 editor=ArrayViewEditor(titles=['Excitation WL', 'Counts Signal', 'Counts BG', 'Counts REF'],
                                        format='%g',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        ),show_label=False),

                  show_border=True, label='Results'),


                ),
    handler = IntegrationResultBaseHandler(),
    )

    def _results_default(self):
        return np.asarray([[0.0,0.0,0.0,0.0]]*4)