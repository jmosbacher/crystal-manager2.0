from traits.api import *
from traitsui.api import *
from traitsui.ui_editors.array_view_editor import ArrayViewEditor
from data_plot_viewers import DataPlotEditorBase
import matplotlib.pyplot as plt
from experiment import SpectrumExperiment,BaseExperiment, ExperimentNameTableEditor
from measurement import SpectrumMeasurement
from compare_experiments import ExperimentComparison
from data_plot_viewers import FittingDataPlotEditor
import numpy as np
from scipy.optimize import curve_fit
from fitters import SpectrumFitter1D



class FittingToolBase(HasTraits):
    project = Any()
    experiments = List(BaseExperiment)
    selected = Instance(BaseExperiment)
    fits_list = Array() #DelegatesTo('selected')
    #fitter = Instance(SpectrumFitter)


    #use_fit = Bool(False)

    #####       Plots     #####
    display = Instance(FittingDataPlotEditor)

    #####       GUI     #####
    perform_fit = Button('Fit Range')
    integrate = Button('Integrate Selections')
    clear = Button('Clear Selections')
    clear_fits = Button('Clear Fits')
    refresh = Button('Refresh View')
    save = Button('Save Results')
    editing = DelegatesTo('display')
    message = Str(' ')
    has_peaks = Property(Bool)
    has_xrange = Property(Bool)


    view = View(
        HSplit(
            VGroup(
                HGroup(
                        Item(name='perform_fit', show_label=False, ),
                        #Item(name='integrate', show_label=False, ),
                       #Item(name='use_fit', label='Fit Data', ),
                        Item(name='message', style='readonly', show_label=False,springy=True),
                       show_border=True, label='Control'),

                HGroup(
                    Item(name='editing', style='custom', label='Edit', ),
                    Item(name='clear', show_label=False, ),
                    Item(name='clear_fits', show_label=False, ),
                    Item(name='refresh', show_label=False),
                    show_border=True, label='Region Selection'
                ),
                Group(Item(name='display', style='custom', show_label=False),
                      show_border=True, label='Plots'),

            ),

            VGroup(
                Group(Item(name='experiments', show_label=False, editor=ExperimentNameTableEditor(selected='selected')),
                      show_border=True, label='Experiments'),
                Group(Item(name='fits_list', show_label=False, editor=ArrayViewEditor(
                                                                titles = [ 'Wavelength', 'Amplitude','Mean',
                                                                           'Sigma', 'Integral', ],
                                                                format = '%g',

                                                                show_index= False,)),
                      show_border=True, label='Fits',scrollable=True),

            ),

        ),
        buttons=['OK'],
        title='Fitting Tool',
        kind='live',

        scrollable=True,
        resizable=True,
        height=800,
        width=1200,
    )


    def __init__(self,project):
        super(FittingToolBase, self).__init__()
        self.project = project
        self.experiments = project.experiments

    def _display_default(self):
        return FittingDataPlotEditor()

    def _fits_list_default(self):
        return np.asarray([[0.0,0.0,0.0,0.0, 0.0]])


    def _perform_fit_fired(self):
        if self.has_peaks and self.has_xrange:
            self.message = ' '
        else:
            if self.has_peaks:
                self.message='Please select a Fit Range'
            elif self.has_xrange:
                self.message = 'Please select Peaks'
            else:
                self.message = 'Please select Peaks and a Fit Range '
            return
        peaks = []
        for xmin,xmax in self.display.peaks:
            if xmax-xmin>1:
                peaks.append((xmin,xmax))
        fitter = SpectrumFitter1D(peaks=peaks)
        xrange = self.display.xrange
        for meas in self.selected.measurements:
            data = meas.bg_corrected()
            data = data[np.where(np.logical_and(data[:,0]>=xrange[0],data[:,0]<=xrange[1]))]
            fitter.xdata, fitter.ydata = data[:,0], data[:,1]
            fitter.perform_fit()
            if fitter.fit_success:
                for fit in fitter.p.reshape(fitter.nexp,3):
                    meas.fits.append(fit)
        self.refresh_display()

    def _clear_fits_fired(self):
        for meas in self.selected.measurements:
            meas.fits = []
        self.refresh_display()

    def _get_has_peaks(self):
        if self.display is None:
            return False
        if len(self.display.peaks):
            return True
        else:
            return False

    def _get_has_xrange(self):
        if self.display is None:
            return False
        if (self.display.xrange[1]-self.display.xrange[0])>10:
            return True
        else:
            return False


    def _refresh_fired(self):
        self.refresh_display()

    def _selected_changed(self):
        self.display.xrange = self.selected.em_wl_range
        self.refresh_display()

    def _clear_fired(self):
        self.display.clear_selections()
        self.refresh_display()
        self.display.configure_selector(peaks=True)

    def refresh_display(self):
        self.fits_list = self.selected.fits_list
        self.display.remove_subplots()
        self.display.add_subplots(self.display.nplots)
        if len(self.display.axs):
            for meas in self.selected.measurements:
                meas.plot_data(ax=self.display.axs[0], legend=False)
                meas.plot_fits(ax=self.display.axs[1], legend=False, xrange=self.display.xrange)
        self.set_titles()
        self.display.draw()
        self.display.configure_selector()

    def set_titles(self):
        self.display.set_title(self.selected.name,size=14)
        if len(self.display.axs):
            self.display.axs[0].set_title('BG Corrected Data', fontsize=12)
            self.display.axs[1].set_title('Fits', fontsize=12)

            self.display.axs[0].set_xlabel('')
            self.display.axs[1].set_xlabel('Emission Wavelength')
            self.display.axs[0].set_ylabel('Counts')
            self.display.axs[1].set_ylabel('Counts')


