from traits.api import *
from traitsui.api import *
from saving import BaseSaveHandler
from pyface.api import FileDialog, confirm, error, YES, CANCEL


class MainSaveHandler(BaseSaveHandler):
    extension = Str('ws')
    def cfg_autosave(self,info):
        autosave_cfg_view = View(
            VGroup(Item(name='autosave', label='Autosave Enabled', ),
                   Item(name='autosaveInterval', label='Autosave Interval',enabled_when='autosave' ),
                   ),
            title='Configure Auto-save',
            buttons=['OK'],
            kind='live'

        )
        info.object.edit_traits(view=autosave_cfg_view)

    def object_autosave_changed(self,info):
        self.autosave = info.object.autosave
        if info.object.autosave:

            if info.object.filepath=='':

                fileDialog = FileDialog(action='save as', title='Save As',
                                        wildcard=self.wildcard,
                                        parent=info.ui.control)
                fileDialog.open()
                if fileDialog.path == '' or fileDialog.return_code == CANCEL:
                    info.object.autosave = False
                    return False
                else:
                    extLen = len(self.extension)
                    if extLen and fileDialog.path[-extLen-1:] != '.' + self.extension:
                        fileDialog.path += '.' + self.extension
                    self.saveObject.filepath = fileDialog.path
            info.object.status = 'Autosave Enabled. Will save every %d seconds to: %s' \
                                % (info.object.autosaveInterval, info.object.filepath)
        else:
            info.object.status = 'Autosave Disabled.'

    def comp_integration_tool(self,info):
        info.object.selected.comparison_integration_tool()

    def exp_integration_tool(self,info):
        info.object.selected.experiment_integration_tool()

    def comp_tool(self,info):
        info.object.selected.comparison_tool()

    def plot_tool(self, info):
        info.object.selected.plotting_tool()

    def object_autosaveInterval_changed(self,info):
        self.autosaveInterval = info.object.autosaveInterval
        info.object.status = 'Autosave Enabled. Will save every %d seconds to: %s' \
                             % (info.object.autosaveInterval, info.object.filepath)


class ProjectHandler(BaseSaveHandler):
    extension = Str('prj')


class CrystalHandler(BaseSaveHandler):
    extension = Str('crystal')


class MeasurementHandler(BaseSaveHandler):
        extension = Str('meas')

        def add_data(self,info):
            fileDialog = FileDialog(action='save as', title='Save As',
                                    wildcard=self.wildcard,
                                    parent=info.ui.control)

            fileDialog.open()
            if fileDialog.path == '' or fileDialog.return_code == CANCEL:
                return False
            else:
                info.object.load_from_file(fileDialog.path)

