"""
Chern-Simons Theory and Topological Invariants
===============================================

Implements Chern-Simons gauge theory computations relevant to
topological quantum computing and the Metric Bundle Programme.

The CS action S_CS = (k/4pi) int Tr(A ^ dA + 2/3 A ^ A ^ A)
determines:
  - Anyon statistics (theta = pi/k for U(1))
  - Jones polynomial values (knot invariants)
  - 3-manifold invariants (Witten invariants)

Connection to Pati-Salam:
  - pi_3(GL+(4)/SO(3,1)) = Z supports instantons
  - The instanton number IS a Chern number
  - CS level k determines which anyon model emerges

References:
  - Witten, Commun. Math. Phys. 121, 351 (1989)
  - Freed & Hopkins, arXiv:1604.06527
  - Kitaev, Ann. Phys. 321, 2-111 (2006)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List


@dataclass
class ChernSimonsTheory:
    """Chern-Simons gauge theory at level k.

    Parameters
    ----------
    gauge_group : str
        Gauge group name ('U1', 'SU2', 'SU3', etc.).
    level : int
        Chern-Simons level k (positive integer).
    """
    gauge_group: str
    level: int

    def __post_init__(self):
        if self.level < 1:
            raise ValueError(f"CS level must be positive, got {self.level}")

    @property
    def central_charge(self) -> float:
        """Central charge of the boundary WZW model.

        For SU(N) at level k: c = k * dim(SU(N)) / (k + N)
        For U(1) at level k: c = 1
        """
        if self.gauge_group == 'U1':
            return 1.0
        elif self.gauge_group.startswith('SU'):
            N = int(self.gauge_group[2:])
            dim_g = N * N - 1
            return self.level * dim_g / (self.level + N)
        return 0.0

    @property
    def n_anyons(self) -> int:
        """Number of distinct anyon types.

        For U(1)_k: k types
        For SU(2)_k: k+1 types (spins 0, 1/2, ..., k/2)
        """
        if self.gauge_group == 'U1':
            return self.level
        elif self.gauge_group == 'SU2':
            return self.level + 1
        elif self.gauge_group.startswith('SU'):
            N = int(self.gauge_group[2:])
            # Number of integrable highest weight representations
            from math import comb
            return comb(self.level + N - 1, N - 1)
        return 1

    def anyon_statistics(self, charge: int = 1) -> float:
        """Topological spin / statistics parameter.

        For U(1)_k: theta_q = pi * q^2 / k
        For SU(2)_k spin j: theta_j = 2*pi * j(j+1) / (k+2)
        """
        if self.gauge_group == 'U1':
            return np.pi * charge ** 2 / self.level
        elif self.gauge_group == 'SU2':
            j = charge / 2.0  # charge = 2j
            return 2 * np.pi * j * (j + 1) / (self.level + 2)
        return 0.0

    def mutual_statistics(self, charge_a: int, charge_b: int) -> float:
        """Mutual braiding phase between two anyons.

        For U(1)_k: theta_{ab} = 2*pi * a*b / k
        """
        if self.gauge_group == 'U1':
            return 2 * np.pi * charge_a * charge_b / self.level
        elif self.gauge_group == 'SU2':
            ja, jb = charge_a / 2.0, charge_b / 2.0
            # Simplified: use conformal weight difference
            return 2 * np.pi * ja * jb / (self.level + 2)
        return 0.0

    def quantum_dimension(self, charge: int = 1) -> float:
        """Quantum dimension of an anyon.

        For U(1)_k: d_q = 1 (all abelian)
        For SU(2)_k spin j: d_j = sin(pi(2j+1)/(k+2)) / sin(pi/(k+2))
        """
        if self.gauge_group == 'U1':
            return 1.0
        elif self.gauge_group == 'SU2':
            j = charge / 2.0
            return (np.sin(np.pi * (2 * j + 1) / (self.level + 2)) /
                    np.sin(np.pi / (self.level + 2)))
        return 1.0

    def total_quantum_dimension(self) -> float:
        """Total quantum dimension D = sqrt(sum d_a^2).

        For SU(2)_k: D = sqrt((k+2) / 2) / sin(pi/(k+2))
        """
        if self.gauge_group == 'U1':
            return np.sqrt(float(self.level))
        elif self.gauge_group == 'SU2':
            return np.sqrt((self.level + 2) / 2.0) / np.sin(np.pi / (self.level + 2))
        return 1.0

    def s_matrix(self) -> np.ndarray:
        """Modular S-matrix.

        For SU(2)_k:
            S_{jj'} = sqrt(2/(k+2)) * sin(pi(2j+1)(2j'+1)/(k+2))

        The S-matrix diagonalizes the fusion rules via the Verlinde formula.
        """
        if self.gauge_group == 'U1':
            k = self.level
            S = np.zeros((k, k), dtype=complex)
            for a in range(k):
                for b in range(k):
                    S[a, b] = np.exp(2j * np.pi * a * b / k) / np.sqrt(k)
            return S

        elif self.gauge_group == 'SU2':
            n = self.level + 1
            S = np.zeros((n, n), dtype=complex)
            prefactor = np.sqrt(2.0 / (self.level + 2))
            for j1 in range(n):
                for j2 in range(n):
                    S[j1, j2] = prefactor * np.sin(
                        np.pi * (j1 + 1) * (j2 + 1) / (self.level + 2))
            return S

        return np.array([[1.0]])

    def t_matrix(self) -> np.ndarray:
        """Modular T-matrix (diagonal, entries = topological spins).

        T_{jj'} = delta_{jj'} * exp(2pi*i * h_j) where h_j is conformal weight.
        """
        if self.gauge_group == 'U1':
            k = self.level
            T = np.zeros((k, k), dtype=complex)
            for a in range(k):
                T[a, a] = np.exp(1j * np.pi * a ** 2 / k)
            return T

        elif self.gauge_group == 'SU2':
            n = self.level + 1
            T = np.zeros((n, n), dtype=complex)
            for j in range(n):
                h_j = j * (j + 2) / (4 * (self.level + 2))
                T[j, j] = np.exp(2j * np.pi * h_j)
            return T

        return np.array([[1.0]])

    def is_universal(self) -> bool:
        """Check if the theory supports universal quantum computation.

        SU(2) at level k >= 3 is universal (Fibonacci anyons at k=3).
        U(1) at any level is NOT universal (abelian anyons only).
        """
        if self.gauge_group == 'U1':
            return False
        elif self.gauge_group == 'SU2':
            return self.level >= 3
        return False

    def anyon_model_name(self) -> str:
        """Name of the anyon model."""
        if self.gauge_group == 'SU2':
            if self.level == 1:
                return "Semion"
            elif self.level == 2:
                return "Ising"
            elif self.level == 3:
                return "Fibonacci"
            else:
                return f"SU(2)_{self.level}"
        elif self.gauge_group == 'U1':
            return f"Z_{self.level} (abelian)"
        return f"{self.gauge_group}_{self.level}"


# ============================================================
# Jones Polynomial
# ============================================================

@dataclass
class KnotInvariant:
    """Result of a knot invariant computation."""
    knot_name: str
    jones_polynomial: Dict[float, complex]  # {exponent: coefficient}
    writhe: int
    cs_level: int

    def evaluate(self, t: complex) -> complex:
        """Evaluate the Jones polynomial at t."""
        return sum(coeff * t ** exp for exp, coeff in self.jones_polynomial.items())

    def __repr__(self) -> str:
        terms = []
        for exp in sorted(self.jones_polynomial.keys()):
            coeff = self.jones_polynomial[exp]
            if abs(coeff.imag) < 1e-10:
                coeff = coeff.real
            if exp == 0:
                terms.append(f"{coeff}")
            elif exp == 1:
                terms.append(f"{coeff}*t")
            else:
                terms.append(f"{coeff}*t^{exp}")
        poly_str = " + ".join(terms)
        return f"KnotInvariant({self.knot_name}, V(t) = {poly_str})"


def jones_polynomial_trefoil() -> KnotInvariant:
    """Jones polynomial of the trefoil knot.

    V(t) = -t^{-4} + t^{-3} + t^{-1}

    This is the simplest non-trivial knot invariant, computable
    from SU(2) Chern-Simons theory at any level k.
    """
    return KnotInvariant(
        knot_name="Trefoil (3_1)",
        jones_polynomial={-4: -1.0, -3: 1.0, -1: 1.0},
        writhe=3,
        cs_level=2,
    )


def jones_polynomial_figure_eight() -> KnotInvariant:
    """Jones polynomial of the figure-eight knot.

    V(t) = t^{-2} - t^{-1} + 1 - t + t^2
    """
    return KnotInvariant(
        knot_name="Figure-eight (4_1)",
        jones_polynomial={-2: 1.0, -1: -1.0, 0: 1.0, 1: -1.0, 2: 1.0},
        writhe=0,
        cs_level=2,
    )


def jones_polynomial_unknot() -> KnotInvariant:
    """Jones polynomial of the unknot: V(t) = 1."""
    return KnotInvariant(
        knot_name="Unknot",
        jones_polynomial={0: 1.0},
        writhe=0,
        cs_level=2,
    )


# ============================================================
# Witten invariants for 3-manifolds
# ============================================================

def witten_invariant_s3(cs: ChernSimonsTheory) -> complex:
    """Witten invariant of S^3.

    Z(S^3) = S_{00} for the modular S-matrix.
    For SU(2)_k: Z(S^3) = sqrt(2/(k+2)) * sin(pi/(k+2))
    """
    S = cs.s_matrix()
    return S[0, 0]


def witten_invariant_lens(cs: ChernSimonsTheory, p: int, q: int = 1) -> complex:
    """Witten invariant of lens space L(p, q).

    For SU(2)_k:
        Z(L(p,1)) = sum_j (S_{0j})^2 * exp(2pi*i*p*h_j)
    where h_j = j(j+2)/(4(k+2)) is the conformal weight.
    """
    if cs.gauge_group != 'SU2':
        raise NotImplementedError("Lens space invariants only for SU(2)")

    S = cs.s_matrix()
    T = cs.t_matrix()

    # Z(L(p,q)) via surgery formula
    result = 0.0 + 0j
    n = cs.level + 1
    for j in range(n):
        h_j = j * (j + 2) / (4 * (cs.level + 2))
        result += abs(S[0, j]) ** 2 * np.exp(2j * np.pi * p * h_j)

    return result


# ============================================================
# Connection to Pati-Salam fibre bundle
# ============================================================

def cs_from_instanton(gauge_coupling: float, instanton_number: int = 1) -> ChernSimonsTheory:
    """Derive Chern-Simons theory from instanton data.

    The instanton action S = 8*pi^2 * n / g^2 determines
    an effective CS level k = 8*pi^2 / g^2.

    For the Pati-Salam coupling g_PS ~ 0.52:
        k_eff = 8*pi^2 / 0.52^2 ~ 292

    Parameters
    ----------
    gauge_coupling : float
        Gauge coupling constant g.
    instanton_number : int
        Topological charge (winding number).

    Returns
    -------
    ChernSimonsTheory
        Effective CS theory with derived level.
    """
    k_eff = int(round(8 * np.pi ** 2 / gauge_coupling ** 2))
    return ChernSimonsTheory(gauge_group='SU2', level=max(1, k_eff))


def anomaly_to_code_constraint(anomaly_coefficients: Dict[str, int]) -> Dict[str, bool]:
    """Map anomaly cancellation conditions to code constraints.

    In the Metric Bundle Programme, anomaly cancellation ensures
    quantum consistency. The same conditions, when mapped to a
    topological code, ensure that all stabilizers commute.

    anomaly_free <=> valid CSS code

    Parameters
    ----------
    anomaly_coefficients : dict
        Anomaly coefficients: {'SU4_cubic': int, 'SU2L_cubic': int, ...}

    Returns
    -------
    dict
        Code validity conditions.
    """
    return {
        'all_stabilizers_commute': all(v == 0 for v in anomaly_coefficients.values()),
        'x_stabilizers_valid': anomaly_coefficients.get('SU4_cubic', 0) == 0,
        'z_stabilizers_valid': anomaly_coefficients.get('SU2L_cubic', 0) == 0,
        'mixed_valid': anomaly_coefficients.get('mixed_grav', 0) == 0,
    }
