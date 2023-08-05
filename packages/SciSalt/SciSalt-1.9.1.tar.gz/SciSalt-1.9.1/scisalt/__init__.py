# Author: Joel Frederico
"""
This project has slowly grown from frequently-used code snippets. The main objective is to create a collection of interconnected methods frequently needed to visualize and analyze data using `NumPy <http://www.numpy.org/>`_, `SciPy <http://www.scipy.org/>`_, `Matplotlib <http://matplotlib.org/>`_, and `PyQt4 <http://www.riverbankcomputing.com/software/pyqt/download>`_.
"""
__version__ = '1.9.1'
from . import accelphys
from . import facettools
from . import logging
from . import matplotlib
from . import numpy
from . import scipy
from . import utils
from . import PWFA


# ============================
# Check if master, dev, or tag
# ============================
# import git as _git
# import os as _os
# 
# _path = _os.path.dirname(_os.path.dirname(__file__))
# 
# def _test_git():
#     try:
#         _repo = _git.Repo(_path)
#         _hexsha = _repo.head.object.hexsha
# 
#         if _repo.is_dirty():
#             import warnings as _warnings
#             _warnings.warn('SciSalt repo is dirty, version not well-defined.', category=SyntaxWarning, stacklevel=3)
#     
#         for _tag in _repo.tags:
#             if _tag.object.hexsha == _hexsha:
#                 return
#     
#         import warnings as _warnings
#         _warnings.warn('SciSalt not currently on a tag, version not well-defined. Head: {}'.format(_repo.head.ref.name), category=SyntaxWarning, stacklevel=3)
#     except _git.InvalidGitRepositoryError:
#         pass
# 
# _test_git()
