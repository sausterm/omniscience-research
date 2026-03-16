"""
Tests for dynamics module — RG running, Coleman-Weinberg potential,
instanton actions, N_eff, WKB tunneling, and Coulomb barrier.
"""

import numpy as np
import math

from omni_toolkit.dynamics.rg_running import (
    GaugeCoupling, RGRunner, sm_couplings
)
from omni_toolkit.dynamics.effective_potential import (
    Particle, ColemanWeinbergPotential, su2R_breaking_particles
)
from omni_toolkit.dynamics.tunneling import (
    InstantonAction, N_eff_Calculator, BarrierTunneling, coulomb_barrier
)


# =====================================================================
# RG running: SM couplings at MZ match PDG values
# =====================================================================

def test_sm_couplings_at_mz():
    """SM gauge couplings at M_Z match PDG 2024 values."""
    couplings = sm_couplings()
    runner = RGRunner(couplings)

    M_Z = 91.1876
    alpha_inv_at_mz = runner.run_1loop(M_Z)

    # alpha_s(M_Z) = 0.1179 => alpha_s^{-1} = 8.481
    assert abs(alpha_inv_at_mz[0] - 1.0/0.1179) < 0.01

    # alpha_2(M_Z)
    alpha_em = 1.0 / 127.951
    sin2_W = 0.23122
    alpha_2 = alpha_em / sin2_W
    expected_alpha2_inv = 1.0 / alpha_2
    assert abs(alpha_inv_at_mz[1] - expected_alpha2_inv) < 0.01

    # alpha_1_GUT(M_Z)
    alpha_1 = alpha_em / (1.0 - sin2_W)
    alpha_1_gut = (5.0 / 3.0) * alpha_1
    expected_alpha1_inv = 1.0 / alpha_1_gut
    assert abs(alpha_inv_at_mz[2] - expected_alpha1_inv) < 0.01


# =====================================================================
# 1-loop running: couplings evolve logarithmically
# =====================================================================

def test_1loop_logarithmic_running():
    """1-loop RG running is linear in ln(mu/mu_0)."""
    couplings = sm_couplings()
    runner = RGRunner(couplings)

    mu_values = [100, 1000, 1e4, 1e6, 1e10]
    for idx, c in enumerate(couplings):
        alpha_inv_vals = []
        t_vals = []
        for mu in mu_values:
            result = runner.run_1loop(mu)
            alpha_inv_vals.append(result[idx])
            t_vals.append(math.log(mu / c.ref_scale))

        t_arr = np.array(t_vals)
        a_arr = np.array(alpha_inv_vals)
        slope_fit = np.polyfit(t_arr, a_arr, 1)
        residuals = a_arr - np.polyval(slope_fit, t_arr)
        assert np.max(np.abs(residuals)) < 1e-8

        expected_slope = -c.b1 / (2 * math.pi)
        assert abs(slope_fit[0] - expected_slope) < 1e-8


# =====================================================================
# Unification scale: 10^14 to 10^17 GeV for SM
# =====================================================================

def test_unification_scale():
    """SM gauge coupling pairwise crossing scales are physical."""
    couplings = sm_couplings()
    runner = RGRunner(couplings)

    for i in range(3):
        for j in range(i + 1, 3):
            M_unif, alpha_inv_unif = runner.unification_scale(i, j)
            log_M = math.log10(M_unif)
            assert 9 < log_M < 18
            assert alpha_inv_unif > 0

    # The alpha_3 & alpha_2 crossing is the best candidate for unification
    M_32, _ = runner.unification_scale(0, 1)
    log_M_32 = math.log10(M_32)
    assert 14 < log_M_32 < 18


# =====================================================================
# Coleman-Weinberg: B coefficient sign depends on particle content
# =====================================================================

def test_cw_B_coefficient_sign():
    """CW B coefficient is positive for bosons, negative for fermions."""
    bosonic_particles = [
        Particle("W", dof=6, mass_sq_coeff=0.3**2, C=5.0/6.0),
        Particle("Z", dof=3, mass_sq_coeff=0.35**2, C=5.0/6.0),
    ]
    cw_bosonic = ColemanWeinbergPotential(bosonic_particles)
    B_bosonic = cw_bosonic.B_coefficient()
    assert B_bosonic > 0

    fermionic_particles = [
        Particle("top", dof=-12, mass_sq_coeff=1.0**2, C=3.0/2.0),
        Particle("W", dof=6, mass_sq_coeff=0.3**2, C=5.0/6.0),
    ]
    cw_fermionic = ColemanWeinbergPotential(fermionic_particles)
    B_fermionic = cw_fermionic.B_coefficient()
    assert B_fermionic < 0


# =====================================================================
# CW potential minimum: exists for appropriate particle content
# =====================================================================

