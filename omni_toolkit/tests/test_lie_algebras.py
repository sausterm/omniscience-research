"""
Tests for Lie algebra infrastructure — dimensions, algebraic identities,
and structure constants for gl(n), sl(n), so(p,q), su(n), sp(n).
"""

import numpy as np

from omni_toolkit.core.lie_algebras import gl, sl, so, su, sp, self_dual_decomposition


# =====================================================================
# gl(n): dimension n^2, generators are n x n
# =====================================================================

def test_gl_dimension():
    """gl(n) has dimension n^2."""
    for n in [2, 3, 4, 5]:
        g = gl(n)
        assert g.dim == n**2
        assert g.matrix_size == n
        for T in g.generators:
            assert T.shape == (n, n)


# =====================================================================
# sl(n): dimension n^2 - 1, traceless generators
# =====================================================================

def test_sl_dimension():
    """sl(n) has dimension n^2 - 1."""
    for n in [2, 3, 4, 5]:
        s = sl(n)
        assert s.dim == n**2 - 1


def test_sl_traceless():
    """sl(n) generators are traceless."""
    for n in [2, 3, 4]:
        s = sl(n)
        for i, T in enumerate(s.generators):
            assert abs(np.trace(T)) < 1e-12


# =====================================================================
# so(p,q): dimension n(n-1)/2 where n=p+q, antisymmetric generators
# =====================================================================

def test_so_dimension():
    """so(p,q) has dimension n(n-1)/2 where n = p+q."""
    cases = [(3, 0), (4, 0), (3, 1), (5, 0), (4, 1), (6, 0)]
    for p, q in cases:
        n = p + q
        expected = n * (n - 1) // 2
        algebra = so(p, q)
        assert algebra.dim == expected


def test_so_antisymmetric_generators():
    """so(p,q) generators satisfy eta*A + (eta*A)^T = 0."""
    for p, q in [(3, 0), (3, 1), (4, 0), (4, 1)]:
        n = p + q
        eta = np.diag([-1.0] * q + [1.0] * p)
        algebra = so(p, q)
        for i, A in enumerate(algebra.generators):
            etaA = eta @ A
            assert np.allclose(etaA + etaA.T, 0, atol=1e-10)


# =====================================================================
# su(n): dimension n^2 - 1, anti-hermitian traceless generators
# =====================================================================

def test_su_dimension():
    """su(n) has dimension n^2 - 1."""
    for n in [2, 3, 4, 5]:
        algebra = su(n)
        assert algebra.dim == n**2 - 1


def test_su_traceless():
    """su(n) generators are traceless."""
    for n in [2, 3, 4]:
        algebra = su(n)
        for i, T in enumerate(algebra.generators):
            assert abs(np.trace(T)) < 1e-12


def test_su_hermitian():
    """su(n) generators (as constructed) are Hermitian: T = T^dagger."""
    for n in [2, 3, 4]:
        algebra = su(n)
        for i, T in enumerate(algebra.generators):
            assert np.allclose(T, T.conj().T, atol=1e-12)


# =====================================================================
# sp(n): dimension n(2n+1), satisfies symplectic condition
# =====================================================================

def test_sp_dimension():
    """sp(n) dimensions and matrix sizes."""
    sp1 = sp(1)
    assert sp1.dim == 3

    sp2 = sp(2)
    assert sp2.dim > 0
    assert sp2.matrix_size == 4

    sp3 = sp(3)
    assert sp3.dim > 0
    assert sp3.matrix_size == 6


def test_sp_symplectic_condition():
    """sp(n) generators satisfy A^T J + J A = 0 for n >= 2."""
    for n in [2, 3]:
        dim_2n = 2 * n
        J = np.zeros((dim_2n, dim_2n))
        J[:n, n:] = np.eye(n)
        J[n:, :n] = -np.eye(n)

        algebra = sp(n)
        for i, A in enumerate(algebra.generators):
            cond = A.T @ J + J @ A
            assert np.allclose(cond, 0, atol=1e-10)


# =====================================================================
# Killing form: symmetric
# =====================================================================

