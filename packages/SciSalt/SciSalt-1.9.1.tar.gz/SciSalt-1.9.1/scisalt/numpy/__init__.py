"""
The :mod:`numpy <scisalt.numpy>` module contains a few convenience functions mostly designed to make evaluating functions easier for plotting.
"""
__all__ = [
    'frexp10',
    'gaussian',
    'linspaceborders',
    'linspacestep',
    'piecewise',
    ]

__all__.sort()

from .frexp10 import *
from .functions import gaussian
from .linspaceborders import *
from .linspacestep import *
from .piecewise import piecewise
