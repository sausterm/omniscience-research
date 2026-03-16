"""
Fermion spectrum and Yukawa couplings from fibre geometry.

Provides:
  - YukawaCoupling: tree-level Yukawa from Ric(V-, V+), b/a ratio
  - FermionSpectrum: mass hierarchy from Froggatt-Nielsen mechanism
  - NeutrinoSector: seesaw mechanism, Majorana masses
"""

from .yukawa_coupling import YukawaCoupling
from .fermion_spectrum import FermionSpectrum
from .neutrino_sector import NeutrinoSector

__all__ = ['YukawaCoupling', 'FermionSpectrum', 'NeutrinoSector']
