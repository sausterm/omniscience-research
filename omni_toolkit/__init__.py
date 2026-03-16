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

Mixing:
    mixing.epsilon_geometry    - Geometric ε = 1/√(2·dim_fibre)
    mixing.vacuum_alignment    - Sp(1) breaking on S²
    mixing.mixing_matrix       - CKM/PMNS from ε + FN charges

Fermions:
    fermions.yukawa_coupling   - Ric(V-,V+) → Yukawa, b/a ratio
    fermions.fermion_spectrum  - Froggatt-Nielsen mass hierarchy
    fermions.neutrino_sector   - Seesaw mechanism

Breaking:
    breaking.breaking_chain    - Multi-step G → H₁ → H₂ → ...
    breaking.moduli_space      - CP³ = SU(4)/U(3) moduli
    breaking.branching_rule    - Representation decomposition

Applications:
    applications.pati_salam - GL+(4)/SO(3,1) → Pati-Salam instantiation
"""

__version__ = "0.1.0"
