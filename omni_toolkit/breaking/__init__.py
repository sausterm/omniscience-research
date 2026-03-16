"""
Symmetry breaking chains and moduli spaces from fibre geometry.

Provides:
  - BreakingChain: multi-step breaking G → H₁ → H₂ → ... with moduli
  - ModuliSpace: CP³ = SU(4)/U(3) stabilization, holomorphic sectional curvature
  - BranchingRule: representation decomposition under subgroup restriction
"""

from .breaking_chain import BreakingChain, BreakingStep
from .moduli_space import ModuliSpace
from .branching_rule import BranchingRule

__all__ = ['BreakingChain', 'BreakingStep', 'ModuliSpace', 'BranchingRule']
