"""
Lie Algebra Infrastructure
==========================

Provides matrix representations and Killing forms for classical Lie algebras.
Supports gl(n), sl(n), so(p,q), su(n), sp(n).

Generalized from the hardcoded gl(4)/so(3,1) computations in the TOE codebase.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class LieAlgebra:
    """A matrix Lie algebra with its structure."""

    name: str
    generators: List[np.ndarray]
    labels: List[str] = field(default_factory=list)
    _killing_matrix: Optional[np.ndarray] = field(default=None, repr=False)

    @property
    def dim(self) -> int:
        return len(self.generators)

    @property
    def matrix_size(self) -> int:
        return self.generators[0].shape[0]

    def bracket(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return X @ Y - Y @ X

    def killing_form_matrix(self) -> np.ndarray:
        """Compute the Killing form B(T_a, T_b) = Tr(ad_a ad_b)."""
        if self._killing_matrix is not None:
            return self._killing_matrix

        n = self.dim
        B = np.zeros((n, n))

        # Build adjoint representation matrices
        ad_mats = []
        for a in range(n):
            ad_a = np.zeros((n, n))
            for b in range(n):
                comm = self.bracket(self.generators[a], self.generators[b])
                # Decompose comm in generator basis
                for c in range(n):
                    # Use trace inner product to find coefficients
                    ad_a[c, b] = np.trace(
                        self.generators[c].conj().T @ comm
                    ) / np.trace(
                        self.generators[c].conj().T @ self.generators[c]
                    )
            ad_mats.append(ad_a)

        for a in range(n):
            for b in range(n):
                B[a, b] = np.trace(ad_mats[a] @ ad_mats[b])

        self._killing_matrix = B
        return B

    def killing_form(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Compute Killing form B(X, Y) using the trace formula.

        For gl(n): B(X,Y) = 2n Tr(XY) - 2 Tr(X)Tr(Y)
        For sl(n): B(X,Y) = 2n Tr(XY)
        For so(n): B(X,Y) = (n-2) Tr(XY)
        """
        n = self.matrix_size
        if self.name.startswith("gl"):
            return 2 * n * np.trace(X @ Y) - 2 * np.trace(X) * np.trace(Y)
        elif self.name.startswith("sl"):
            return 2 * n * np.trace(X @ Y)
        elif self.name.startswith("so"):
            return (n - 2) * np.trace(X @ Y)
        elif self.name.startswith("su"):
            return 2 * n * np.trace(X @ Y).real
        else:
            # Fall back to matrix computation
            B = self.killing_form_matrix()
            x_coeffs = self._decompose(X)
            y_coeffs = self._decompose(Y)
            return x_coeffs @ B @ y_coeffs

    def _decompose(self, X: np.ndarray) -> np.ndarray:
        """Decompose X into generator basis coefficients."""
        coeffs = np.zeros(self.dim)
        for i, T in enumerate(self.generators):
            norm_sq = np.trace(T.conj().T @ T).real
            if norm_sq > 1e-15:
                coeffs[i] = np.trace(T.conj().T @ X).real / norm_sq
        return coeffs

    def casimir(self, rep_matrices: List[np.ndarray]) -> np.ndarray:
        """Compute quadratic Casimir C2 = sum_a T_a^2 in a representation."""
        C = np.zeros_like(rep_matrices[0])
        for T in rep_matrices:
            C += T @ T
        return C

    def structure_constants(self) -> np.ndarray:
        """Compute structure constants f^c_{ab} from [T_a, T_b] = f^c_{ab} T_c."""
        n = self.dim
        f = np.zeros((n, n, n))
        for a in range(n):
            for b in range(n):
                comm = self.bracket(self.generators[a], self.generators[b])
                for c in range(n):
                    norm_sq = np.trace(
                        self.generators[c].conj().T @ self.generators[c]
                    ).real
                    if norm_sq > 1e-15:
                        f[c, a, b] = np.trace(
                            self.generators[c].conj().T @ comm
                        ).real / norm_sq
        return f

    def subalgebra(self, indices: List[int], name: str = "") -> 'LieAlgebra':
        """Extract a subalgebra from specified generator indices."""
        gens = [self.generators[i] for i in indices]
        labs = [self.labels[i] for i in indices] if self.labels else []
        return LieAlgebra(name=name or f"sub({self.name})", generators=gens, labels=labs)


