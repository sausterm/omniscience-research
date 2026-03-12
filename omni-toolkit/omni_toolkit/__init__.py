"""
omni-toolkit: Non-perturbative geometric toolkit for symmetric space physics.

Abstracts the mathematical machinery of the Metric Bundle Programme into
general-purpose components parametrized by arbitrary G/H symmetric spaces.

Core modules:
    core.lie_algebra       - Lie algebra structure, Killing form
    core.symmetric_space   - G/H symmetric spaces, DeWitt metric
    core.curvature         - Ricci tensor, sectional curvature
    core.representations   - Eigendecomposition, subgroup analysis

Dynamics:
    dynamics.rg_running         - RG beta functions, scale evolution
    dynamics.effective_potential - Coleman-Weinberg potential

Topology:
    topology.complex_structures - Complex/quaternionic structures
    topology.index_theorem      - Index computations

Copyright (c) 2026 OmniSciences LLC. MIT License.
"""

__version__ = "0.1.0"
