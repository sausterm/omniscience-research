# omni-toolkit

Non-perturbative geometric toolkit for symmetric space physics. Computes DeWitt supermetric signatures, Ricci tensors, gauge group identifications, RG running, and effective potentials for arbitrary G/H symmetric spaces. Developed as the computational backbone of the Metric Bundle Programme.

## Install

```bash
cd omni_toolkit
pip install -e .
```

## Quick start

```python
import numpy as np
from omni_toolkit.core import SymmetricSpace, RicciTensor, EigenDecomposition

# GL+(4)/SO(3,1) — the Lorentzian metric bundle fibre
eta = np.diag([-1.0, 1.0, 1.0, 1.0])
space = SymmetricSpace(eta, lam=0.5)

# DeWitt metric signature
print(f"Signature: {space.dewitt.signature}")  # (6, 4)

# Ricci tensor
ric = RicciTensor(space)
print(f"Scalar curvature: {ric.scalar_curvature}")  # -30.0

# V+/V- eigendecomposition (gauge vs Higgs)
eigen = EigenDecomposition(space)
print(f"V+ dim: {eigen.v_plus_dim}, V- dim: {eigen.v_minus_dim}")  # 6, 4

# Any background works — try Euclidean 3D (elasticity)
eta3 = np.diag([1.0, 1.0, 1.0])
space3 = SymmetricSpace(eta3, lam=0.5)
print(f"GL+(3)/SO(3) signature: {space3.dewitt.signature}")  # (6, 0)
```

## Modules

| Module | Contents |
|--------|----------|
| `core.lie_algebra` | `LieAlgebra` — bracket, Killing form, adjoint, Casimir, structure constants |
| `core.symmetric_space` | `SymmetricSpace`, `DeWittMetric` — tangent space basis, metric, eigendecomposition |
| `core.curvature` | `RicciTensor` — Killing form + double commutator methods, V+/V- blocks |
| `core.representations` | `EigenDecomposition` — stabilizer, maximal compact subgroup, Dynkin indices |
| `dynamics.rg_running` | `RGRunner`, `BetaSystem` — RK4 integration, 1-loop analytic, two-scale solver |
| `dynamics.effective_potential` | `ColemanWeinberg`, `Particle` — V_CW, B coefficient, instanton scale |
| `topology.complex_structures` | `QuaternionicStructure` — complex structures on R^{4+2}, algebra verification |
| `topology.index_theorem` | `GenerationCounter` — N_G = 3, Cabibbo epsilon |
| `applications.pati_salam` | `PatiSalam` — complete GL+(4)/SO(3,1) → Pati-Salam instantiation |

## API reference

### `SymmetricSpace(background, lam=0.5)`
Constructs GL+(d)/H for a d×d background metric. The `lam` parameter is the DeWitt parameter (λ = 1/2 is the DeWitt value).

### `RicciTensor(space)`
Computes Ricci tensor via two independent methods (Killing form and double commutator). Properties: `ric_matrix`, `scalar_curvature`, `v_plus_eigenvalues`, `v_minus_eigenvalues`.

### `EigenDecomposition(space)`
Splits the tangent space into V+ (gauge/traceless) and V- (Higgs/trace) sectors. Identifies stabilizer subalgebra and maximal compact subgroup.

### `RGRunner(beta_system, method='rk4')`
Integrates coupled beta functions. `BetaSystem` defines 1-loop coefficients. `compute_lr_betas()` returns left-right symmetric Pati-Salam betas.

### `ColemanWeinberg(particles, mu)`
Computes 1-loop effective potential from a list of `Particle(mass_sq_func, dof, sign)`. Finds radiative minimum and instanton scale.

## Citation

If you use this toolkit, please cite:

```bibtex
@misc{austermann2026metric,
  author = {Austermann, Sloan},
  title = {The Metric Bundle Programme},
  year = {2026},
  doi = {10.5281/zenodo.18860687},
}
```

## License

MIT
