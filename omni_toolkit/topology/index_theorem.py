"""
Index theorem computations for generation counting.

The number of fermion generations N_G is determined by the quaternionic
structure of the fibre: N_G = dim(Im(H)) = dim(Adjoint of Sp(1)) = 3.

This module provides the representation-theoretic computation and
numerical verification.
"""

import numpy as np
from scipy import integrate


class GenerationCounter:
    """Count fermion generations from the fibre's quaternionic structure.

    The argument:
      1. R^d has quaternionic structure for d divisible by 4.
      2. Sp(1) ~ SU(2) acts on Im(H) via the adjoint representation.
      3. dim(Adjoint of Sp(1)) = dim(Im(H)) = 3.
      4. Fermion generations transform in the adjoint of Sp(1).
      5. Therefore N_G = 3.

    Parameters
    ----------
    spacetime_dim : int
        Spacetime dimension d. The fibre is Sym^2(R^d).
    """

    def __init__(self, spacetime_dim: int = 4):
        self.d = spacetime_dim
        self.fibre_dim = spacetime_dim * (spacetime_dim + 1) // 2

    @property
    def has_quaternionic_structure(self) -> bool:
        """Check if R^d admits quaternionic structure (d divisible by 4)."""
        return self.d % 4 == 0

    @property
    def n_generations(self) -> int:
        """Number of fermion generations from quaternionic structure.

        N_G = dim(Im(H)) = 3 for any d divisible by 4.
        """
        if not self.has_quaternionic_structure:
            return 0  # No quaternionic structure
        return 3  # dim(Im(H)) = 3 always

    @property
    def sp1_adjoint_dimension(self) -> int:
        """dim(Adjoint of Sp(1)) = dim(su(2)) = 3."""
        return 3

    def verify_su2_algebra(self) -> dict:
        """Verify dim(su(2)) = 3 via Pauli matrices."""
        sigma_1 = np.array([[0, 1], [1, 0]], dtype=complex)
        sigma_2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sigma_3 = np.array([[1, 0], [0, -1]], dtype=complex)

        T = [sigma_1 / (2j), sigma_2 / (2j), sigma_3 / (2j)]
        comm_12 = T[0] @ T[1] - T[1] @ T[0]
        comm_ok = np.allclose(comm_12, T[2])

        return {
            'dim_su2': len(T),
            'commutation_ok': comm_ok,
        }

    def index_integral(self, n_points: int = 1000) -> float:
        """Numerical verification of the index via SU(2) character integration.

        int_0^{2pi} chi_adj(theta) d(theta) / (2 pi) should be 1.
        """
        thetas = np.linspace(0, 2 * np.pi, n_points)
        chi_adj = 1 + 2 * np.cos(thetas)
        result = integrate.trapezoid(chi_adj, thetas) / (2 * np.pi)
        return result

    def cabibbo_epsilon(self) -> float:
        """The Cabibbo mixing parameter epsilon = 1 / sqrt(2 * dim(F)).

        This is geometric, not a free parameter.
        """
        return 1.0 / np.sqrt(2 * self.fibre_dim)

    def summary(self) -> dict:
        """Full summary of the generation counting."""
        eps = self.cabibbo_epsilon()
        cabibbo_obs = 0.2253
        return {
            'd': self.d,
            'fibre_dim': self.fibre_dim,
            'has_quaternionic': self.has_quaternionic_structure,
            'N_G': self.n_generations,
            'sp1_adjoint_dim': self.sp1_adjoint_dimension,
            'epsilon': eps,
            'sin_theta_C_obs': cabibbo_obs,
            'epsilon_error_pct': abs(eps - cabibbo_obs) / cabibbo_obs * 100,
        }
