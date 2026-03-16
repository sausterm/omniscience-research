"""Tests for the mixing module."""

import numpy as np
from omni_toolkit.mixing import EpsilonGeometry, VacuumAlignment, MixingMatrix


def test_epsilon_value():
    """ε = 1/√20 ≈ 0.2236 for d=4."""
    eg = EpsilonGeometry(spacetime_dim=4)
    assert abs(eg.epsilon - 1.0 / np.sqrt(20.0)) < 1e-10
    print("PASS: ε = 1/√20")


def test_epsilon_cabibbo_match():
    """ε matches sin(θ_C) to < 1%."""
    eg = EpsilonGeometry()
    assert eg.cabibbo_error_pct < 1.0
    print(f"PASS: Cabibbo error = {eg.cabibbo_error_pct:.3f}%")


def test_epsilon_fibre_dim():
    """Fibre dimension = d(d+1)/2 = 10 for d=4."""
    eg = EpsilonGeometry(spacetime_dim=4)
    assert eg.fibre_dim == 10
    print("PASS: dim_fibre = 10")


def test_epsilon_generalization():
    """ε(d) = 1/√(d(d+1)) for arbitrary d."""
    eg = EpsilonGeometry()
    for d in [2, 3, 4, 5, 6]:
        eps = eg.epsilon_for_dim(d)
        expected = 1.0 / np.sqrt(d * (d + 1))
        assert abs(eps - expected) < 1e-10
    print("PASS: ε(d) formula works for d=2..6")


def test_u3_intersection():
    """U(3) intersection structure confirms k ≈ 0.5."""
    eg = EpsilonGeometry()
    result = eg.u3_intersection_analysis()
    # Each stabilizer should have dim 9
    for dim in result['stabilizer_dims']:
        assert dim == 9, f"Expected dim(u(3)) = 9, got {dim}"
    # Intersection should have dim 4
    assert result['intersection_dim_01'] == 4
    # k should be close to 0.5
    assert abs(result['k_parameter'] - 0.5) < 0.05
    print(f"PASS: U(3) intersection dim=4, k={result['k_parameter']:.3f}")


def test_vacuum_fn_charges():
    """Sp(1) → U(1) along K gives q = (2, 2, 0)."""
    va = VacuumAlignment(breaking_direction=np.array([0, 0, 1]))
    charges = va.fn_charges_sp1()
    assert np.allclose(charges, [2, 2, 0])
    print("PASS: FN charges = (2, 2, 0) for K-breaking")


def test_vacuum_two_step():
    """Two-step breaking gives three distinct charges."""
    va = VacuumAlignment()
    charges = va.fn_charges_two_step(epsilon_2=0.5)
    # Should have three distinct values
    assert len(set(np.round(charges, 6))) == 3
    print(f"PASS: Two-step charges = {charges}")


def test_ckm_wolfenstein():
    """CKM in Wolfenstein parametrization is approximately unitary."""
    mm = MixingMatrix()
    V = mm.ckm_wolfenstein(order=3)
    # Check approximate unitarity (exact to O(λ⁴))
    VVd = V @ V.conj().T
    assert np.max(np.abs(VVd - np.eye(3))) < 0.05
    print("PASS: CKM approximately unitary")


def test_ckm_vus():
    """|V_us| ≈ ε to < 1%."""
    mm = MixingMatrix()
    V = mm.ckm_magnitudes()
    eps = mm.epsilon
    assert abs(V[0, 1] - eps) / eps < 0.01
    print(f"PASS: |V_us| = {V[0, 1]:.4f} ≈ ε = {eps:.4f}")


def test_ckm_hierarchy():
    """|V_us| > |V_cb| > |V_ub| (hierarchical structure)."""
    mm = MixingMatrix()
    V = mm.ckm_magnitudes()
    assert V[0, 1] > V[1, 2] > V[0, 2]
    print("PASS: CKM hierarchy |V_us| > |V_cb| > |V_ub|")


def test_jarlskog():
    """Jarlskog invariant is O(10⁻⁵)."""
    mm = MixingMatrix()
    J = mm.jarlskog_invariant()
    assert 1e-6 < abs(J) < 1e-4
    print(f"PASS: Jarlskog J = {J:.2e}")


def test_pmns_tribimaximal():
    """TBM matrix has sin²(θ₁₂) = 1/3, sin²(θ₂₃) = 1/2."""
    mm = MixingMatrix()
    U = mm.pmns_tribimaximal()
    s12_sq = U[0, 1]**2
    s23_sq = U[1, 2]**2
    assert abs(s12_sq - 1.0/3.0) < 0.01
    assert abs(s23_sq - 0.5) < 0.01
    print(f"PASS: TBM sin²θ₁₂ = {s12_sq:.4f}, sin²θ₂₃ = {s23_sq:.4f}")


def test_pmns_comparison():
    """PMNS predictions within ~10% of observed for large angles."""
    mm = MixingMatrix()
    comp = mm.pmns_comparison()
    assert comp['sin2_12']['error_pct'] < 15
    assert comp['sin2_23']['error_pct'] < 15
    print(f"PASS: PMNS θ₁₂ error = {comp['sin2_12']['error_pct']:.1f}%, "
          f"θ₂₃ error = {comp['sin2_23']['error_pct']:.1f}%")


def test_quark_lepton_complementarity():
    """θ₁₂^PMNS + θ_C ≈ 45°."""
    mm = MixingMatrix()
    qlc = mm.quark_lepton_complementarity()
    assert abs(qlc['sum_deg'] - 45.0) < 5.0
    print(f"PASS: QLC sum = {qlc['sum_deg']:.1f}°")


# =====================================================================
# Runner
# =====================================================================

ALL_TESTS = [
    test_epsilon_value,
    test_epsilon_cabibbo_match,
    test_epsilon_fibre_dim,
    test_epsilon_generalization,
    test_u3_intersection,
    test_vacuum_fn_charges,
    test_vacuum_two_step,
    test_ckm_wolfenstein,
    test_ckm_vus,
    test_ckm_hierarchy,
    test_jarlskog,
    test_pmns_tribimaximal,
    test_pmns_comparison,
    test_quark_lepton_complementarity,
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
    print(f"\n{passed}/{passed+failed} mixing tests passed")
