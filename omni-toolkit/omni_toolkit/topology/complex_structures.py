"""
Complex and quaternionic structures on vector spaces.

Given a vector space R^{2n} (or R^{4n}), constructs complex structures J
satisfying J^2 = -1, and quaternionic triples (I, J, K) satisfying IJ = K.
Analyzes stabilizer groups U(n) and their intersections.
"""

import numpy as np
from typing import Tuple


class QuaternionicStructure:
    """Quaternionic structure on R^{4+2} = R^4 ⊕ R^2 (or general R^{2n}).

    Constructs three complex structures I, J, K satisfying the quaternion
    algebra, computes their stabilizer groups U(n), and analyzes overlaps.

    Parameters
    ----------
    dim : int
        Dimension of the vector space (must be even).
    quaternionic_dim : int
        Dimension of the quaternionic part (must be divisible by 4).
        The remaining dim - quaternionic_dim dimensions get a standard
        complex structure.
    """

    def __init__(self, dim: int = 6, quaternionic_dim: int = 4):
        self.dim = dim
        self.q_dim = quaternionic_dim
        self.c_dim = dim - quaternionic_dim
        assert dim % 2 == 0, "dim must be even for complex structures"
        assert quaternionic_dim % 4 == 0, "quaternionic_dim must be divisible by 4"

        self._build_structures()

    def _build_structures(self):
        """Build the three complex structures I, J, K."""
        d = self.q_dim
        # Quaternionic structure on R^d: standard i, j, k matrices
        # For R^4: the three complex structures
        I_q = np.zeros((d, d))
        J_q = np.zeros((d, d))
        K_q = np.zeros((d, d))

        # Build in 4x4 blocks
        for block in range(d // 4):
            s = 4 * block
            I_q[s:s+4, s:s+4] = np.array([
                [0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]])
            J_q[s:s+4, s:s+4] = np.array([
                [0, 0, -1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, -1, 0, 0]])
            K_q[s:s+4, s:s+4] = np.array([
                [0, 0, 0, -1], [0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0]])

        # Standard complex structure on the remaining dimensions
        c = self.c_dim
        I_c = np.zeros((c, c))
        for block in range(c // 2):
            s = 2 * block
            I_c[s:s+2, s:s+2] = np.array([[0, -1], [1, 0]])

        # Block diagonal
        n = self.dim
        def block_diag(A, B):
            M = np.zeros((n, n))
            M[:A.shape[0], :A.shape[1]] = A
            M[A.shape[0]:, A.shape[1]:] = B
            return M

        self.J_I = block_diag(I_q, I_c)
        self.J_J = block_diag(J_q, I_c)
        self.J_K = block_diag(K_q, I_c)

    def verify_algebra(self) -> dict:
        """Verify the quaternion algebra relations."""
        n = self.dim
        eye = np.eye(n)
        return {
            'I_sq_minus_1': np.allclose(self.J_I @ self.J_I, -eye),
            'J_sq_minus_1': np.allclose(self.J_J @ self.J_J, -eye),
            'K_sq_minus_1': np.allclose(self.J_K @ self.J_K, -eye),
            'IJ_eq_K': np.allclose(self.J_I @ self.J_J, self.J_K),
            'JK_eq_I': np.allclose(self.J_J @ self.J_K, self.J_I),
            'KI_eq_J': np.allclose(self.J_K @ self.J_I, self.J_J),
        }

    def stabilizer_dimension(self, J: np.ndarray) -> int:
        """Compute dim(U(n)) = dim({g in SO(2n) : gJ = Jg}).

        This is the number of independent antisymmetric matrices commuting with J.
        """
        n = self.dim
        # A in so(n) means A^T = -A
        # A commutes with J: AJ = JA
        # Count solutions by solving: A J - J A = 0 with A + A^T = 0
        constraints = []
        # A has n(n-1)/2 independent components
        idx_map = {}
        k = 0
        for i in range(n):
            for j in range(i + 1, n):
                idx_map[(i, j)] = k
                k += 1
        n_vars = k

        # Build constraint matrix for [A, J] = 0
        rows = []
        for i in range(n):
            for j in range(n):
                row = np.zeros(n_vars)
                for l in range(n):
                    # (AJ)_{ij} = sum_l A_{il} J_{lj}
                    if l < i:
                        row[idx_map[(l, i)]] -= J[l, j]
                    elif l > i:
                        row[idx_map[(i, l)]] += J[l, j]
                    # -(JA)_{ij} = -sum_l J_{il} A_{lj}
                    if l < j:
                        row[idx_map[(l, j)]] -= J[i, l]
                    elif l > j:
                        row[idx_map[(j, l)]] += J[i, l]
                rows.append(row)
        C = np.array(rows)
        rank = np.linalg.matrix_rank(C, tol=1e-10)
        return n_vars - rank

    def analyze(self) -> dict:
        """Full analysis of the quaternionic structure."""
        dim_stab_I = self.stabilizer_dimension(self.J_I)
        dim_stab_J = self.stabilizer_dimension(self.J_J)
        dim_stab_K = self.stabilizer_dimension(self.J_K)

        alg = self.verify_algebra()
        all_ok = all(alg.values())

        return {
            'dim': self.dim,
            'quaternionic_dim': self.q_dim,
            'complex_dim': self.c_dim,
            'algebra_verified': all_ok,
            'stabilizer_dims': {
                'U_I': dim_stab_I,
                'U_J': dim_stab_J,
                'U_K': dim_stab_K,
            },
            'n_complex_structures': 3,
            'dim_imaginary_quaternions': 3,
        }
