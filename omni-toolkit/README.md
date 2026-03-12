# omni-toolkit

Non-perturbative geometric toolkit for symmetric space physics.

Given a background metric of any signature and dimension, computes the DeWitt supermetric,
Ricci curvature, eigendecomposition into positive/negative norm subspaces, and identifies
the resulting gauge group structure.

## Install

```bash
cd omni-toolkit
pip install -e .
```

## Quick Start

```python
import numpy as np
from omni_toolkit.core import SymmetricSpace, RicciTensor, EigenDecomposition

# Define a background metric (any signature)
eta = np.diag([-1, 1, 1, 1])  # Lorentzian 4D

# Build the symmetric space GL+(4)/SO(3,1)
space = SymmetricSpace(eta)
print(f"Fibre dimension: {space.dim_fibre}")   # 10
print(f"DeWitt signature: {space.signature}")   # (6, 4)

# Compute Ricci tensor (two independent methods)
ricci = RicciTensor(space)
print(f"Scalar curvature: {ricci.scalar_curvature}")  # -30.0
print(f"Methods agree: {ricci.methods_agree}")          # True

# Identify gauge group from signature
reps = EigenDecomposition(space)
print(reps.maximal_compact_subgroup()['description'])
# SO(6) x SO(4) = SU(4) x SU(2)_L x SU(2)_R [Pati-Salam]
```

## Modules

### `core/` — Symmetric space geometry
- **`LieAlgebra`** — Bracket, Killing form, adjoint representation, structure constants
- **`SymmetricSpace`** — G/H construction from background metric, DeWitt metric, V+/V- eigendecomposition
- **`DeWittMetric`** — The supermetric G(h,k) on symmetric 2-tensors
- **`RicciTensor`** — Ricci via Killing form and double commutator, sectional curvature
- **`EigenDecomposition`** — Stabilizer algebra, adjoint action, maximal compact subgroup

### `dynamics/` — Gauge coupling evolution
- **`BetaSystem`** — 1-loop and 2-loop beta function systems
- **`RGRunner`** — RK4 integrator, analytic 1-loop, multi-scale solvers
- **`ColemanWeinberg`** — Effective potential for radiative symmetry breaking

### `topology/` — Topological structures
- **`QuaternionicStructure`** — Complex/quaternionic structures on vector spaces
- **`GenerationCounter`** — Fermion generation counting from quaternionic structure

## Works with any G/H

The toolkit is parametric — it works for any background metric, not just particle physics:

```python
# 3D Euclidean: elastic deformation space (DTI, elasticity)
eta_3d = np.diag([1, 1, 1])
space_3d = SymmetricSpace(eta_3d)  # GL+(3)/SO(3), 6D fibre

# 2D Lorentzian: conformal structure
eta_2d = np.diag([-1, 1])
space_2d = SymmetricSpace(eta_2d)  # GL+(2)/SO(1,1), 3D fibre
```

## Tests

```bash
python -m omni_toolkit.tests.test_core
```

## Citation

If you use this toolkit, please cite:

```bibtex
@software{austermann2026omni,
  author = {Austermann, Sloan},
  title = {omni-toolkit: Geometric toolkit for symmetric space physics},
  year = {2026},
  url = {https://github.com/sausterm/omniscience-research},
  note = {Part of the Metric Bundle Programme}
}
```

See also: [Paper 1 (Gauge Structure from the Metric Bundle)](https://doi.org/10.5281/zenodo.18860687)

## License

MIT. Copyright (c) 2026 OmniSciences LLC.
