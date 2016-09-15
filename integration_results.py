import os
from traits.api import *
from traitsui.api import *
from traitsui.ui_editors.array_view_editor import ArrayViewEditor

class IntegrationResultBase(HasTraits):
    name = Str('Results')
    int_range = Tuple((0.0,0.0),labels=['Min','Max'],cols=2)
    results = Array()

class ComparisonIntegrationResult(HasTraits):
    view = View(
        Group(
            Item(name='int_range', label='Integration Range', style='readonly'),
            Item('results',
                 show_label=False,
                 editor=ArrayViewEditor(titles=['Excitation WL', 'Counts 1st', 'Counts 2nd', 'Counts Subtraction'],
                                        format='%.1f',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        )),

        ),





    )



class ExperimentIntegrationResult(HasTraits):
    view = View(
        Group(
            Item(name='int_range', label='Integration Range', style='readonly'),
            Item('results',
                 show_label=False,
                 editor=ArrayViewEditor(titles=['Excitation WL', 'Counts Signal', 'Counts BG', 'Counts REF'],
                                        format='%.1f',
                                        show_index=False,
                                        # Font fails with wx in OSX;
                                        #   see traitsui issue #13:
                                        # font   = 'Arial 8'
                                        )),

        ),





    )