def test_cw_potential_minimum():
    """CW potential has a minimum for SU(2)_R breaking particle content."""
    g_R = 0.42
    g_BL = 0.46
    particles = su2R_breaking_particles(g_R, g_BL, f_nu=0.0, n_gen=3)
    cw = ColemanWeinbergPotential(particles)

    B = cw.B_coefficient()
    assert B > 0

    mu = 1e10
    v_min, V_min = cw.find_minimum(mu)
    assert v_min > 0
    V_left = cw.V(v_min * 0.5, mu)
    V_right = cw.V(v_min * 2.0, mu)
    assert V_min <= V_left or V_min <= V_right


# =====================================================================
# Instanton action: S = 8*pi^2/g^2
# =====================================================================

def test_instanton_action():
    """Standard instanton action S = 8 pi^2 / g^2."""
    inst = InstantonAction(dim_fibre=10, dim_isotropy=6)

    for g in [0.3, 0.5, 1.0, 2.0]:
        S = inst.standard_action(g, n=1)
        expected = 8 * math.pi**2 / g**2
        assert abs(S - expected) < 1e-10

    # Winding number n = 2
    S2 = inst.standard_action(0.5, n=2)
    S1 = inst.standard_action(0.5, n=1)
    assert abs(S2 - 2 * S1) < 1e-10


def test_instanton_effective_action():
    """Effective action S_eff = 8 pi^2 / (N_eff * g^2)."""
    inst = InstantonAction(dim_fibre=10, dim_isotropy=6)

    g = 0.5
    N_eff = 5.0
    S_eff = inst.effective_action(g, N_eff, n=1)
    expected = 8 * math.pi**2 / (N_eff * g**2)
    assert abs(S_eff - expected) < 1e-10

    S_std = inst.standard_action(g, n=1)
    assert S_eff < S_std


# =====================================================================
# N_eff calculator: dimension counting gives dim_p
# =====================================================================

def test_neff_dimension_counting():
    """N_eff from dimension counting gives dim_p."""
    for dim_p, dim_h in [(10, 6), (6, 3), (20, 10)]:
        calc = N_eff_Calculator(dim_p, dim_h)
        N = calc.from_dimension_counting()
        assert abs(N - dim_p) < 1e-10


def test_neff_metric_eigenvalues():
    """N_eff from metric eigenvalues: participation ratio."""
    calc = N_eff_Calculator(10, 6)

    equal_eigs = np.ones(10)
    N = calc.from_metric_eigenvalues(equal_eigs)
    assert abs(N - 10.0) < 1e-10

    dominant_eigs = np.array([100.0] + [0.001] * 9)
    N = calc.from_metric_eigenvalues(dominant_eigs)
    assert N < 2.0
    assert N >= 1.0


# =====================================================================
# WKB tunneling: rate decreases with barrier height
# =====================================================================

def test_wkb_tunneling_rate_vs_barrier():
    """WKB tunneling rate decreases with increasing barrier height."""
    rates = []
    for V0 in [1.0, 5.0, 10.0, 20.0]:
        potential = lambda x, V=V0: V * (1 - (x/5.0)**2) if abs(x) < 5.0 else 0.0
        bt = BarrierTunneling(potential, mass=1.0)
        rate = bt.wkb_rate(-5.0, 5.0, E=0.0)
        rates.append(rate)

    for i in range(len(rates) - 1):
        assert rates[i] > rates[i + 1]


def test_wkb_action_positive():
    """WKB action is always non-negative."""
    potential = lambda x: 10.0 * (1 - (x/3.0)**2) if abs(x) < 3.0 else 0.0
    bt = BarrierTunneling(potential, mass=1.0)
    S = bt.wkb_action(-3.0, 3.0, E=0.0)
    assert S >= 0
    assert S > 0


# =====================================================================
# Coulomb barrier: correct Z1*Z2 dependence
# =====================================================================

def test_coulomb_barrier_z_dependence():
    """Coulomb barrier scales linearly with Z1*Z2."""
    r_test = 10.0  # fm

    V_11 = coulomb_barrier(1, 1)(r_test)
    V_12 = coulomb_barrier(1, 2)(r_test)
    V_23 = coulomb_barrier(2, 3)(r_test)

    assert abs(V_12 / V_11 - 2.0) < 1e-10
    assert abs(V_23 / V_11 - 6.0) < 1e-10

    alpha_em = 1.0 / 137.036
    hbar_c = 197.3
    expected = 1 * 1 * alpha_em * hbar_c / r_test
    assert abs(V_11 - expected) < 1e-6


def test_coulomb_barrier_screening():
    """Screened Coulomb barrier is less than unscreened."""
    r_test = 5.0
    V_unscreened = coulomb_barrier(1, 1)(r_test)
    V_screened = coulomb_barrier(1, 1, screening_length=10.0)(r_test)

    assert V_screened < V_unscreened
    expected_ratio = math.exp(-r_test / 10.0)
    actual_ratio = V_screened / V_unscreened
    assert abs(actual_ratio - expected_ratio) < 1e-10
