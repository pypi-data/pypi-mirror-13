class SciImage(object):
    def __init__(self, im, cb, cax):
        self._im = im
        self._cb = cb
        self._cax = cax

    @property
    def im(self):
        return self._im

    @property
    def cb(self):
        return self._cb

    @property
    def cax(self):
        return self._cax
