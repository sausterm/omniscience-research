"""
Coleman-Weinberg effective potential for radiative symmetry breaking.

Generic CW potential parametrized by particle content:
  V = sum_i (n_i / 64 pi^2) M_i^4 [ln(M_i^2 / mu^2) - C_i]

Supports arbitrary gauge bosons, scalars, and fermions that get mass
from the symmetry-breaking VEV.
"""

import numpy as np
import math
from dataclasses import dataclass, field
from typing import Optional
from scipy.optimize import minimize_scalar


@dataclass
class Particle:
    """A particle species contributing to the CW potential.

    Parameters
    ----------
    name : str
        Particle name.
    dof : int
        Number of degrees of freedom (e.g., 6 for W_R^+-, 3 for Z', 2 for Majorana).
    coupling_sq : float
        M^2 = coupling_sq * v^2 (the mass-squared coefficient).
    is_fermion : bool
        Fermions enter with opposite sign.
    C : float
        MS-bar constant: 5/6 for gauge bosons, 3/2 for scalars/fermions.
    """

    name: str
    dof: int
    coupling_sq: float
    is_fermion: bool = False
    C: float = 5.0 / 6.0

    def __post_init__(self):
        if self.is_fermion:
            self.C = 3.0 / 2.0


class ColemanWeinberg:
    """Coleman-Weinberg effective potential for radiative symmetry breaking.

    Parameters
    ----------
    particles : list of Particle
        All particle species that get mass from the VEV.
    M_UV : float
        UV cutoff / matching scale (e.g., M_C for SU(2)_R breaking).
    """

    def __init__(self, particles: list, M_UV: float):
        self.particles = particles
        self.M_UV = M_UV

    def V_CW(self, v: float, mu: Optional[float] = None) -> float:
        """Compute the 1-loop CW potential.

        Parameters
        ----------
        v : float
            The VEV (symmetry-breaking scale).
        mu : float, optional
            Renormalization scale. Defaults to M_UV.
        """
        if v <= 0:
            return 0.0
        if mu is None:
            mu = self.M_UV

        V = 0.0
        for p in self.particles:
            M2 = p.coupling_sq * v ** 2
            if M2 <= 0:
                continue
            sign = -1 if p.is_fermion else 1
            V += sign * (p.dof / (64 * math.pi ** 2)) * M2 ** 2 * (
                math.log(M2 / mu ** 2) - p.C)
        return V

    def B_coefficient(self) -> float:
        """The field-independent coefficient B = sum n_i c_i^4 / (64 pi^2)."""
        B = 0.0
        for p in self.particles:
            sign = -1 if p.is_fermion else 1
            B += sign * (p.dof / (64 * math.pi ** 2)) * p.coupling_sq ** 2
        return B

    def find_minimum(self, log_v_range: tuple = (3, 18)) -> dict:
        """Find the minimum of V_CW by scanning.

        Returns dict with 'v_min', 'V_min', 'log10_v', 'v_over_MUV'.
        """
        def V_of_logv(lv):
            return self.V_CW(10 ** lv, mu=self.M_UV)

        res = minimize_scalar(V_of_logv, bounds=log_v_range, method='bounded')
        v_min = 10 ** res.x
        return {
            'v_min': v_min,
            'V_min': res.fun,
            'log10_v': res.x,
            'v_over_MUV': v_min / self.M_UV,
        }

    def find_minimum_rg_improved(self, run_couplings_fn, log_v_range: tuple = (3, 18),
                                 n_points: int = 500) -> dict:
        """Find minimum with RG-improved couplings.

        Parameters
        ----------
        run_couplings_fn : callable
            Function(mu) -> dict of coupling_sq values keyed by particle name.
        """
        best_v, best_V = None, float('inf')
        for lv in np.linspace(*log_v_range, n_points):
            v = 10 ** lv
            couplings = run_couplings_fn(v)
            if couplings is None:
                continue
            # Update particle couplings temporarily
            V = 0.0
            for p in self.particles:
                if p.name in couplings:
                    c_sq = couplings[p.name]
                else:
                    c_sq = p.coupling_sq
                M2 = c_sq * v ** 2
                if M2 <= 0:
                    continue
                sign = -1 if p.is_fermion else 1
                V += sign * (p.dof / (64 * math.pi ** 2)) * M2 ** 2 * (
                    math.log(c_sq) - p.C)  # mu = v cancels v^2 in log
            if V < best_V:
                best_V = V
                best_v = v

        if best_v is None:
            return {'v_min': None, 'V_min': None}
        return {
            'v_min': best_v,
            'V_min': best_V,
            'log10_v': math.log10(best_v),
            'v_over_MUV': best_v / self.M_UV,
        }

    def beta_lambda_gauge(self, couplings: dict) -> float:
        """Estimate beta_lambda at lambda=0 from gauge loops.

        Parameters
        ----------
        couplings : dict
            Maps particle name -> coupling_sq.
        """
        beta = 0.0
        for p in self.particles:
            if p.is_fermion:
                continue
            c_sq = couplings.get(p.name, p.coupling_sq)
            beta -= (p.dof / (16 * math.pi ** 2)) * c_sq ** 2
        return beta

    def instanton_scale(self, g_unified: float, N_eff: float = 1.0) -> float:
        """Estimate non-perturbative scale from instantons.

        Lambda_inst = M_UV * exp(-8 pi^2 / (N_eff * g^2))
        """
        exponent = -8 * math.pi ** 2 / (N_eff * g_unified ** 2)
        return self.M_UV * math.exp(exponent)
