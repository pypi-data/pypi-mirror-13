import os as _os
_on_rtd = _os.environ.get('READTHEDOCS', None) == 'True'
if not _on_rtd:
    pass


class BeamBase(object):
    def __init__(self, nb0, E=20.35, dE=0.01):
        self._nb0 = nb0
        self._E   = E
        self._dE  = dE

    @property
    def nb0(self):
        """
        On-axis beam density.
        """
        return self._nb0

    @property
    def E(self):
        """
        Beam energy in GeV.
        """
        return self._E

    @property
    def dE(self):
        """
        Beam energy spread.
        """
        return self._dE


class RoundBeam(BeamBase):
    def __init__(self, nb0, s_r, E=20.35, dE=0.01):
        super().__init__(nb0=nb0, E=E, dE=dE)
        self._s_r = s_r

    @property
    def s_r(self):
        return self._s_r
