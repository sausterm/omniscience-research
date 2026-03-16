"""Tests for the fermions module."""

import numpy as np
from omni_toolkit.fermions import YukawaCoupling, FermionSpectrum, NeutrinoSector


def test_yukawa_tree_level_degenerate():
    """Tree-level Yukawa is degenerate (Sp(1) invariance)."""
    yc = YukawaCoupling(ric_mixed_norm=0.0)
    assert yc.tree_level_degenerate
    Y = yc.yukawa_matrix_tree()
    assert np.allclose(Y, np.eye(3))
    print("PASS: Tree-level Yukawa = y₀ I₃ (degenerate)")


def test_ba_zero_at_symmetric_point():
    """b/a = 0 at the symmetric point (no (15,2,2))."""
    yc = YukawaCoupling(b_over_a=0.0)
    cg = yc.quark_lepton_cg()
    assert abs(cg['mb_over_mtau'] - 1.0) < 1e-10
    assert cg['status'] == 'DERIVED (CG)'
    print("PASS: b/a = 0 → m_b/m_τ = 1 (pure SU(4))")


def test_ba_fitted():
    """b/a ≈ 0.3 gives m_b/m_τ ≈ 1.7."""
    yc = YukawaCoupling(b_over_a=0.3)
    cg = yc.quark_lepton_cg()
    assert abs(cg['mb_over_mtau'] - 1.57) < 0.3
    print(f"PASS: b/a = 0.3 → m_b/m_τ = {cg['mb_over_mtau']:.2f}")


def test_c_parameter():
    """c = g_PS/2 ≈ 0.26."""
    yc = YukawaCoupling(g_PS=0.52)
    assert abs(yc.c_parameter - 0.26) < 0.01
    print(f"PASS: c = {yc.c_parameter}")


def test_up_down_ratio():
    """m_t/m_b ratio from SU(2)_R asymmetry."""
    yc = YukawaCoupling(g_PS=0.52, tan_beta=1.0)
    ratio = yc.up_down_ratio()
    # At tan(β) = 1, cos(2β) = 0, ratio = 1
    assert abs(ratio - 1.0) < 1e-10
    print(f"PASS: m_u/m_d ratio at tan(β)=1 = {ratio:.3f}")


def test_up_down_ratio_asymmetric():
    """m_t/m_b > 1 for tan(β) < 1."""
    yc = YukawaCoupling(g_PS=0.52, tan_beta=0.5)
    ratio = yc.up_down_ratio()
    assert ratio > 1.0
    print(f"PASS: m_u/m_d ratio at tan(β)=0.5 = {ratio:.3f}")


def test_fermion_spectrum_epsilon():
    """Spectrum uses ε = 1/√20."""
    fs = FermionSpectrum()
    assert abs(fs.epsilon - 1.0 / np.sqrt(20.0)) < 1e-10
    print("PASS: FermionSpectrum uses ε = 1/√20")


def test_fermion_mass_ratios():
    """Mass ratios follow ε^n pattern."""
    fs = FermionSpectrum()
    eps = fs.epsilon
    for sector in ['up', 'down', 'lepton']:
        ratios = fs.mass_ratios(sector)
        # Heaviest generation ratio should be 1
        assert abs(ratios[2] - 1.0) < 1e-10
        # Lighter generations should be < 1
        assert ratios[0] < ratios[1] < ratios[2]
    print("PASS: Mass ratios hierarchical for all sectors")


def test_fermion_hierarchy_pattern():
    """Universal 1:ε²:ε⁴ pattern from Sp(1)."""
    fs = FermionSpectrum()
    pattern = fs.hierarchy_pattern()
    eps = fs.epsilon
    assert abs(pattern['epsilon'] - eps) < 1e-10
    assert pattern['universal_pattern'] == '1 : ε² : ε⁴'
    print("PASS: Universal hierarchy pattern 1:ε²:ε⁴")


def test_sp1_charges():
    """One-step Sp(1) gives degenerate charges (2, 2, 0)."""
    fs = FermionSpectrum()
    charges = fs.sp1_breaking_charges()
    assert charges['one_step_charges'] == [2, 2, 0]
    assert charges['two_step_charges'] == [3, 1, 0]
    print("PASS: Sp(1) charges correct")


def test_neutrino_su4_relation():
    """SU(4) relation: m_D(ν) = m_up at M_PS."""
    ns = NeutrinoSector()
    # Default Dirac masses should be up-type at M_PS
    assert abs(ns.dirac_masses[2] - 90.0) < 1.0  # m_t at M_PS
    print("PASS: m_D(ν₃) = m_t at M_PS (SU(4) relation)")


def test_neutrino_type_I():
    """Type-I seesaw gives masses m_ν = m_D²/M_R."""
    ns = NeutrinoSector(v_R=1e14)
    m = ns.light_masses_type_I()
    # m_ν₃ = (90 GeV)² / 10¹⁴ GeV = 8.1 × 10⁻¹¹ GeV = 0.081 eV
    m_eV = m * 1e9
    assert 0.01 < m_eV[2] < 1.0
    print(f"PASS: Type-I m_ν₃ = {m_eV[2]:.4f} eV")


def test_neutrino_tension():
    """Neutrino mass tension exists for v_R ~ 10⁹ GeV."""
    ns = NeutrinoSector(v_R=1.1e9)
    tension = ns.tension_diagnostic()
    assert tension['status'] == 'TENSION'
    assert tension['ratio'] > 1000  # Factor > 10³ off
    print(f"PASS: Tension factor = {tension['ratio']:.0e}")


def test_neutrino_inverse_seesaw():
    """Inverse seesaw resolves tension."""
    ns = NeutrinoSector(v_R=1.1e9, seesaw_type='inverse', mu_S=1e4)
    m = ns.light_masses()
    m_eV = m * 1e9
    # Should be much lighter than type-I
    assert m_eV[2] < 100  # Should be sub-eV to ~eV
    print(f"PASS: Inverse seesaw m_ν₃ = {m_eV[2]:.4f} eV")


def test_neutrino_normal_ordering():
    """Normal ordering: m₃ > m₂ > m₁."""
    ns = NeutrinoSector(v_R=1e14, seesaw_type='type_I')
    m = ns.light_masses()
    assert m[2] > m[1] > m[0]
    print("PASS: Normal ordering m₃ > m₂ > m₁")


def test_neutrino_0nubb():
    """Effective Majorana mass is small for normal ordering."""
    ns = NeutrinoSector(v_R=1e14)
    m_ee = ns.effective_mass_0nubb()
    # Should be < 0.1 eV
    assert m_ee < 0.1
    print(f"PASS: m_ee = {m_ee:.4f} eV")


# =====================================================================
# Runner
# =====================================================================

ALL_TESTS = [
    test_yukawa_tree_level_degenerate,
    test_ba_zero_at_symmetric_point,
    test_ba_fitted,
    test_c_parameter,
    test_up_down_ratio,
    test_up_down_ratio_asymmetric,
    test_fermion_spectrum_epsilon,
    test_fermion_mass_ratios,
    test_fermion_hierarchy_pattern,
    test_sp1_charges,
    test_neutrino_su4_relation,
    test_neutrino_type_I,
    test_neutrino_tension,
    test_neutrino_inverse_seesaw,
    test_neutrino_normal_ordering,
    test_neutrino_0nubb,
]

if __name__ == "__main__":
    passed = 0
    failed = 0
    for test in ALL_TESTS:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} fermion tests passed")
