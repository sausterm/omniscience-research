"""
Renormalization group running for gauge couplings.

Provides a generic RG runner that handles:
  - 1-loop and 2-loop beta functions
  - Multi-step breaking chains (e.g., PS -> LR -> SM)
  - Matching conditions at intermediate scales
  - Root-finding for unification scales
"""

import numpy as np
import math
from dataclasses import dataclass, field
from typing import Callable, Optional
from scipy.optimize import fsolve


@dataclass
class BetaSystem:
    """A system of 1-loop (and optionally 2-loop) beta functions.

    Parameters
    ----------
    b1 : ndarray
        1-loop beta coefficients, shape (n_couplings,).
    b2 : ndarray, optional
        2-loop beta matrix, shape (n_couplings, n_couplings).
    label : str
        Name of this regime (e.g., "SM", "LR", "PS").
    coupling_labels : list of str
        Names of each coupling.
    """

    b1: np.ndarray
    b2: Optional[np.ndarray] = None
    label: str = ""
    coupling_labels: list = field(default_factory=list)

    def __post_init__(self):
        self.b1 = np.asarray(self.b1, dtype=float)
        self.n_couplings = len(self.b1)
        if self.b2 is not None:
            self.b2 = np.asarray(self.b2, dtype=float)
        if not self.coupling_labels:
            self.coupling_labels = [f"alpha_{i}" for i in range(self.n_couplings)]

    def rhs(self, alpha_inv: np.ndarray, two_loop: bool = True) -> np.ndarray:
        """d(alpha_i^{-1})/dt where t = ln(mu/mu_0) / (2 pi)."""
        d = -self.b1.copy()
        if two_loop and self.b2 is not None:
            a = np.where(alpha_inv > 0, 1.0 / alpha_inv, 1e-10)
            d -= self.b2 @ a
        return d


class RGRunner:
    """Generic RG evolution with multi-step breaking chains.

    Handles running couplings between arbitrary scales using RK4 integration,
    with matching conditions at intermediate thresholds.
    """

    @staticmethod
    def rk4_integrate(rhs: Callable, y0: np.ndarray, t_start: float,
                      t_end: float, n_steps: int = 10000, **kwargs) -> np.ndarray:
        """RK4 integrator for ODE systems.

        Parameters
        ----------
        rhs : callable
            Function rhs(y, **kwargs) -> dy/dt.
        y0 : ndarray
            Initial conditions.
        t_start, t_end : float
            Integration interval in t = ln(mu/mu_0) / (2 pi).
        n_steps : int
            Number of integration steps.
        """
        dt = (t_end - t_start) / n_steps
        y = np.asarray(y0, dtype=float).copy()
        for _ in range(n_steps):
            k1 = np.asarray(rhs(y, **kwargs), dtype=float)
            k2 = np.asarray(rhs(y + 0.5 * dt * k1, **kwargs), dtype=float)
            k3 = np.asarray(rhs(y + 0.5 * dt * k2, **kwargs), dtype=float)
            k4 = np.asarray(rhs(y + dt * k3, **kwargs), dtype=float)
            y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        return y

    @staticmethod
    def run_1loop_analytic(alpha_inv_0: np.ndarray, b: np.ndarray,
                           delta_t: float) -> np.ndarray:
        """Analytic 1-loop evolution: alpha^{-1}(t) = alpha^{-1}(0) - b * delta_t."""
        return alpha_inv_0 - b * delta_t

    @staticmethod
    def solve_two_scale(system_low: BetaSystem, system_high: BetaSystem,
                        alpha_inv_measured: np.ndarray, M_ref: float,
                        matching: Callable, unification_condition: Callable,
                        x0: np.ndarray = None) -> Optional[dict]:
        """Solve for two intermediate scales (M_R, M_C) in a breaking chain.

        Parameters
        ----------
        system_low : BetaSystem
            Beta functions for the low-energy regime (e.g., SM).
        system_high : BetaSystem
            Beta functions for the high-energy regime (e.g., LR).
        alpha_inv_measured : ndarray
            Measured coupling inverses at M_ref.
        M_ref : float
            Reference scale (e.g., M_Z).
        matching : callable
            Function(alpha_inv_low_at_MR) -> alpha_inv_high_at_MR.
        unification_condition : callable
            Function(alpha_inv_high_at_MC) -> residuals.
        x0 : ndarray, optional
            Initial guess [log10(M_R), log10(M_C)].

        Returns dict with 'M_R', 'M_C', 'alpha_unified', etc.
        """
        def residual(x):
            log10_MR, log10_MC = x
            M_R = 10 ** log10_MR
            M_C = 10 ** log10_MC
            if M_R <= M_ref or M_C <= M_R:
                return np.array([1e6, 1e6])

            tR = math.log(M_R / M_ref) / (2 * math.pi)
            tC = math.log(M_C / M_ref) / (2 * math.pi)
            Dt = tC - tR

            # Run low-energy system from M_ref to M_R
            ainv_MR = RGRunner.rk4_integrate(
                system_low.rhs, alpha_inv_measured, 0.0, tR,
                two_loop=(system_low.b2 is not None))

            # Match to high-energy system
            ainv_MR_high = matching(ainv_MR, Dt)

            # Run high-energy system from M_R to M_C (1-loop analytic)
            ainv_MC = RGRunner.run_1loop_analytic(ainv_MR_high, system_high.b1, Dt)

            return unification_condition(ainv_MC, ainv_MR)

        if x0 is None:
            x0 = np.array([9.0, 16.0])

        sol = fsolve(residual, x0, full_output=True, maxfev=5000, epsfcn=1e-10)
        x_sol, info, ier, msg = sol
        resid = residual(x_sol)

        if np.max(np.abs(resid)) > 0.1:
            return None

        M_R = 10 ** x_sol[0]
        M_C = 10 ** x_sol[1]
        return {
            'M_R': M_R, 'M_C': M_C,
            'log10_MR': x_sol[0], 'log10_MC': x_sol[1],
            'residual': resid,
        }

    @staticmethod
    def compute_lr_betas(n_bidoublet: int = 1, has_delta_L: bool = False,
                         has_delta_R: bool = True) -> np.ndarray:
        """Compute 1-loop betas for SU(3)_c x SU(2)_L x SU(2)_R x U(1)_{B-L}.

        Standard LR model with n_g = 3 generations.

        Returns array [b_3, b_2L, b_2R, b_BL].
        """
        n_g = 3
        gauge = np.array([-11.0, -22.0 / 3, -22.0 / 3, 0.0])
        fermion_per_gen = np.array([4.0 / 3, 4.0 / 3, 4.0 / 3, 4.0 / 3])
        s_bidoublet = np.array([0.0, 1.0 / 3, 1.0 / 3, 0.0])
        s_deltaR = np.array([0.0, 0.0, 2.0 / 3, 3.0 / 2])
        s_deltaL = np.array([0.0, 2.0 / 3, 0.0, 3.0 / 2])

        b = gauge + n_g * fermion_per_gen + n_bidoublet * s_bidoublet
        if has_delta_R:
            b += s_deltaR
        if has_delta_L:
            b += s_deltaL
        return b
