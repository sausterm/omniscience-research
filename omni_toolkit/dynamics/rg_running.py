"""
Renormalization Group Running
=============================

Beta functions and RG flow for gauge couplings, Yukawa couplings,
and scalar quartic couplings.

Generalized from zero_parameter_rg.py.
"""

import numpy as np
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
from scipy.integrate import solve_ivp


@dataclass
class GaugeCoupling:
    """A gauge coupling with its beta function coefficients."""
    name: str
    group: str           # "SU(3)", "SU(2)", "U(1)", etc.
    alpha_inv: float     # alpha^{-1} at reference scale
    b1: float            # 1-loop beta coefficient
    b2: float = 0.0      # 2-loop beta coefficient
    ref_scale: float = 91.1876  # Reference scale (GeV)


class RGRunner:
    """Run gauge couplings between scales using beta functions."""

    def __init__(self, couplings: List[GaugeCoupling]):
        self.couplings = couplings

    def run_1loop(self, mu: float) -> List[float]:
        """Run all couplings from ref_scale to mu at 1-loop.

        alpha_i^{-1}(mu) = alpha_i^{-1}(mu_0) - (b_i / 2pi) ln(mu / mu_0)

        Returns list of alpha^{-1} values.
        """
        results = []
        for c in self.couplings:
            t = math.log(mu / c.ref_scale)
            alpha_inv = c.alpha_inv - (c.b1 / (2 * math.pi)) * t
            results.append(alpha_inv)
        return results

    def run_2loop(self, mu_target: float, n_points: int = 1000) -> np.ndarray:
        """Run all couplings from ref_scale to mu_target at 2-loop.

        Uses coupled RGEs with 2-loop beta functions.
        Returns array of shape (n_couplings, n_points).
        """
        n = len(self.couplings)

        def rge_system(t, y):
            dy = np.zeros(n)
            alphas = [1.0 / y[i] if y[i] > 0 else 0.0 for i in range(n)]
            for i in range(n):
                b1 = self.couplings[i].b1
                b2 = self.couplings[i].b2
                dy[i] = -(b1 / (2 * math.pi)) - (b2 / (4 * math.pi**2)) * alphas[i]
            return dy

        t_start = 0
        t_end = math.log(mu_target / self.couplings[0].ref_scale)
        y0 = [c.alpha_inv for c in self.couplings]
        t_eval = np.linspace(t_start, t_end, n_points)

        sol = solve_ivp(rge_system, (t_start, t_end), y0,
                        t_eval=t_eval, method='RK45',
                        rtol=1e-10, atol=1e-12)
        return sol

    def unification_scale(self, i: int, j: int) -> Tuple[float, float]:
        """Find the scale where couplings i and j unify.

        Returns (M_unif, alpha_inv_unif) at 1-loop.
        """
        ci, cj = self.couplings[i], self.couplings[j]
        # alpha_i^{-1} = alpha_j^{-1} at mu = M_unif
        # ci.alpha_inv - ci.b1/(2pi) * t = cj.alpha_inv - cj.b1/(2pi) * t
        # t * (cj.b1 - ci.b1)/(2pi) = cj.alpha_inv - ci.alpha_inv
        delta_b = cj.b1 - ci.b1
        if abs(delta_b) < 1e-15:
            return float('inf'), 0.0

        t = 2 * math.pi * (cj.alpha_inv - ci.alpha_inv) / delta_b
        M_unif = ci.ref_scale * math.exp(t)
        alpha_inv = ci.alpha_inv - (ci.b1 / (2 * math.pi)) * t
        return M_unif, alpha_inv


