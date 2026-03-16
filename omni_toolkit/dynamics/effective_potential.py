"""
Effective Potentials — Coleman-Weinberg Mechanism
==================================================

General Coleman-Weinberg effective potential computation for
classically conformal theories. Includes RG improvement.

Generalized from coleman_weinberg_su2R.py.

The CW potential at 1-loop in MS-bar:
  V = sum_i (n_i / 64 pi^2) M_i^4 [ln(M_i^2 / mu^2) - C_i]

where:
  n_i = degrees of freedom (with sign: +1 bosons, -1 fermions)
  M_i = field-dependent mass
  C_i = 5/6 (gauge), 3/2 (scalar/fermion) in MS-bar
"""

import numpy as np
import math
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Tuple
from scipy.optimize import minimize_scalar
from scipy.integrate import solve_ivp


@dataclass
class Particle:
    """A particle species contributing to the CW potential."""
    name: str
    dof: int               # Degrees of freedom (negative for fermions)
    mass_sq_coeff: float = 0.0  # M^2 = coeff * v^2
    C: float = 5.0 / 6.0   # MS-bar constant: 5/6 for gauge, 3/2 for scalar/fermion
    coupling_sq: Optional[float] = None  # Alias for mass_sq_coeff

    def __post_init__(self):
        if self.coupling_sq is not None:
            self.mass_sq_coeff = self.coupling_sq

    @property
    def is_fermion(self) -> bool:
        return self.dof < 0


class ColemanWeinbergPotential:
    """1-loop Coleman-Weinberg effective potential."""

    def __init__(self, particles: List[Particle]):
        self.particles = particles

    def V(self, v: float, mu: float) -> float:
        """Compute V_CW(v) at renormalization scale mu."""
        if v <= 0:
            return 0.0

        total = 0.0
        for p in self.particles:
            M_sq = p.mass_sq_coeff * v**2
            if M_sq > 0:
                sign = 1 if p.dof > 0 else -1
                n = abs(p.dof)
                total += sign * (n / (64 * math.pi**2)) * M_sq**2 * (
                    math.log(M_sq / mu**2) - p.C
                )
        return total

    def B_coefficient(self) -> float:
        """Compute the B coefficient: V ~ B * v^4 * [ln(v/mu) + const]."""
        B = 0.0
        for p in self.particles:
            sign = 1 if p.dof > 0 else -1
            n = abs(p.dof)
            B += sign * (n / (64 * math.pi**2)) * p.mass_sq_coeff**2
        return B

    def find_minimum(self, mu: float, log_v_range: Tuple[float, float] = (2, 18)) -> Tuple[float, float]:
        """Find the minimum of V_CW(v).

        Returns (v_min, V_min).
        """
        result = minimize_scalar(
            lambda lv: self.V(10**lv, mu),
            bounds=log_v_range,
            method='bounded'
        )
        v_min = 10**result.x
        V_min = result.fun
        return v_min, V_min

    def dimensional_transmutation_scale(self, Lambda: float,
                                         beta_lambda: float) -> float:
        """Compute the CW-generated scale via dimensional transmutation.

        v = Lambda * exp(something) where the "something" depends on
        the ratio beta_lambda / B.

        Returns v_min.
        """
        B = self.B_coefficient()
        if abs(beta_lambda / 3 + 8 * B) < 1e-20:
            return Lambda  # No hierarchy

        t_min = -2 * B / (beta_lambda / 3 + 8 * B)
        return Lambda * math.exp(t_min)


