import os as _os
_on_rtd = _os.environ.get('READTHEDOCS', None) == 'True'
if not _on_rtd:
    import numpy as _np


def keys(obj):
    """
    Returns an array of strings of the keys like Python 2 used to do.

    .. versionadded:: 1.4

    Parameters
    ----------

    obj : object
        Object to get keys from.

    Returns
    -------
    
    keys : list
        List of keys.
    """
    return [key for key in obj.keys()]


def get(f, key, default=None):
    """
    Gets an array from datasets.

    .. versionadded:: 1.4
    """

    if key in f.keys():
        val = f[key].value

        if default is None:
            return val
        else:
            if _np.shape(val) == _np.shape(default):
                return val

    return default