def gl(n: int) -> LieAlgebra:
    """Construct gl(n,R) — all n×n real matrices."""
    generators = []
    labels = []
    for i in range(n):
        for j in range(n):
            E = np.zeros((n, n))
            E[i, j] = 1.0
            generators.append(E)
            labels.append(f"E_{i}{j}")
    return LieAlgebra(name=f"gl({n})", generators=generators, labels=labels)


def sl(n: int) -> LieAlgebra:
    """Construct sl(n,R) — traceless n×n real matrices."""
    generators = []
    labels = []

    # Off-diagonal
    for i in range(n):
        for j in range(n):
            if i != j:
                E = np.zeros((n, n))
                E[i, j] = 1.0
                generators.append(E)
                labels.append(f"E_{i}{j}")

    # Diagonal traceless: H_k = E_{kk} - E_{k+1,k+1}
    for k in range(n - 1):
        H = np.zeros((n, n))
        H[k, k] = 1.0
        H[k + 1, k + 1] = -1.0
        generators.append(H)
        labels.append(f"H_{k}")

    return LieAlgebra(name=f"sl({n})", generators=generators, labels=labels)


def so(p: int, q: int = 0) -> LieAlgebra:
    """Construct so(p,q) — matrices preserving metric diag(+1,...,+1,-1,...,-1).

    so(p,q) = {A : eta A + (eta A)^T = 0} where eta = diag(1^p, -1^q).
    """
    n = p + q
    # Physics convention: negative (timelike) directions first
    eta = np.diag([-1.0] * q + [1.0] * p)

    generators = []
    labels = []

    for i in range(n):
        for j in range(i + 1, n):
            A = np.zeros((n, n))
            if eta[i, i] * eta[j, j] > 0:
                # Both same sign: standard rotation
                A[i, j] = 1.0
                A[j, i] = -1.0
            else:
                # Mixed sign: boost
                A[i, j] = 1.0
                A[j, i] = 1.0

            # Verify: eta A should be antisymmetric
            etaA = eta @ A
            if not np.allclose(etaA + etaA.T, 0, atol=1e-10):
                raise ValueError(f"Generator ({i},{j}) not in so({p},{q})")

            generators.append(A)
            if i < p and j >= p:
                labels.append(f"B_{i}{j}")
            else:
                labels.append(f"R_{i}{j}")

    return LieAlgebra(name=f"so({p},{q})" if q > 0 else f"so({p})", generators=generators, labels=labels)


def su(n: int) -> LieAlgebra:
    """Construct su(n) — traceless anti-Hermitian n×n matrices (times i for Hermitian generators)."""
    generators = []
    labels = []

    # Off-diagonal: (E_{ij} - E_{ji}) / sqrt(2) and i(E_{ij} + E_{ji}) / sqrt(2)
    for i in range(n):
        for j in range(i + 1, n):
            # Real part
            T = np.zeros((n, n), dtype=complex)
            T[i, j] = 1.0 / np.sqrt(2)
            T[j, i] = 1.0 / np.sqrt(2)
            generators.append(T)
            labels.append(f"T^R_{i}{j}")

            # Imaginary part
            T = np.zeros((n, n), dtype=complex)
            T[i, j] = -1j / np.sqrt(2)
            T[j, i] = 1j / np.sqrt(2)
            generators.append(T)
            labels.append(f"T^I_{i}{j}")

    # Diagonal traceless (generalized Gell-Mann)
    for k in range(1, n):
        T = np.zeros((n, n), dtype=complex)
        for i in range(k):
            T[i, i] = 1.0
        T[k, k] = -k
        T /= np.sqrt(k * (k + 1) / 2)
        generators.append(T)
        labels.append(f"H_{k}")

    return LieAlgebra(name=f"su({n})", generators=generators, labels=labels)


