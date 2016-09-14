import os
from traits.api import *
from traitsui.api import *
from traitsui.extras.checkbox_column import CheckboxColumn
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np
import random
import pandas as pd


class DictEditor(HasTraits):

    Object = Instance( object )
    def __init__(self, obj, **traits):
        super(DictEditor, self).__init__(**traits)
        self.Object = obj

    def trait_view(self, name=None, view_elements=None):
        return View(
          VGroup(
            Item('Object',
                  label      = 'Debug',
                  id         = 'debug',
                  editor     = ValueEditor(), #ValueEditor()
                  style      = 'custom',
                  dock       = 'horizontal',
                  show_label = False),),
          title     = 'Dictionary Editor',
          width     = 800,
          height    = 600,
          resizable = True)


class _MPLFigureEditor(Editor):

   scrollable  = True

   def init(self, parent):
       self.control = self._create_canvas(parent)
       self.set_tooltip()

   def update_editor(self):
       pass

   def _create_canvas(self, parent):
       """ Create the MPL canvas. """
       # matplotlib commands to create a canvas
       mpl_canvas = FigureCanvas(self.value)
       return mpl_canvas

class MPLFigureEditor(BasicEditorFactory):

   klass = _MPLFigureEditor