class RGImprovedPotential:
    """RG-improved effective potential with running couplings."""

    def __init__(self, cw_potential: ColemanWeinbergPotential,
                 rge_system: Callable,
                 initial_conditions: List[float],
                 Lambda_UV: float):
        """
        Args:
            cw_potential: The CW potential (used for structure)
            rge_system: Function (t, y) -> dy/dt for the coupled RGEs
                        where t = ln(mu / Lambda_UV)
            initial_conditions: [lambda, alpha_1^{-1}, alpha_2^{-1}, ...]
            Lambda_UV: UV cutoff scale
        """
        self.cw = cw_potential
        self.rge = rge_system
        self.y0 = initial_conditions
        self.Lambda_UV = Lambda_UV
        self._solution = None

    def solve_rge(self, mu_min: float = 100.0, n_points: int = 2000):
        """Solve the coupled RGE system from Lambda_UV down to mu_min."""
        t_span = (0, -math.log(self.Lambda_UV / mu_min))
        t_eval = np.linspace(0, t_span[1], n_points)

        self._solution = solve_ivp(
            self.rge, t_span, self.y0, t_eval=t_eval,
            method='RK45', rtol=1e-10, atol=1e-12
        )
        return self._solution

    def running_couplings_at(self, mu: float) -> Optional[np.ndarray]:
        """Interpolate running couplings at scale mu."""
        if self._solution is None:
            self.solve_rge()

        t = math.log(mu / self.Lambda_UV)
        t_vals = self._solution.t

        idx = np.searchsorted(-t_vals, -t)
        if idx <= 0 or idx >= len(t_vals):
            return None

        frac = (t - t_vals[idx - 1]) / (t_vals[idx] - t_vals[idx - 1])
        y = self._solution.y[:, idx - 1] + frac * (
            self._solution.y[:, idx] - self._solution.y[:, idx - 1]
        )
        return y

    def V_eff(self, v: float) -> float:
        """RG-improved effective potential V(v) with running couplings at mu = v."""
        couplings = self.running_couplings_at(v)
        if couplings is None:
            return 0.0

        lam = couplings[0]
        V_tree = (lam / 24) * v**4
        # 1-loop correction is small when mu = v (logs are O(ln(g)))
        return V_tree + self.cw.V(v, v)

    def find_minimum(self, log_v_range: Tuple[float, float] = (2, 17)) -> Tuple[float, float]:
        """Find the minimum of V_eff(v)."""
        result = minimize_scalar(
            lambda lv: self.V_eff(10**lv),
            bounds=log_v_range,
            method='bounded'
        )
        return 10**result.x, result.fun


@dataclass
class BetaFunctionCoefficients:
    """Coefficients for the quartic coupling beta function.

    beta_lambda = (1/16pi^2) [a_self * lambda^2
                               + a_gauge * lambda * g^2
                               - c_gauge * g^4
                               + a_yukawa * lambda * f^2
                               - c_yukawa * f^4]
    """
    a_self: float = 14.0
    a_gauge: float = 24.0
    c_gauge: float = 12.0
    a_yukawa: float = 0.0
    c_yukawa: float = 0.0

    def beta_lambda(self, lam: float, g: float, f: float = 0.0) -> float:
        return (1 / (16 * math.pi**2)) * (
            self.a_self * lam**2
            + self.a_gauge * lam * g**2
            - self.c_gauge * g**4
            + self.a_yukawa * lam * f**2
            - self.c_yukawa * f**4
        )


# =====================================================================
# Backward-compatible wrapper for pati_salam.py
# =====================================================================

class ColemanWeinberg:
    """Backward-compatible wrapper around ColemanWeinbergPotential.

    Accepts the old constructor signature: ColemanWeinberg(particles, M_UV).
    The old Particle had 'coupling_sq' instead of 'mass_sq_coeff'.
    """

    def __init__(self, particles, M_UV: float):
        self.M_UV = M_UV
        # Convert old-style particles (coupling_sq) to new-style (mass_sq_coeff)
        converted = []
        for p in particles:
            if hasattr(p, 'mass_sq_coeff'):
                converted.append(p)
            else:
                coeff = getattr(p, 'coupling_sq', 0.0)
                converted.append(Particle(p.name, p.dof, coeff, getattr(p, 'C', 5.0/6.0)))
        self._cw = ColemanWeinbergPotential(converted)

    def B_coefficient(self) -> float:
        return self._cw.B_coefficient()

    def find_minimum(self) -> dict:
        v_min, V_min = self._cw.find_minimum(self.M_UV)
        return {
            'v_min': v_min,
            'V_min': V_min,
            'v_over_MUV': v_min / self.M_UV if self.M_UV > 0 else float('inf'),
        }

    def instanton_scale(self, g: float, N_eff: float = 1.0) -> float:
        """Non-perturbative scale M_UV * exp(-8π²/(N_eff * g²))."""
        S_eff = 8 * math.pi ** 2 / (N_eff * g ** 2)
        return self.M_UV * math.exp(-S_eff)


def su2R_breaking_particles(g_R: float, g_BL: float, f_nu: float = 0.0,
                             n_gen: int = 3) -> List[Particle]:
    """Particle spectrum for SU(2)_R breaking by right-handed triplet.

    Returns the particles that get mass from v_R = <Delta_R^0>.
    """
    return [
        Particle("W_R±", dof=6, mass_sq_coeff=g_R**2, C=5/6),
        Particle("Z'", dof=3, mass_sq_coeff=g_R**2 + g_BL**2, C=5/6),
        Particle("nu_R", dof=-2 * n_gen, mass_sq_coeff=f_nu**2, C=3/2),
    ]