def sm_couplings() -> List[GaugeCoupling]:
    """Standard Model gauge couplings at M_Z (PDG 2024)."""
    M_Z = 91.1876
    alpha_em = 1.0 / 127.951
    alpha_s = 0.1179
    sin2_W = 0.23122

    alpha_2 = alpha_em / sin2_W
    alpha_1 = alpha_em / (1.0 - sin2_W)
    alpha_1_gut = (5.0 / 3.0) * alpha_1

    # 1-loop beta coefficients (SM with 3 generations)
    b3 = -7.0
    b2 = -19.0 / 6.0
    b1_gut = 41.0 / 6.0

    # 2-loop contributions
    b3_2 = -26.0
    b2_2 = 35.0 / 6.0
    b1_2 = 199.0 / 18.0

    return [
        GaugeCoupling("alpha_3", "SU(3)", 1.0 / alpha_s, b3, b3_2, M_Z),
        GaugeCoupling("alpha_2", "SU(2)", 1.0 / alpha_2, b2, b2_2, M_Z),
        GaugeCoupling("alpha_1_GUT", "U(1)", 1.0 / alpha_1_gut, b1_gut, b1_2, M_Z),
    ]


def compute_lr_betas(n_bidoublet: int = 1, has_delta_L: bool = False,
                     has_delta_R: bool = True) -> np.ndarray:
    """Compute Left-Right model 1-loop beta coefficients from scratch.

    SU(3)_c × SU(2)_L × SU(2)_R × U(1)_{B-L,GUT}.
    Returns array [b_3, b_2L, b_2R, b_BL].
    """
    n_g = 3

    # Gauge: -(11/3)C₂(G)
    gauge = np.array([-11.0, -22.0/3, -22.0/3, 0.0])

    # Fermions per generation: 4/3 each (verified in TN21)
    fermion_per_gen = np.array([4.0/3, 4.0/3, 4.0/3, 4.0/3])

    # Scalars
    s_bidoublet = np.array([0.0, 1.0/3, 1.0/3, 0.0])
    s_deltaR = np.array([0.0, 0.0, 2.0/3, 3.0/2])
    s_deltaL = np.array([0.0, 2.0/3, 0.0, 3.0/2])

    b = gauge + n_g * fermion_per_gen + n_bidoublet * s_bidoublet
    if has_delta_R:
        b += s_deltaR
    if has_delta_L:
        b += s_deltaL

    return b


def lr_beta_coefficients(scenario: str = "A") -> Tuple[float, float, float, float]:
    """Left-Right model beta coefficients for various scalar scenarios.

    Scenario A: Φ(1,2,2) + Δ_R(1,1,3) — minimal
    Scenario B: Φ(1,2,2) + Δ_L(1,3,1) + Δ_R(1,1,3) — L-R symmetric
    Scenario C: 2Φ(1,2,2) + Δ_R(1,1,3)

    Returns (b_3, b_2L, b_2R, b_BL).
    """
    if scenario == "A":
        b = compute_lr_betas(1, False, True)
    elif scenario == "B":
        b = compute_lr_betas(1, True, True)
    elif scenario == "C":
        b = compute_lr_betas(2, False, True)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    return tuple(b)


# =====================================================================
# Backward-compatible wrappers for pati_salam.py
# =====================================================================

class BetaSystem:
    """Container for beta function coefficients (backward-compatible wrapper)."""

    def __init__(self, b1, b2=None, label="", coupling_labels=None):
        self.b1 = np.array(b1) if not isinstance(b1, np.ndarray) else b1
        self.b2 = np.array(b2) if b2 is not None else None
        self.label = label
        self.coupling_labels = coupling_labels or []


# Add static methods to RGRunner for backward compatibility
@staticmethod
def _rk4_integrate(rhs, y0, t0, t1, n_steps=1000):
    """Simple RK4 integrator."""
    dt = (t1 - t0) / n_steps
    y = np.array(y0, dtype=float)
    t = t0
    for _ in range(n_steps):
        k1 = np.array(rhs(y))
        k2 = np.array(rhs(y + 0.5 * dt * k1))
        k3 = np.array(rhs(y + 0.5 * dt * k2))
        k4 = np.array(rhs(y + dt * k3))
        y = y + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
    return y


@staticmethod
def _compute_lr_betas(n_higgs_bidoublet=1, has_delta_L=False, has_delta_R=True):
    """Compute Left-Right model beta coefficients.

    Returns array [b_3, b_2L, b_2R, b_BL].
    """
    return compute_lr_betas(n_higgs_bidoublet, has_delta_L, has_delta_R)


RGRunner.rk4_integrate = _rk4_integrate
RGRunner.compute_lr_betas = _compute_lr_betas
