"""Tests for the breaking module."""

import numpy as np
from omni_toolkit.breaking import BreakingChain, BreakingStep, ModuliSpace, BranchingRule


def test_ps_chain_creation():
    """Pati-Salam chain has 3 breaking steps."""
    chain = BreakingChain.pati_salam_chain()
    assert len(chain.steps) == 3
    assert chain.initial_group == "SU(4) x SU(2)_L x SU(2)_R"
    print("PASS: PS chain has 3 steps")


def test_ps_chain_scales():
    """Scales are hierarchical: M_C > M_R > M_Z."""
    chain = BreakingChain.pati_salam_chain()
    assert chain.steps[0].scale > chain.steps[1].scale > chain.steps[2].scale
    print("PASS: M_C > M_R > M_Z")


def test_ps_chain_derivation_status():
    """Each step has correct derivation status."""
    chain = BreakingChain.pati_salam_chain()
    assert chain.steps[0].derivation_status == "DERIVED"
    assert chain.steps[1].derivation_status == "OPEN"
    assert chain.steps[2].derivation_status == "STANDARD"
    print("PASS: Derivation statuses correct")


def test_total_goldstones():
    """Total Goldstone count = 9 + 3 + 3 = 15."""
    chain = BreakingChain.pati_salam_chain()
    assert chain.total_goldstones() == 15
    print("PASS: 15 total Goldstones")


def test_instanton_action():
    """Instanton action S = 8π²/g²_PS ≈ 290."""
    chain = BreakingChain.pati_salam_chain()
    inst = chain.instanton_action(g_PS=0.52)
    assert 280 < inst['instanton_action'] < 300
    assert inst['N_eff'] == 1.0
    assert inst['pi3'] == 'Z'
    print(f"PASS: S_inst = {inst['instanton_action']:.1f}")


def test_instanton_suppression():
    """Instanton is too suppressed: exp(-S) ~ 10⁻¹²⁶."""
    chain = BreakingChain.pati_salam_chain()
    inst = chain.instanton_action(g_PS=0.52)
    assert inst['log10_exp_minus_S'] < -100
    print(f"PASS: log₁₀(exp(-S)) = {inst['log10_exp_minus_S']:.0f}")


def test_cw_no_hierarchy():
    """Coleman-Weinberg gives no hierarchy: v_R ≈ M_C."""
    chain = BreakingChain.pati_salam_chain()
    cw = chain.coleman_weinberg_hierarchy()
    assert not cw['hierarchy_generated']
    assert cw['v_R_over_M_C'] > 0.5
    print(f"PASS: CW v_R/M_C = {cw['v_R_over_M_C']:.2f} (no hierarchy)")


def test_scalar_content():
    """Scalar content includes bidoublet from V⁻ and triplets from V⁺."""
    chain = BreakingChain.pati_salam_chain()
    sc = chain.scalar_content()
    assert len(sc['from_V_minus']) == 1
    assert sc['from_V_minus'][0]['rep'] == '(1, 2, 2)_0'
    assert len(sc['composite']) == 2
    print("PASS: Scalar content correct")


def test_moduli_standard_J():
    """Standard complex structure satisfies J² = -I."""
    ms = ModuliSpace(dim=6)
    J = ms.standard_complex_structure()
    assert np.allclose(J @ J, -np.eye(6))
    print("PASS: Standard J satisfies J² = -I")


def test_moduli_random_J():
    """Random complex structure satisfies J² = -I."""
    ms = ModuliSpace(dim=6)
    np.random.seed(42)
    J = ms.random_complex_structure()
    assert np.allclose(J @ J, -np.eye(6), atol=1e-10)
    print("PASS: Random J satisfies J² = -I")


def test_moduli_ad_J_eigenvalues():
    """ad_J eigenvalues for standard J contain ±2i (CP³ modes)."""
    ms = ModuliSpace(dim=6)
    J = ms.standard_complex_structure()
    eigs = ms.ad_J_eigenvalues(J)
    # Should contain eigenvalues ±2i
    imag_parts = np.sort(np.abs(np.imag(eigs)))
    has_2i = np.any(np.abs(imag_parts - 2.0) < 0.1)
    assert has_2i, f"No ±2i eigenvalues found. Imag parts: {imag_parts}"
    print("PASS: ad_J has ±2i eigenvalues (CP³ = 3⊕3̄)")


def test_branching_rule_64():
    """Branching for (6,4): spinor dim = 2⁵ = 32."""
    br = BranchingRule(n_plus=6, n_minus=4)
    decomp = br.decompose_spinor_weights()
    assert decomp['spinor_dim'] == 32
    assert decomp['rank'] == 5
    print(f"PASS: Spin(10) spinor dim = {decomp['spinor_dim']}")


def test_branching_zero_singlets():
    """Zero singlets for (6,4) — Parthasarathy obstruction."""
    br = BranchingRule(n_plus=6, n_minus=4)
    n_singlets = br.count_singlets()
    assert n_singlets == 0
    print("PASS: Zero singlets (Parthasarathy obstruction)")


def test_branching_summary():
    """Summary includes correct branching rule."""
    br = BranchingRule(n_plus=6, n_minus=4)
    s = br.summary()
    assert s['parthasarathy'] == True
    assert s['n_singlets'] == 0
    print("PASS: Branching summary correct")


def test_breaking_chain_summary():
    """Full summary includes all information."""
    chain = BreakingChain.pati_salam_chain()
    s = chain.summary()
    assert len(s['steps']) == 3
    assert s['total_goldstones'] == 15
    print("PASS: Breaking chain summary complete")


# =====================================================================
# Runner
# =====================================================================

ALL_TESTS = [
    test_ps_chain_creation,
    test_ps_chain_scales,
    test_ps_chain_derivation_status,
    test_total_goldstones,
    test_instanton_action,
    test_instanton_suppression,
    test_cw_no_hierarchy,
    test_scalar_content,
    test_moduli_standard_J,
    test_moduli_random_J,
    test_moduli_ad_J_eigenvalues,
    test_branching_rule_64,
    test_branching_zero_singlets,
    test_branching_summary,
    test_breaking_chain_summary,
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
    print(f"\n{passed}/{passed+failed} breaking tests passed")
