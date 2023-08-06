import os as _os
_on_rtd = _os.environ.get('READTHEDOCS', None) == 'True'
if not _on_rtd:
    import numpy as _np


def piecewise(x, condlist, funclist, *args, **kw):
    x = _np.array([x], dtype=float).flatten()

    return _np.piecewise(x, condlist, funclist, *args, **kw)
