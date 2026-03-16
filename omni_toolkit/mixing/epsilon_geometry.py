"""
Geometric derivation of the Cabibbo expansion parameter ε.

The key result: ε = 1/√(2·dim_fibre) where dim_fibre = d(d+1)/2.
For d=4 spacetime: ε = 1/√20 ≈ 0.2236, matching sin(θ_C) to 0.75%.

The factor of 2 has three independent interpretations:
  1. Two chiralities (L, R) of Dirac spinors
  2. Two quark sectors (up-type, down-type) in CKM
  3. Shared subspace k=0.5 from U(3) intersection structure

STATUS: ε = 1/√(2·dim_fibre) is DERIVED from geometry.
        The sector-specific powers (ε², ε^2.5, ε³) are FITTED.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


# Observed value (PDG 2024)
SIN_THETA_CABIBBO_OBS = 0.2253


@dataclass
class EpsilonGeometry:
    """Geometric expansion parameter from fibre dimension.

    Parameters
    ----------
    spacetime_dim : int
        Spacetime dimension d. Default 4.
    fibre_dim : int or None
        Override fibre dimension. If None, computed as d(d+1)/2.
    """

    spacetime_dim: int = 4
    fibre_dim: Optional[int] = None

    def __post_init__(self):
        if self.fibre_dim is None:
            d = self.spacetime_dim
            self.fibre_dim = d * (d + 1) // 2

    @property
    def epsilon(self) -> float:
        """ε = 1/√(2·dim_fibre). DERIVED from geometry."""
        return 1.0 / np.sqrt(2.0 * self.fibre_dim)

    @property
    def cabibbo_error_pct(self) -> float:
        """Percent error relative to observed sin(θ_C)."""
        return abs(self.epsilon - SIN_THETA_CABIBBO_OBS) / SIN_THETA_CABIBBO_OBS * 100

    def u3_intersection_analysis(self) -> dict:
        """Verify ε from U(3) intersection structure on V+.

        Three complex structures J₁, J₂, J₃ on R⁶ have stabilizers
        u(3)_a with dim=9. Their pairwise intersection has dim=4.
        This gives k = dim(∩)·dim_fibre / (dim(u3)·N_G²) ≈ 0.5,
        confirming ε = √(k/dim_fibre) = 1/√20.

        Returns dict with intersection dimensions and k parameter.
        """
        # Build complex structures on R^6 = R^4 ⊕ R^2
        # On R^4: quaternion left-multiplication by i, j, k
        # On R^2: standard complex structure
        J = np.zeros((3, 6, 6))

        # Standard 2D complex structure for the R^2 factor
        J2_std = np.array([[0, -1], [1, 0]], dtype=float)

        # Quaternionic triple on R^4 (left multiplication)
        # i: (q₀,q₁,q₂,q₃) → (-q₁,q₀,-q₃,q₂)
        I4 = np.array([[ 0,-1, 0, 0],
                        [ 1, 0, 0, 0],
                        [ 0, 0, 0,-1],
                        [ 0, 0, 1, 0]], dtype=float)
        # j: (q₀,q₁,q₂,q₃) → (-q₂,q₃,q₀,-q₁)
        J4 = np.array([[ 0, 0,-1, 0],
                        [ 0, 0, 0, 1],
                        [ 1, 0, 0, 0],
                        [ 0,-1, 0, 0]], dtype=float)
        # k = ij
        K4 = I4 @ J4

        # J₁ = block_diag(I₄, J₂_std)
        J[0, :4, :4] = I4
        J[0, 4:, 4:] = J2_std
        # J₂ = block_diag(J₄, J₂_std)
        J[1, :4, :4] = J4
        J[1, 4:, 4:] = J2_std
        # J₃ = block_diag(K₄, J₂_std)
        J[2, :4, :4] = K4
        J[2, 4:, 4:] = J2_std

        # Verify J_a² = -I
        for a in range(3):
            assert np.allclose(J[a] @ J[a], -np.eye(6), atol=1e-10)

        # Compute stabilizer dimensions: u(3)_a = {X ∈ so(6) : [X, J_a] = 0}
        dims = []
        stab_bases = []
        for a in range(3):
            basis = self._stabilizer_basis(J[a])
            stab_bases.append(basis)
            dims.append(len(basis))

        # Pairwise intersections
        if len(stab_bases[0]) > 0 and len(stab_bases[1]) > 0:
            dim_01 = self._intersection_dim(stab_bases[0], stab_bases[1])
        else:
            dim_01 = 0

        N_G = 3
        dim_u3 = dims[0]
        k = dim_01 * self.fibre_dim / (dim_u3 * N_G**2) if dim_u3 > 0 else 0.0
        eps_from_k = np.sqrt(k / self.fibre_dim) if k > 0 else 0.0

        return {
            'stabilizer_dims': dims,
            'intersection_dim_01': dim_01,
            'k_parameter': k,
            'epsilon_from_k': eps_from_k,
            'epsilon_formula': self.epsilon,
            'agreement_pct': abs(eps_from_k - self.epsilon) / self.epsilon * 100
                             if self.epsilon > 0 else float('inf'),
        }

    def _stabilizer_basis(self, J: np.ndarray) -> list:
        """Find basis of {X ∈ so(n) : [X, J] = 0}."""
        n = J.shape[0]
        so_basis = []
        for i in range(n):
            for j in range(i+1, n):
                E = np.zeros((n, n))
                E[i, j] = 1.0
                E[j, i] = -1.0
                so_basis.append(E)

        dim_so = len(so_basis)
        if dim_so == 0:
            return []

        # Build constraint matrix M: columns are flattened [X_i, J].
        # Constraint: Σ c_i [X_i, J] = 0, i.e., M c = 0.
        # M has shape (n², dim_so).
        M = np.zeros((n * n, dim_so))
        for i, X in enumerate(so_basis):
            comm = X @ J - J @ X
            M[:, i] = comm.ravel()

        # Null space of M gives stabilizer coefficients in R^{dim_so}
        _, s, Vh = np.linalg.svd(M, full_matrices=True)
        null_dim = np.sum(s < 1e-10)
        # Last null_dim rows of Vh span the null space of M
        null_vecs = Vh[-null_dim:] if null_dim > 0 else np.zeros((0, dim_so))

        stab_basis = []
        for v in null_vecs:
            X = sum(v[k] * so_basis[k] for k in range(dim_so))
            stab_basis.append(X)
        return stab_basis

    def _intersection_dim(self, basis1: list, basis2: list) -> int:
        """Compute dimension of intersection of two subspaces."""
        if not basis1 or not basis2:
            return 0
        n = basis1[0].shape[0]
        vecs1 = np.array([X.ravel() for X in basis1])
        vecs2 = np.array([X.ravel() for X in basis2])

        # Dim of intersection = dim(V1) + dim(V2) - dim(V1 + V2)
        combined = np.vstack([vecs1, vecs2])
        rank_combined = np.linalg.matrix_rank(combined, tol=1e-8)
        return len(basis1) + len(basis2) - rank_combined

    def epsilon_for_dim(self, d: int) -> float:
        """ε(d) = 1/√(d(d+1)) for arbitrary spacetime dimension."""
        return 1.0 / np.sqrt(d * (d + 1))

    def summary(self) -> dict:
        """Full summary of epsilon derivation."""
        return {
            'spacetime_dim': self.spacetime_dim,
            'fibre_dim': self.fibre_dim,
            'epsilon': self.epsilon,
            'sin_theta_C_obs': SIN_THETA_CABIBBO_OBS,
            'error_pct': self.cabibbo_error_pct,
            'status': 'DERIVED' if self.spacetime_dim == 4 else 'GENERALIZED',
        }