def sp(n: int) -> LieAlgebra:
    """Construct sp(n) — compact symplectic algebra.

    sp(n) ≅ su(2) for n=1. Generators are 2n×2n matrices.
    """
    if n == 1:
        # sp(1) ≅ su(2)
        sigma_1 = np.array([[0, 1], [1, 0]], dtype=complex) / 2
        sigma_2 = np.array([[0, -1j], [1j, 0]], dtype=complex) / 2
        sigma_3 = np.array([[1, 0], [0, -1]], dtype=complex) / 2
        return LieAlgebra(
            name="sp(1)",
            generators=[sigma_1, sigma_2, sigma_3],
            labels=["J_I", "J_J", "J_K"]
        )

    # General sp(n): 2n×2n matrices A satisfying A^T J + J A = 0
    # where J = [[0, I_n], [-I_n, 0]]
    dim_2n = 2 * n
    J = np.zeros((dim_2n, dim_2n))
    J[:n, n:] = np.eye(n)
    J[n:, :n] = -np.eye(n)

    generators = []
    labels = []

    # Symmetric off-diagonal blocks
    for i in range(n):
        for j in range(i, n):
            # Upper-right symmetric block
            A = np.zeros((dim_2n, dim_2n))
            A[i, n + j] = 1.0
            A[j, n + i] = 1.0
            A[n + j, i] = -1.0
            A[n + i, j] = -1.0
            if np.max(np.abs(A)) > 1e-10:
                generators.append(A / np.sqrt(np.trace(A.T @ A)))
                labels.append(f"S+_{i}{j}")

            # Lower-left symmetric block
            A = np.zeros((dim_2n, dim_2n))
            A[n + i, j] = 1.0
            A[n + j, i] = 1.0
            A[j, n + i] = -1.0
            A[i, n + j] = -1.0
            if np.max(np.abs(A)) > 1e-10 and i != j:
                generators.append(A / np.sqrt(np.trace(A.T @ A)))
                labels.append(f"S-_{i}{j}")

    # Diagonal block (u(n) part)
    for i in range(n):
        for j in range(i + 1, n):
            A = np.zeros((dim_2n, dim_2n))
            A[i, j] = 1.0
            A[j, i] = -1.0
            A[n + i, n + j] = 1.0
            A[n + j, n + i] = -1.0
            generators.append(A / np.sqrt(np.trace(A.T @ A)))
            labels.append(f"U_{i}{j}")

    for k in range(n):
        A = np.zeros((dim_2n, dim_2n))
        A[k, n + k] = 1.0
        A[n + k, k] = -1.0
        generators.append(A / np.sqrt(np.trace(A.T @ A)))
        labels.append(f"D_{k}")

    return LieAlgebra(name=f"sp({n})", generators=generators, labels=labels)


def self_dual_decomposition(n: int = 4) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Decompose so(4) = su(2)_L + su(2)_R via self-dual/anti-self-dual split.

    Returns (su2_L_generators, su2_R_generators).
    """
    if n != 4:
        raise ValueError("Self-dual decomposition only defined for so(4)")

    def make_2form(i, j):
        A = np.zeros((4, 4))
        A[i, j] = 1.0
        A[j, i] = -1.0
        return A

    e01, e02, e03 = make_2form(0, 1), make_2form(0, 2), make_2form(0, 3)
    e12, e13, e23 = make_2form(1, 2), make_2form(1, 3), make_2form(2, 3)

    # Self-dual (SU(2)_L)
    L1 = (e01 + e23) / 2
    L2 = (e02 - e13) / 2
    L3 = (e03 + e12) / 2

    # Anti-self-dual (SU(2)_R)
    R1 = (e01 - e23) / 2
    R2 = (e02 + e13) / 2
    R3 = (e03 - e12) / 2

    return [L1, L2, L3], [R1, R2, R3]
