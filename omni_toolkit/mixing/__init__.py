"""
Mixing matrices and flavor structure from fibre geometry.

Provides:
  - EpsilonGeometry: geometric derivation of ε = 1/√(2·dim_fibre)
  - VacuumAlignment: Sp(1) breaking on S² and Froggatt-Nielsen charges
  - MixingMatrix: parametric CKM/PMNS from ε + FN charges
"""

from .epsilon_geometry import EpsilonGeometry
from .vacuum_alignment import VacuumAlignment
from .mixing_matrix import MixingMatrix

__all__ = ['EpsilonGeometry', 'VacuumAlignment', 'MixingMatrix']
