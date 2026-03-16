"""
Vacuum alignment on S² from Sp(1) breaking.

Sp(1) ≅ SU(2) flavor symmetry acts on the three quaternion directions I, J, K.
Breaking Sp(1) → U(1) selects a direction v ∈ S² and generates
Froggatt-Nielsen charges for the three generations.

STATUS: The framework is DERIVED from quaternionic geometry.
        Sp(1) → U(1) gives q = (2, 2, 0) — two generations degenerate.
        Three distinct charges require two-step breaking or additional structure.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class VacuumAlignment:
    """Sp(1) breaking on S² and Froggatt-Nielsen charge computation.

    Parameters
    ----------
    breaking_direction : ndarray or None
        Unit vector v = (v₁, v₂, v₃) on S² specifying breaking direction.
        Default: K-direction = (0, 0, 1).
    """

    breaking_direction: Optional[np.ndarray] = None

    def __post_init__(self):
        if self.breaking_direction is None:
            self.breaking_direction = np.array([0.0, 0.0, 1.0])
        self.breaking_direction = np.asarray(self.breaking_direction, dtype=float)
        norm = np.linalg.norm(self.breaking_direction)
        if norm > 0:
            self.breaking_direction = self.breaking_direction / norm

    def fn_charges_sp1(self) -> np.ndarray:
        """Froggatt-Nielsen charges from Sp(1) → U(1) breaking.

        For breaking along v = (v₁, v₂, v₃):
            q_a = 2(1 - v_a²)  for a = 1, 2, 3 (generations I, J, K)

        Returns shape (3,) array of charges.

        NOTE: Breaking along any axis gives q = (2, 2, 0), i.e.,
        TWO generations always degenerate due to residual Z₂ symmetry.
        Three distinct charges require additional breaking.
        """
        v = self.breaking_direction
        return 2.0 * (1.0 - v**2)

    def fn_charges_two_step(self, epsilon_2: float = 0.5) -> np.ndarray:
        """FN charges from two-step Sp(1) → U(1) → {1} breaking.

        Stage 1: Sp(1) → U(1) along v, giving q₃ = 0, q₂ = q₁ = 2.
        Stage 2: U(1) → {1} with secondary parameter ε₂, splitting
                 the degenerate pair: q₁ = 3, q₂ = 1, q₃ = 0.

        Parameters
        ----------
        epsilon_2 : float
            Secondary breaking parameter (0 < ε₂ < 1).

        Returns shape (3,) array of effective charges.
        """
        q = self.fn_charges_sp1()
        # Sort: heaviest generation (smallest charge) last
        idx = np.argsort(q)[::-1]

        # Split the degenerate pair
        q_eff = np.zeros(3)
        q_eff[idx[2]] = 0.0              # Heaviest: q = 0
        q_eff[idx[1]] = q[idx[1]] * (1 - epsilon_2)    # Middle
        q_eff[idx[0]] = q[idx[0]] * (1 + epsilon_2)    # Lightest

        return q_eff

    def s2_potential(self, theta: float, phi: float,
                     loop_factor: float = 1.0) -> float:
        """Coleman-Weinberg potential on S² from fermion loops.

        V(θ, φ) ∝ Σ_a (q_a(θ,φ))² log(q_a(θ,φ)/Λ²)

        This is direction-dependent but has residual Z₂ symmetry.

        Parameters
        ----------
        theta, phi : float
            Spherical coordinates on S².
        loop_factor : float
            Overall loop suppression.
        """
        v = np.array([np.sin(theta)*np.cos(phi),
                       np.sin(theta)*np.sin(phi),
                       np.cos(theta)])
        q = 2.0 * (1.0 - v**2)

        # Regularized potential (avoid log(0))
        V = 0.0
        for qa in q:
            if qa > 1e-10:
                V += loop_factor * qa**2 * np.log(qa)
        return V

    def scan_s2_potential(self, n_theta: int = 50,
                          n_phi: int = 100) -> dict:
        """Scan CW potential over S² to find minima.

        Returns dict with min/max values and locations.
        """
        thetas = np.linspace(0.01, np.pi - 0.01, n_theta)
        phis = np.linspace(0, 2*np.pi, n_phi, endpoint=False)

        V_min = float('inf')
        V_max = float('-inf')
        loc_min = (0, 0)
        loc_max = (0, 0)

        for theta in thetas:
            for phi in phis:
                V = self.s2_potential(theta, phi)
                if V < V_min:
                    V_min = V
                    loc_min = (theta, phi)
                if V > V_max:
                    V_max = V
                    loc_max = (theta, phi)

        return {
            'V_min': V_min,
            'V_max': V_max,
            'min_location': loc_min,
            'max_location': loc_max,
            'anisotropy': (V_max - V_min) / abs(V_min) if abs(V_min) > 1e-15 else float('inf'),
        }

    def mass_ratios_from_charges(self, charges: np.ndarray,
                                  epsilon: float) -> np.ndarray:
        """Compute mass ratios m_i/m_3 from FN charges and ε.

        m_i/m_3 = ε^{q_i - q_3} where q_3 is the smallest charge.
        """
        q_min = np.min(charges)
        return epsilon ** (charges - q_min)
