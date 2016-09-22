import os
from traits.api import *
from traitsui.api import *
from traitsui.ui_editors.array_view_editor import ArrayViewEditor
from pyface.api import FileDialog, confirm, error, YES, CANCEL
import numpy as np
from saving import BaseSaveHandler
from auxilary_functions import data_array_to_text_file


class IntegrationResultBaseHandler(BaseSaveHandler):
    #extension = Str('int')
    promptOnExit = False

    def object_save_data_changed(self, info):
        fileDialog = FileDialog(action='save as', title='Save As',
                                wildcard=self.wildcard,
                                parent=info.ui.control,
                                default_filename=info.object.name+'_integration')

        fileDialog.open()
        if fileDialog.path == '' or fileDialog.return_code == CANCEL:
            return False
        else:
            range_data='Integration Range: %d to %d nm' %(info.object.int_range[0],info.object.int_range[1])
            data_array_to_text_file(path=fileDialog.path,array=info.object.results,
                                    headers=info.object.headers,table_fmt=info.object.table_fmt,
                                    float_fmt=info.object.float_fmt,first_line=range_data)


class IntegrationResultBase(HasTraits):
    name = Str('Results')
    int_range = Tuple((0.0,0.0),labels=['Min','Max'],cols=2)
    results = Array()

class ComparisonIntegrationResult(IntegrationResultBase):
    headers = ['Excitation WL', 'Counts 1st', 'Counts 2nd', 'Counts Subtraction']
    save_data = Button('Export Data') #Action(name = 'Export', action = 'save_data')
    table_fmt = Enum(['plain', 'simple', 'grid', 'fancy_grid', 'pipe','orgtbl','rst','mediawiki','html', 'latex', 'latex_booktabs'])
    fmt = Str('e')
    ndec = Int(2)
    float_fmt = Property(Str)


    view = View(
        VGroup(
            HGroup(Item(name='int_range', label='Integration Range', style='readonly'),
                   ),
            HGroup(
                Item(name='save_data', editor=ButtonEditor(label='Export Data')),
                Item(name='table_fmt', label='Table Format'),
                Item(name='fmt',editor=EnumEditor(values={'f':'Regular', 'e':'Exponential'}), label='Number Format'),
                Item(name='ndec', label='Decimals'),
            ),

            Group(Item('results',
                 show_label=False,
                 editor=ArrayViewEditor(titles=['Excitation WL', '1st Exp. (BG corrected)', '2nd Exp. (BG corrected)', 'Subtraction (BG corrected)'],
                                        format='%.2e',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        )),
                  show_border=True,label='Results'),

        ),



    handler=IntegrationResultBaseHandler(),
    resizable=True,
    scrollable=True,
    )

    def _get_float_fmt(self):
        return '.{}{}'.format(self.ndec,self.fmt)

    def _results_default(self):
        return np.asarray([[0.0,0.0,0.0,0.0]]*4)

class ExperimentIntegrationResult(IntegrationResultBase):
    headers = ['Excitation WL', 'Signal (Counts)', 'BG (Counts)','Signal-BG', 'REF (Counts)']
    save_data = Button('Export Data') #Action(name = 'Export Data', action = 'save_data')
    table_fmt = Enum(['plain', 'simple', 'grid', 'fancy_grid', 'pipe','orgtbl','rst','mediawiki','html', 'latex', 'latex_booktabs'])
    fmt = Str('e')
    ndec = Int(2)
    float_fmt = Property(Str)


    view = View(
        VGroup(
            HGroup(Item(name='int_range', label='Integration Range', style='readonly'),

                   ),
            HGroup(
                Item(name='save_data', editor=ButtonEditor(label='Export Data')),
                Item(name='table_fmt', label='Table Format'),
                Item(name='fmt', editor=EnumEditor(values={'f':'Regular', 'e':'Exponential'}), label='Number Format'),
                Item(name='ndec', label='Decimals'),


            ),
            Group(Item('results',
                 editor=ArrayViewEditor(titles=['Excitation WL', 'Signal (Counts)', 'BG (Counts)','Signal-BG', 'REF (Counts)'],
                                        format='%.2e',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        ),show_label=False),

                  show_border=True, label='Results'),


                ),
    handler = IntegrationResultBaseHandler(),
    )

    def _get_float_fmt(self):
        return '.{}{}'.format(self.ndec,self.fmt)

    def _results_default(self):
        return np.asarray([[0.0,0.0,0.0,0.0]]*4)