__all__ = [
    'Imshow_Slider',
    'Imshow_Slider_Array',
    'NonUniformImage',
    'NonUniformImage_axes',
    'RectangleSelector',
    'addlabel',
    'axesfontsize',
    'colorbar',
    'contour',
    'figure',
    'hist',
    'hist2d',
    'imshow',
    'imshow_batch',
    'latexfig',
    'less_labels',
    'pcolor_axes',
    'plot',
    'plot_featured',
    'quiver',
    'rgb2gray',
    'savefig',
    'scaled_figsize',
    'setup_axes',
    'setup_figure',
    'showfig',
    ]
__all__.sort()

import os as _os
on_rtd = _os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:
    from .cmaps import *  # noqa
    __all__.sort()

from .Imshow_Slider_mod import Imshow_Slider
from .Imshow_Slider_Array_mod import Imshow_Slider_Array
from .NonUniformImage import NonUniformImage
from .NonUniformImage_axes import NonUniformImage_axes
from .RectangleSelector_mod import RectangleSelector
from .addlabel import addlabel
from .axesfontsize import axesfontsize
from .colorbar import colorbar
from .figure import figure
from .hist import hist
from .hist2d import hist2d
from .imshow import contour
from .imshow import imshow
from .imshow import quiver
from .imshow import scaled_figsize
from .imshow_batch import imshow_batch
from .latexfig import latexfig
from .less_labels import less_labels
from .pcolor_axes import pcolor_axes
from .plot import plot
from .plot_featured import plot_featured
from .rgb2gray import rgb2gray
from .savefig import savefig
from .setup_axes import setup_axes
from .setup_figure import setup_figure
from .showfig import showfig