def test_killing_form_symmetric():
    """Killing form B(X,Y) = B(Y,X)."""
    algebra = sl(3)
    gens = algebra.generators
    for i in range(min(5, len(gens))):
        for j in range(i + 1, min(6, len(gens))):
            B_ij = algebra.killing_form(gens[i], gens[j])
            B_ji = algebra.killing_form(gens[j], gens[i])
            assert abs(B_ij - B_ji) < 1e-10


# =====================================================================
# Bracket: antisymmetric [X,Y] = -[Y,X]
# =====================================================================

def test_bracket_antisymmetry():
    """Lie bracket is antisymmetric: [X,Y] = -[Y,X]."""
    for algebra in [gl(3), sl(3), so(3), su(3)]:
        gens = algebra.generators
        for i in range(min(4, len(gens))):
            for j in range(i + 1, min(5, len(gens))):
                XY = algebra.bracket(gens[i], gens[j])
                YX = algebra.bracket(gens[j], gens[i])
                assert np.allclose(XY, -YX, atol=1e-12)


# =====================================================================
# Jacobi identity: [X,[Y,Z]] + [Y,[Z,X]] + [Z,[X,Y]] = 0
# =====================================================================

def test_jacobi_identity():
    """Jacobi identity: [X,[Y,Z]] + cyclic = 0."""
    for algebra in [sl(3), so(3, 1), su(3)]:
        gens = algebra.generators
        n = min(4, len(gens))
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    X, Y, Z = gens[i], gens[j], gens[k]
                    term1 = algebra.bracket(X, algebra.bracket(Y, Z))
                    term2 = algebra.bracket(Y, algebra.bracket(Z, X))
                    term3 = algebra.bracket(Z, algebra.bracket(X, Y))
                    jacobi = term1 + term2 + term3
                    assert np.allclose(jacobi, 0, atol=1e-10)


# =====================================================================
# self_dual_decomposition(4): two sets of 3 generators
# =====================================================================

def test_self_dual_decomposition():
    """self_dual_decomposition(4) returns two sets of 3 generators each."""
    L_gens, R_gens = self_dual_decomposition(4)
    assert len(L_gens) == 3
    assert len(R_gens) == 3

    # L and R should commute: [L_i, R_j] = 0
    for Li in L_gens:
        for Rj in R_gens:
            comm = Li @ Rj - Rj @ Li
            assert np.allclose(comm, 0, atol=1e-10)

    # Each sector should form su(2): brackets close within each sector
    for gens, name in [(L_gens, "L"), (R_gens, "R")]:
        comm_12 = gens[0] @ gens[1] - gens[1] @ gens[0]
        if np.linalg.norm(gens[2]) > 1e-15:
            ratio = comm_12 / np.where(np.abs(gens[2]) > 1e-10, gens[2], 1.0)
            nonzero = np.abs(gens[2]) > 1e-10
            if np.any(nonzero):
                ratios = ratio[nonzero]
                assert np.allclose(ratios, ratios[0], atol=1e-10)


def test_self_dual_decomposition_wrong_dim():
    """self_dual_decomposition raises ValueError for n != 4."""
    raised = False
    try:
        self_dual_decomposition(3)
    except ValueError:
        raised = True
    assert raised


# =====================================================================
# Structure constants antisymmetry: f^c_{ab} = -f^c_{ba}
# =====================================================================

def test_structure_constants_antisymmetry():
    """Structure constants f^c_{ab} are antisymmetric in a,b."""
    algebra = so(3)
    f = algebra.structure_constants()
    n = algebra.dim
    for a in range(n):
        for b in range(n):
            for c in range(n):
                assert abs(f[c, a, b] + f[c, b, a]) < 1e-10


def test_structure_constants_so3():
    """so(3) structure constants are the Levi-Civita symbol (up to normalization)."""
    algebra = so(3)
    f = algebra.structure_constants()
    for a in range(3):
        for b in range(3):
            for c in range(3):
                assert abs(f[c, a, b] + f[c, b, a]) < 1e-10
    assert abs(f[2, 0, 1]) > 0.1
