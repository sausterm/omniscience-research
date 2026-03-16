"""
Moduli spaces of complex structures and their curvature.

The key example: CP³ = SU(4)/U(3) parametrizes complex structures on V+ (R⁶).
The holomorphic sectional curvature E(J) varies by ~193% over CP³,
creating a potential that selects a preferred U(3) ⊃ SU(3) × U(1)_{B-L}.

STATUS:
  - SU(4) → SU(3) × U(1)_{B-L} from CP³ minimum: DERIVED from fibre curvature
  - Ric = 0 direction = B-L generator: DERIVED
  - CP³ modes = 3 ⊕ 3̄ (color triplets): DERIVED from ad_J eigenvalues ±2i
  - SU(2)_R breaking from CP³: OPEN (tree-level preserves L-R symmetry)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List
from scipy.optimize import minimize


@dataclass
class ModuliSpace:
    """Moduli space of complex structures on a real vector space.

    Parameters
    ----------
    dim : int
        Dimension of the real vector space (must be even).
    metric : ndarray or None
        Inner product on the vector space. Default: identity.
    riemann : ndarray or None
        Riemann tensor R_{ijkl} on the vector space. If None, computed
        from Killing form for symmetric space.
    """

    dim: int = 6
    metric: Optional[np.ndarray] = None
    riemann: Optional[np.ndarray] = None

    def __post_init__(self):
        assert self.dim % 2 == 0, "Dimension must be even for complex structures"
        if self.metric is None:
            self.metric = np.eye(self.dim)

    def standard_complex_structure(self) -> np.ndarray:
        """Standard complex structure J₀ on R^{2n}: pairs (0,1), (2,3), ..."""
        n = self.dim
        J = np.zeros((n, n))
        for k in range(n // 2):
            J[2*k, 2*k+1] = -1.0
            J[2*k+1, 2*k] = 1.0
        return J

    def random_complex_structure(self) -> np.ndarray:
        """Generate a random complex structure on R^n via SO(n) rotation.

        Returns J = O J₀ O^T for random orthogonal O.
        """
        J0 = self.standard_complex_structure()
        # Random orthogonal matrix
        A = np.random.randn(self.dim, self.dim)
        Q, _ = np.linalg.qr(A)
        if np.linalg.det(Q) < 0:
            Q[:, 0] *= -1
        return Q @ J0 @ Q.T

    def holomorphic_sectional_curvature(self, J: np.ndarray,
                                         R: np.ndarray = None) -> float:
        """Compute E(J) = holomorphic sectional curvature for complex structure J.

        E(J) = Σ_{a,b} R_{a Ja b Jb} where sum is over an orthonormal basis.

        Parameters
        ----------
        J : ndarray
            Complex structure (n×n, J² = -I).
        R : ndarray or None
            Riemann tensor R_{ijkl}. If None, uses self.riemann.
        """
        if R is None:
            R = self.riemann
        if R is None:
            raise ValueError("Riemann tensor required for E(J)")

        n = self.dim
        E = 0.0
        for a in range(n):
            for b in range(n):
                Ja = J[a, :]
                Jb = J[b, :]
                ea = np.zeros(n)
                ea[a] = 1.0
                eb = np.zeros(n)
                eb[b] = 1.0
                E += self._R_contract(R, ea, Ja, eb, Jb)
        return E

    def _R_contract(self, R: np.ndarray, u: np.ndarray, v: np.ndarray,
                     w: np.ndarray, x: np.ndarray) -> float:
        """Contract R_{ijkl} with four vectors."""
        return np.einsum('ijkl,i,j,k,l', R, u, v, w, x)

    def build_riemann_killing(self, basis: list, metric_matrix: np.ndarray) -> np.ndarray:
        """Build Riemann tensor from Killing form for symmetric space.

        R_{kijl} = -G([[e_k, e_i], e_j], e_l) for basis elements e_i.

        Parameters
        ----------
        basis : list of ndarray
            Basis matrices for the tangent space.
        metric_matrix : ndarray
            DeWitt metric matrix G_{ij}.
        """
        n = len(basis)
        R = np.zeros((n, n, n, n))
        for k in range(n):
            for i in range(n):
                comm = basis[k] @ basis[i] - basis[i] @ basis[k]
                for j in range(n):
                    double_comm = comm @ basis[j] - basis[j] @ comm
                    for l in range(n):
                        # Project double_comm onto basis[l] using metric
                        R[k, i, j, l] = -np.sum(
                            metric_matrix[m, l] *
                            np.trace(double_comm.T @ basis[m])
                            for m in range(n)
                        )
        return R

    def ricci_eigenvalues_on_subspace(self, subspace_vecs: np.ndarray,
                                       ric_matrix: np.ndarray) -> np.ndarray:
        """Project Ricci tensor to subspace and find eigenvalues.

        Parameters
        ----------
        subspace_vecs : ndarray
            Matrix whose columns span the subspace.
        ric_matrix : ndarray
            Full Ricci tensor.
        """
        R_sub = subspace_vecs.T @ ric_matrix @ subspace_vecs
        return np.linalg.eigvalsh(R_sub)

    def optimize_E(self, R: np.ndarray, n_starts: int = 20) -> dict:
        """Find minimum and maximum of E(J) over the space of complex structures.

        Uses multi-start optimization over SO(n) parametrization.

        Parameters
        ----------
        R : ndarray
            Riemann tensor.
        n_starts : int
            Number of random restarts.

        Returns dict with E_min, E_max, J_min, J_max, anisotropy.
        """
        J0 = self.standard_complex_structure()
        n = self.dim

        def E_from_params(params, sign=1.0):
            """Parametrize J = O J₀ O^T via exponential map."""
            # params → skew-symmetric matrix → O = exp(A)
            A = np.zeros((n, n))
            k = 0
            for i in range(n):
                for j in range(i+1, n):
                    A[i, j] = params[k]
                    A[j, i] = -params[k]
                    k += 1
            O = self._matrix_exp_skew(A)
            J = O @ J0 @ O.T
            return sign * self.holomorphic_sectional_curvature(J, R)

        n_params = n * (n - 1) // 2

        best_min = float('inf')
        best_max = float('-inf')
        J_min = J0.copy()
        J_max = J0.copy()

        for _ in range(n_starts):
            p0 = np.random.randn(n_params) * 0.5
            # Minimize E
            res = minimize(lambda p: E_from_params(p, +1.0), p0,
                           method='Powell', options={'maxiter': 500})
            if res.fun < best_min:
                best_min = res.fun
                J_min = self._params_to_J(res.x, J0)

            # Maximize E
            res = minimize(lambda p: E_from_params(p, -1.0), p0,
                           method='Powell', options={'maxiter': 500})
            if -res.fun > best_max:
                best_max = -res.fun
                J_max = self._params_to_J(res.x, J0)

        anisotropy = (best_max - best_min) / abs(best_min) * 100 if abs(best_min) > 1e-15 else float('inf')

        return {
            'E_min': best_min,
            'E_max': best_max,
            'J_min': J_min,
            'J_max': J_max,
            'anisotropy_pct': anisotropy,
        }

    def _params_to_J(self, params: np.ndarray, J0: np.ndarray) -> np.ndarray:
        """Convert parameter vector to complex structure."""
        n = J0.shape[0]
        A = np.zeros((n, n))
        k = 0
        for i in range(n):
            for j in range(i+1, n):
                A[i, j] = params[k]
                A[j, i] = -params[k]
                k += 1
        O = self._matrix_exp_skew(A)
        return O @ J0 @ O.T

    @staticmethod
    def _matrix_exp_skew(A: np.ndarray) -> np.ndarray:
        """Matrix exponential of skew-symmetric matrix (gives SO(n))."""
        eigenvalues, U = np.linalg.eigh(1j * A)
        return np.real(U @ np.diag(np.exp(-1j * eigenvalues)) @ U.conj().T)

    def ad_J_eigenvalues(self, J: np.ndarray) -> np.ndarray:
        """Eigenvalues of ad_J acting on so(n).

        For CP³ modes: eigenvalues ±2i confirm 3 ⊕ 3̄ decomposition.
        """
        n = J.shape[0]
        # Build so(n) basis
        so_basis = []
        for i in range(n):
            for j in range(i+1, n):
                E = np.zeros((n, n))
                E[i, j] = 1.0
                E[j, i] = -1.0
                so_basis.append(E)

        dim_so = len(so_basis)
        ad_J = np.zeros((dim_so, dim_so))
        for a in range(dim_so):
            comm = J @ so_basis[a] - so_basis[a] @ J
            for b in range(dim_so):
                ad_J[a, b] = np.trace(comm.T @ so_basis[b]) / 2.0

        return np.linalg.eigvals(ad_J)
