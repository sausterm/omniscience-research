#!/usr/bin/env python3
"""
Core tests for omni-toolkit.

Verifies the fundamental geometric computations on symmetric spaces
of various signatures and dimensions.
"""

import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from omni_toolkit.core import SymmetricSpace, DeWittMetric, RicciTensor, LieAlgebra, EigenDecomposition


def test_dewitt_2d():
    """DeWitt metric on GL+(2)/SO(2): 3D fibre."""
    eta = np.diag([1.0, 1.0])
    space = SymmetricSpace(eta)
    assert space.dim_fibre == 3, f"Expected 3, got {space.dim_fibre}"
    print(f"  PASS: d=2 Euclidean → {space.dim_fibre}D fibre, signature {space.signature}")


def test_dewitt_3d_euclidean():
    """DeWitt metric on GL+(3)/SO(3): 6D fibre."""
    eta = np.diag([1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    assert space.dim_fibre == 6
    assert space.signature[0] + space.signature[1] == 6
    print(f"  PASS: d=3 Euclidean → signature {space.signature}")


def test_dewitt_3d_lorentzian():
    """DeWitt metric on GL+(3)/SO(2,1): 6D fibre, should give (3,3)."""
    eta = np.diag([-1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    assert space.signature == (3, 3), f"Expected (3,3), got {space.signature}"
    print(f"  PASS: d=3 Lorentzian → signature {space.signature}")


def test_dewitt_4d_lorentzian():
    """DeWitt metric on GL+(4)/SO(3,1): 10D fibre, signature (6,4)."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    assert space.dim_fibre == 10
    assert space.signature == (6, 4), f"Expected (6,4), got {space.signature}"
    print(f"  PASS: d=4 Lorentzian → signature {space.signature}")


def test_dewitt_4d_euclidean():
    """DeWitt metric on GL+(4)/SO(4): 10D fibre, signature (9,1)."""
    eta = np.diag([1.0, 1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    assert space.signature == (9, 1), f"Expected (9,1), got {space.signature}"
    print(f"  PASS: d=4 Euclidean → signature {space.signature}")


def test_ricci_methods_agree():
    """Killing form and double commutator methods must agree."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    ricci = RicciTensor(space)
    assert ricci.methods_agree, "Ricci methods disagree!"
    print(f"  PASS: Ricci methods agree (max diff = {np.max(np.abs(ricci.ric_killing - ricci.ric_double_comm)):.2e})")


def test_scalar_curvature():
    """R = -30 for d=4 Lorentzian."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    ricci = RicciTensor(space)
    R = ricci.scalar_curvature
    assert abs(R - (-30.0)) < 1e-6, f"Expected -30, got {R}"
    print(f"  PASS: R = {R:.4f}")


def test_lie_bracket():
    """Lie bracket [A, B] = AB - BA."""
    A = np.array([[0, 1], [-1, 0]], dtype=float)
    B = np.array([[0, 1], [1, 0]], dtype=float)
    C = LieAlgebra.bracket(A, B)
    expected = A @ B - B @ A
    assert np.allclose(C, expected), "Bracket failed"
    print(f"  PASS: Lie bracket [A, B] correct")


def test_eigendecomposition():
    """V+/V- split gives correct dimensions."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    space = SymmetricSpace(eta)
    ed = EigenDecomposition(space)
    sub = ed.maximal_compact_subgroup()
    assert sub['n_generators'] == 21  # 15 + 3 + 3
    print(f"  PASS: Maximal compact: {sub['description']}")


def test_dewitt_inner_product():
    """Both inner product methods must agree."""
    eta = np.diag([-1.0, 1.0, 1.0])
    dw = DeWittMetric(eta)
    h = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=float)
    k = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    v1 = dw.inner_product(h, k)
    v2 = dw.inner_product_fast(h, k)
    assert abs(v1 - v2) < 1e-12, f"Methods disagree: {v1} vs {v2}"
    print(f"  PASS: Inner product methods agree ({v1:.6f})")


if __name__ == '__main__':
    print("=" * 70)
    print("OMNI-TOOLKIT CORE TESTS")
    print("=" * 70)

    tests = [
        test_dewitt_2d,
        test_dewitt_3d_euclidean,
        test_dewitt_3d_lorentzian,
        test_dewitt_4d_lorentzian,
        test_dewitt_4d_euclidean,
        test_ricci_methods_agree,
        test_scalar_curvature,
        test_lie_bracket,
        test_eigendecomposition,
        test_dewitt_inner_product,
    ]

    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")
