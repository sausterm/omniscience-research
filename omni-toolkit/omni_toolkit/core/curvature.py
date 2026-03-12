"""
Ricci tensor and sectional curvature for symmetric spaces.

Two independent methods:
  Method 1 (Killing form): Ric(X,Y) = -(1/2) B(X,Y) for symmetric spaces of non-compact type.
  Method 2 (double commutator): Ric_{ij} = G^{kl} R_{kijl} with R from [[e_k,e_i],e_j].

Both are provided as cross-checks.
"""

import numpy as np
from .symmetric_space import SymmetricSpace
from .lie_algebra import LieAlgebra


class RicciTensor:
    """Compute and analyze the Ricci tensor on a symmetric space.

    Parameters
    ----------
    space : SymmetricSpace
        The symmetric space G/H.
    """

    def __init__(self, space: SymmetricSpace):
        self.space = space
        self._compute_killing()
        self._compute_double_commutator()
        self._decompose_blocks()

    def _compute_killing(self):
        """Ricci via Killing form: Ric = -(1/2) B restricted to p."""
        n = self.space.d
        basis = self.space.basis
        dim = self.space.dim_fibre
        B = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                B[i, j] = (2 * n * np.trace(basis[i] @ basis[j])
                           - 2 * np.trace(basis[i]) * np.trace(basis[j]))
        self.killing_form = B
        self.ric_killing = -0.5 * B

    def _compute_double_commutator(self):
        """Ricci via double commutator: R_{kijl} = -G([[e_k,e_i],e_j], e_l)."""
        dim = self.space.dim_fibre
        basis = self.space.basis
        G_inv = self.space.metric_inverse
        dw = self.space.dewitt

        Ric = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                val = 0.0
                for k in range(dim):
                    for l in range(dim):
                        comm_ki = LieAlgebra.bracket(basis[k], basis[i])
                        double_comm = LieAlgebra.bracket(comm_ki, basis[j])
                        R_kijl = -dw.inner_product_fast(double_comm, basis[l])
                        val += G_inv[k, l] * R_kijl
                Ric[i, j] = val
        self.ric_double_comm = Ric

    def _decompose_blocks(self):
        """Decompose Ric in the V+/V- eigenbasis using subspace projections."""
        V_plus = self.space.V_plus_vecs   # dim_fibre x n_plus
        V_minus = self.space.V_minus_vecs  # dim_fibre x n_minus
        Ric = self.ric_killing

        self.ric_pp = V_plus.T @ Ric @ V_plus
        self.ric_mm = V_minus.T @ Ric @ V_minus
        self.ric_mp = V_minus.T @ Ric @ V_plus

    @property
    def ric(self) -> np.ndarray:
        """The Ricci tensor (Killing form method, exact for symmetric spaces)."""
        return self.ric_killing

    @property
    def scalar_curvature(self) -> float:
        """Scalar curvature R = Tr(G^{-1} Ric)."""
        return np.trace(self.space.metric_inverse @ self.ric_killing)

    @property
    def methods_agree(self) -> bool:
        """Check if Killing form and double commutator methods agree."""
        return np.max(np.abs(self.ric_killing - self.ric_double_comm)) < 1e-6

    def ric_over_g_ratios(self) -> dict:
        """Compute Ric/G ratios on V+ and V- subspaces.

        Returns dict with 'V_plus_ratios', 'V_minus_ratios', 'is_einstein'.
        """
        eigs_pp = np.linalg.eigvalsh(self.ric_pp)
        eigs_mm = np.linalg.eigvalsh(self.ric_mm)

        pos_evals = self.space.eigenvalues[self.space.pos_idx]
        neg_evals = self.space.eigenvalues[self.space.neg_idx]

        ratios_pp = eigs_pp / pos_evals if len(pos_evals) > 0 else np.array([])
        ratios_mm = eigs_mm / neg_evals if len(neg_evals) > 0 else np.array([])

        mean_pp = np.mean(ratios_pp) if len(ratios_pp) > 0 else 0.0
        mean_mm = np.mean(ratios_mm) if len(ratios_mm) > 0 else 0.0

        is_einstein = (len(ratios_pp) > 0 and len(ratios_mm) > 0
                       and abs(mean_pp - mean_mm) / abs(mean_pp + 1e-30) < 0.01)

        return {
            'V_plus_ratios': ratios_pp,
            'V_minus_ratios': ratios_mm,
            'V_plus_mean': mean_pp,
            'V_minus_mean': mean_mm,
            'is_einstein': is_einstein,
        }

    def mixed_norm(self) -> float:
        """Frobenius norm of the mixed block Ric(V-, V+).

        Zero at the symmetric point; nonzero indicates Yukawa-type coupling.
        """
        return np.linalg.norm(self.ric_mp)

    def sectional_curvature(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Compute sectional curvature K(X, Y) for two tangent vectors.

        Parameters
        ----------
        X, Y : ndarray
            Tangent vectors as d x d matrices.
        """
        eta = self.space.background
        dw = self.space.dewitt

        comm = LieAlgebra.bracket(X, Y)
        # Project to h (stabilizer): eta A antisymmetric
        etaM = eta @ comm
        A_part = 0.5 * (etaM - etaM.T)
        comm_h = np.linalg.solve(eta, A_part)

        double_comm = LieAlgebra.bracket(comm_h, Y)
        R_XYYX = dw.inner_product_fast(double_comm, X)

        denom = (dw.inner_product_fast(X, X) * dw.inner_product_fast(Y, Y)
                 - dw.inner_product_fast(X, Y) ** 2)
        if abs(denom) < 1e-15:
            return 0.0
        return -R_XYYX / denom

    def perturbation_analysis(self, direction_idx: int, epsilons: list = None) -> list:
        """Analyze how Ric_mixed changes under perturbation along a V+ direction.

        Parameters
        ----------
        direction_idx : int
            Index into V_plus_mats.
        epsilons : list of float
            Perturbation magnitudes.

        Returns list of dicts with 'eps', 'ric_mp_norm', 'signature'.
        """
        if epsilons is None:
            epsilons = [0.01, 0.05, 0.1, 0.2]
        results = []
        eta = self.space.background
        h_mat = self.space.V_plus_mats[direction_idx]

        for eps in epsilons:
            g_pert = eta + eps * h_mat
            try:
                G_new = self.space.compute_metric_at(g_pert)
            except np.linalg.LinAlgError:
                results.append({'eps': eps, 'ric_mp_norm': None, 'signature': None})
                continue

            eig_new, U_new = np.linalg.eigh(G_new)

            pos_new = np.where(eig_new > 1e-10)[0]
            neg_new = np.where(eig_new < -1e-10)[0]

            if len(pos_new) != self.space.n_pos or len(neg_new) != self.space.n_neg:
                results.append({'eps': eps, 'ric_mp_norm': None,
                                'signature': (len(pos_new), len(neg_new))})
                continue

            V_p = U_new[:, pos_new]
            V_m = U_new[:, neg_new]
            ric_mp_new = V_m.T @ self.ric_killing @ V_p

            results.append({
                'eps': eps,
                'ric_mp_norm': np.linalg.norm(ric_mp_new),
                'signature': (len(pos_new), len(neg_new)),
            })
        return results
