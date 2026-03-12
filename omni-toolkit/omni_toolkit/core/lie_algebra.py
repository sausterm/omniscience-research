"""
Lie algebra computations for matrix Lie algebras.

Provides Killing form, structure constants, adjoint action, and Casimir operators
for any matrix Lie algebra specified by a set of generator matrices.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LieAlgebra:
    """A matrix Lie algebra specified by generator matrices.

    Parameters
    ----------
    generators : list of ndarray
        Basis matrices for the Lie algebra, each of shape (n, n).
    labels : list of str, optional
        Human-readable labels for each generator.
    """

    generators: list
    labels: list = field(default_factory=list)

    def __post_init__(self):
        self.generators = [np.asarray(g, dtype=float) for g in self.generators]
        self.dim = len(self.generators)
        self.matrix_size = self.generators[0].shape[0]
        if not self.labels:
            self.labels = [f"T_{i}" for i in range(self.dim)]

    @staticmethod
    def bracket(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Lie bracket [A, B] = AB - BA."""
        return A @ B - B @ A

    def killing_form_matrix(self, n: Optional[int] = None) -> np.ndarray:
        """Killing form B(T_i, T_j) = 2n Tr(T_i T_j) - 2 Tr(T_i) Tr(T_j).

        For gl(n, R), the Killing form is B(X, Y) = 2n Tr(XY) - 2 Tr(X)Tr(Y).

        Parameters
        ----------
        n : int, optional
            The n in the gl(n) formula. Defaults to matrix_size.
        """
        if n is None:
            n = self.matrix_size
        B = np.zeros((self.dim, self.dim))
        for i in range(self.dim):
            for j in range(self.dim):
                B[i, j] = (2 * n * np.trace(self.generators[i] @ self.generators[j])
                           - 2 * np.trace(self.generators[i]) * np.trace(self.generators[j]))
        return B

    def adjoint_matrix(self, A: np.ndarray) -> np.ndarray:
        """Matrix of ad_A in the generator basis: (ad_A)_ij such that
        [A, T_j] = sum_i (ad_A)_ij T_i.

        Uses the metric (Killing form or identity) to extract components.
        """
        mat = np.zeros((self.dim, self.dim))
        for j in range(self.dim):
            bracket_result = self.bracket(A, self.generators[j])
            for i in range(self.dim):
                mat[i, j] = np.trace(self.generators[i].T @ bracket_result)
        # Solve for coefficients using overlap matrix
        overlap = np.zeros((self.dim, self.dim))
        for i in range(self.dim):
            for j in range(self.dim):
                overlap[i, j] = np.trace(self.generators[i].T @ self.generators[j])
        overlap_inv = np.linalg.inv(overlap)
        return overlap_inv @ mat

    def casimir(self, generator_indices: list) -> np.ndarray:
        """Compute Casimir C2 = sum_i (ad_{T_i})^2 for given generator indices."""
        C2 = np.zeros((self.dim, self.dim))
        for idx in generator_indices:
            M = self.adjoint_matrix(self.generators[idx])
            C2 += M @ M
        return C2

    def structure_constants(self) -> np.ndarray:
        """Compute structure constants f^k_{ij} where [T_i, T_j] = f^k_{ij} T_k."""
        f = np.zeros((self.dim, self.dim, self.dim))
        overlap = np.zeros((self.dim, self.dim))
        for i in range(self.dim):
            for j in range(self.dim):
                overlap[i, j] = np.trace(self.generators[i].T @ self.generators[j])
        overlap_inv = np.linalg.inv(overlap)
        for i in range(self.dim):
            for j in range(self.dim):
                bracket_ij = self.bracket(self.generators[i], self.generators[j])
                components = np.array([np.trace(self.generators[k].T @ bracket_ij)
                                       for k in range(self.dim)])
                f[:, i, j] = overlap_inv @ components
        return f
