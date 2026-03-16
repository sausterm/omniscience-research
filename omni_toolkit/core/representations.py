"""
Representation analysis on symmetric spaces.

Eigendecomposition of the DeWitt metric, stabilizer group construction,
and adjoint action analysis for identifying gauge group content.
"""

import numpy as np
from .symmetric_space import SymmetricSpace
from .lie_algebra import LieAlgebra


class EigenDecomposition:
    """Analyze the eigenstructure of a symmetric space metric.

    Identifies the V+/V- split, constructs the stabilizer algebra,
    and computes the adjoint action of the stabilizer on V+/V-.
    """

    def __init__(self, space: SymmetricSpace):
        self.space = space

    def build_stabilizer_basis(self) -> tuple:
        """Build the stabilizer (isotropy) algebra h = so(p, q) where
        (p, q) is the background metric signature.

        Returns (generators, labels) for h.
        """
        d = self.space.d
        eta = self.space.background
        basis = []
        labels = []
        for i in range(d):
            for j in range(i + 1, d):
                A = np.zeros((d, d))
                if eta[i, i] * eta[j, j] > 0:
                    # Rotation
                    A[i, j] = 1.0
                    A[j, i] = -1.0
                    labels.append(f"R{i}{j}")
                else:
                    # Boost
                    A[i, j] = 1.0
                    A[j, i] = 1.0
                    labels.append(f"B{max(i,j)}")

                # Verify eta-antisymmetry: eta A + (eta A)^T = 0
                etaA = eta @ A
                if np.max(np.abs(etaA + etaA.T)) > 1e-10:
                    A[j, i] = -A[j, i]

                basis.append(A)
        return basis, labels

    def adjoint_on_p(self, A: np.ndarray) -> np.ndarray:
        """Matrix of ad_A acting on the tangent space p, in the p-basis.

        Parameters
        ----------
        A : ndarray
            A stabilizer algebra element (d x d matrix).
        """
        dim = self.space.dim_fibre
        basis = self.space.basis
        dw = self.space.dewitt
        G_inv = self.space.metric_inverse

        mat = np.zeros((dim, dim))
        for j in range(dim):
            bracket = LieAlgebra.bracket(A, basis[j])
            for i in range(dim):
                mat[i, j] = dw.inner_product_fast(basis[i], bracket)
        return G_inv @ mat

    def adjoint_in_eigenbasis(self, A: np.ndarray) -> dict:
        """Compute the adjoint action of A decomposed into V+/V- blocks.

        Returns dict with 'pp', 'mm', 'mp', 'pm' blocks and their norms.
        """
        M = self.adjoint_on_p(A)
        U = self.space.eigenvectors
        M_eig = U.T @ M @ U

        pos = list(self.space.pos_idx)
        neg = list(self.space.neg_idx)

        M_pp = M_eig[np.ix_(pos, pos)]
        M_mm = M_eig[np.ix_(neg, neg)]
        M_mp = M_eig[np.ix_(neg, pos)]
        M_pm = M_eig[np.ix_(pos, neg)]

        return {
            'pp': M_pp, 'mm': M_mm, 'mp': M_mp, 'pm': M_pm,
            'norm_pp': np.linalg.norm(M_pp),
            'norm_mm': np.linalg.norm(M_mm),
            'norm_mp': np.linalg.norm(M_mp),
        }

    def maximal_compact_subgroup(self) -> dict:
        """Identify the maximal compact subgroup from the signature.

        For SO(p, q), the maximal compact subgroup is SO(p) x SO(q).
        Returns dict with 'positive_group', 'negative_group', 'description'.
        """
        p, q = self.space.signature
        # Standard isomorphisms
        descriptions = {
            (6, 4): "SO(6) x SO(4) = SU(4) x SU(2)_L x SU(2)_R [Pati-Salam]",
            (9, 1): "SO(9) x SO(1) = SO(9) [Euclidean signature]",
            (3, 3): "SO(3) x SO(3) = SU(2) x SU(2)",
            (3, 1): "SO(3) x SO(1) = SO(3)",
        }
        desc = descriptions.get((p, q), f"SO({p}) x SO({q})")
        return {
            'positive_group': f"SO({p})",
            'negative_group': f"SO({q})",
            'description': desc,
            'n_generators': p * (p - 1) // 2 + q * (q - 1) // 2,
        }

    def dynkin_indices(self) -> dict:
        """Compute Dynkin indices for gauge factor representations.

        For the fundamental of SO(p,q), the p-dim rep under SO(p) and
        the q-dim rep under SO(q).
        """
        p, q = self.space.signature
        # For SO(n), the fundamental has T(fund) = 1
        # For the decomposition of the fundamental (p+q) of SO(p,q):
        # (p+q) -> (p, 1) + (1, q) under SO(p) x SO(q)
        return {
            'T_positive': 1,  # Dynkin index of SO(p) in (p,1)
            'T_negative': 1,  # Dynkin index of SO(q) in (1,q)
            'equal': True,    # Always equal for this decomposition
        }
