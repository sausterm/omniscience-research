"""
Symmetric spaces G/H and the DeWitt supermetric.

Provides the core abstraction: a symmetric space defined by a background metric
(any signature), with automatic construction of the tangent space basis,
the DeWitt metric, and eigendecomposition into positive/negative norm subspaces.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class DeWittMetric:
    """The DeWitt supermetric on symmetric 2-tensors S^2(R^d).

    G(h,k) = g^{mu rho} g^{nu sigma} h_{mu nu} k_{rho sigma}
             - lambda * (g^{mu nu} h_{mu nu})(g^{rho sigma} k_{rho sigma})

    Parameters
    ----------
    background : ndarray
        The background metric g_{mu nu}, shape (d, d). Any signature.
    lam : float
        The trace coupling parameter. DeWitt canonical value is 1/2.
    """

    background: np.ndarray
    lam: float = 0.5

    def __post_init__(self):
        self.background = np.asarray(self.background, dtype=float)
        self.d = self.background.shape[0]
        self.g_inv = np.linalg.inv(self.background)

    def inner_product(self, h: np.ndarray, k: np.ndarray) -> float:
        """Compute G(h, k) for two symmetric 2-tensors."""
        d = self.d
        g_inv = self.g_inv
        term1 = 0.0
        for mu in range(d):
            for nu in range(d):
                for rho in range(d):
                    for sig in range(d):
                        term1 += g_inv[mu, rho] * g_inv[nu, sig] * h[mu, nu] * k[rho, sig]
        trh = np.einsum('ij,ij', g_inv, h)
        trk = np.einsum('ij,ij', g_inv, k)
        return term1 - self.lam * trh * trk

    def inner_product_fast(self, h: np.ndarray, k: np.ndarray) -> float:
        """Vectorized computation of G(h, k)."""
        g_inv = self.g_inv
        term1 = np.einsum('mr,ns,mn,rs', g_inv, g_inv, h, k)
        trh = np.einsum('ij,ij', g_inv, h)
        trk = np.einsum('ij,ij', g_inv, k)
        return term1 - self.lam * trh * trk


class SymmetricSpace:
    """A symmetric space G/H defined by a background metric.

    Constructs the tangent space p (eta-symmetric matrices for Lorentzian,
    or standard symmetric matrices for Euclidean), the DeWitt metric on p,
    and decomposes into positive/negative eigenspaces V+/V-.

    Parameters
    ----------
    background : ndarray
        Background metric eta_{mu nu}. Signature determines G/H:
        - diag(-1,1,...,1): GL+(d)/SO(d-1,1) (Lorentzian)
        - diag(1,1,...,1):  GL+(d)/SO(d) (Euclidean)
        - arbitrary diagonal with ±1 entries for general signature.
    lam : float
        DeWitt trace coupling (default 1/2).
    """

    def __init__(self, background: np.ndarray, lam: float = 0.5):
        self.background = np.asarray(background, dtype=float)
        self.d = self.background.shape[0]
        self.dim_fibre = self.d * (self.d + 1) // 2
        self.dewitt = DeWittMetric(self.background, lam)

        self._build_basis()
        self._build_metric_matrix()
        self._eigendecompose()

    def _build_basis(self):
        """Build eta-symmetric basis for the tangent space p.

        For background eta, the tangent space consists of matrices S
        such that eta S is symmetric: eta S = (eta S)^T.
        """
        d = self.d
        eta = self.background
        basis = []
        labels = []
        for i in range(d):
            for j in range(i, d):
                mat = np.zeros((d, d))
                if i == j:
                    mat[i, i] = 1.0
                else:
                    if eta[i, i] * eta[j, j] > 0:
                        # Same signature: symmetric off-diagonal
                        mat[i, j] = 1.0 / np.sqrt(2)
                        mat[j, i] = 1.0 / np.sqrt(2)
                    else:
                        # Opposite signature: antisymmetric off-diagonal
                        mat[i, j] = 1.0 / np.sqrt(2)
                        mat[j, i] = -1.0 / np.sqrt(2)
                    # Verify eta-symmetry and correct if needed
                    lhs = eta @ mat
                    if np.max(np.abs(lhs - lhs.T)) > 1e-10:
                        mat[j, i] = -mat[j, i]
                basis.append(mat)
                labels.append(f"({i},{j})")
        self.basis = basis
        self.labels = labels

    def _build_metric_matrix(self):
        """Build the dim_fibre x dim_fibre DeWitt metric matrix."""
        n = self.dim_fibre
        G = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                G[i, j] = self.dewitt.inner_product_fast(self.basis[i], self.basis[j])
        self.metric_matrix = G
        # Use pseudoinverse when metric is singular (e.g. d=2 at lambda=1/2
        # where the conformal mode is null)
        if abs(np.linalg.det(G)) < 1e-10:
            self.metric_inverse = np.linalg.pinv(G)
            self.metric_singular = True
        else:
            self.metric_inverse = np.linalg.inv(G)
            self.metric_singular = False

    def _eigendecompose(self):
        """Eigendecompose the metric into V+ and V- subspaces."""
        eigenvalues, eigenvectors = np.linalg.eigh(self.metric_matrix)
        self.eigenvalues = eigenvalues
        self.eigenvectors = eigenvectors  # columns are eigenvectors

        self.pos_idx = np.where(eigenvalues > 1e-10)[0]
        self.neg_idx = np.where(eigenvalues < -1e-10)[0]
        self.zero_idx = np.where(np.abs(eigenvalues) <= 1e-10)[0]

        self.n_pos = len(self.pos_idx)
        self.n_neg = len(self.neg_idx)
        self.signature = (self.n_pos, self.n_neg)

        # V+ and V- coefficient vectors (columns of eigenvectors)
        self.V_plus_vecs = eigenvectors[:, self.pos_idx]
        self.V_minus_vecs = eigenvectors[:, self.neg_idx]

        # V+ and V- as matrices in the original d x d space
        self.V_plus_mats = [self._vec_to_mat(self.V_plus_vecs[:, i])
                            for i in range(self.n_pos)]
        self.V_minus_mats = [self._vec_to_mat(self.V_minus_vecs[:, i])
                             for i in range(self.n_neg)]

    def _vec_to_mat(self, v: np.ndarray) -> np.ndarray:
        """Convert coefficient vector to d x d matrix using the basis."""
        return sum(v[i] * self.basis[i] for i in range(self.dim_fibre))

    def mat_to_vec(self, M: np.ndarray) -> np.ndarray:
        """Project a d x d matrix onto the basis using the DeWitt metric."""
        components = np.array([self.dewitt.inner_product_fast(self.basis[i], M)
                               for i in range(self.dim_fibre)])
        return self.metric_inverse @ components

    def compute_metric_at(self, g: np.ndarray) -> np.ndarray:
        """Compute the DeWitt metric matrix at an arbitrary background g.

        This allows perturbation analysis away from the symmetric point.
        """
        dw = DeWittMetric(g, self.dewitt.lam)
        n = self.dim_fibre
        G = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                G[i, j] = dw.inner_product_fast(self.basis[i], self.basis[j])
        return G

    def classify_modes(self) -> dict:
        """Classify basis elements by their spacetime content.

        Returns dict with keys 'spatial', 'shift', 'lapse' (for Lorentzian),
        each mapping to lists of basis indices.
        """
        eta = self.background
        spatial = []
        shift = []
        lapse = []

        # Find which indices are timelike (negative diagonal)
        timelike = [i for i in range(self.d) if eta[i, i] < 0]
        spacelike = [i for i in range(self.d) if eta[i, i] > 0]

        for idx, label in enumerate(self.labels):
            i, j = int(label[1]), int(label[3])
            if i in timelike and j in timelike:
                lapse.append(idx)
            elif i in timelike or j in timelike:
                shift.append(idx)
            else:
                spatial.append(idx)

        return {'spatial': spatial, 'shift': shift, 'lapse': lapse}

    def restricted_metric(self, indices: list) -> np.ndarray:
        """Extract the metric restricted to a subset of basis elements."""
        n = len(indices)
        G = np.zeros((n, n))
        for a in range(n):
            for b in range(n):
                G[a, b] = self.metric_matrix[indices[a], indices[b]]
        return G
