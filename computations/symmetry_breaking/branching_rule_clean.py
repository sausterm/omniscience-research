"""
BRANCHING RULE: Spin(9) spinor → Spin(4) via the (3,3) isotropy embedding
==========================================================================

The fiber of the metric bundle is SL(4,R)/SO(4), with tangent space
p = Sym_0^2(R^4), dimension 9. The structure group K = SO(4) acts on p
via the isotropy representation, which is the (3,3) of SU(2)_L × SU(2)_R.

This script computes the branching rule for the 16-dimensional spinor
of Spin(9) restricted to Spin(4) via this embedding.

The result tells us the representation content of fermions on the fiber.
"""

import numpy as np
from itertools import combinations

np.set_printoptions(precision=6, suppress=True, linewidth=120)

# ================================================================
# Step 1: Build Clifford algebra Cl(9) via real gamma matrices
# ================================================================

# Use the standard recursive construction.
# For Cl(2n), use 2^n × 2^n matrices.
# For Cl(2n+1), add the chirality operator of Cl(2n).

def pauli():
    """Return Pauli matrices as complex 2×2."""
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return sx, sy, sz

def build_gamma_matrices(dim):
    """Build gamma matrices for Cl(dim) using the standard recursive construction.
    Returns real/complex matrices of size 2^(dim//2)."""
    sx, sy, sz = pauli()
    I2 = np.eye(2, dtype=complex)

    if dim == 1:
        return [np.array([[1]], dtype=complex)]

    # Build Cl(2k) first, then add chirality for odd dim
    n = dim // 2  # For dim=9, n=4

    # Recursive construction for Cl(2n):
    # Start with Cl(2): gamma1 = sx, gamma2 = sy, chirality = sz
    gammas = [sx, sy]
    chiral = sz

    for k in range(1, n):
        # Extend from Cl(2k) to Cl(2k+2)
        new_size = 2**(k+1)
        new_gammas = []
        # Old gammas tensor with I2
        for g in gammas:
            new_gammas.append(np.kron(g, I2))
        # Two new gammas
        new_gammas.append(np.kron(chiral, sx))
        new_gammas.append(np.kron(chiral, sy))
        # New chirality
        chiral = np.kron(chiral, sz)
        gammas = new_gammas

    if dim % 2 == 1:
        # Add chirality as the last gamma
        gammas.append(chiral)

    return gammas

gamma = build_gamma_matrices(9)
N = gamma[0].shape[0]  # Should be 16

print(f"Clifford algebra Cl(9)")
print(f"Gamma matrix size: {N}×{N}")
print(f"Number of gamma matrices: {len(gamma)}")

# Verify Clifford relations
print("\nVerifying {γ_i, γ_j} = 2δ_ij:")
ok = True
for i in range(9):
    for j in range(i, 9):
        ac = gamma[i] @ gamma[j] + gamma[j] @ gamma[i]
        expected = 2.0 * np.eye(N) if i == j else np.zeros((N, N))
        if not np.allclose(ac, expected, atol=1e-12):
            print(f"  FAIL: i={i}, j={j}")
            ok = False
print(f"  All relations OK: {ok}")

# Verify hermiticity (gamma_i should be Hermitian for Euclidean signature)
for i in range(9):
    if not np.allclose(gamma[i], gamma[i].conj().T, atol=1e-12):
        print(f"  WARNING: γ_{i} not Hermitian")

# ================================================================
# Step 2: SO(9) generators in the spinor representation
# ================================================================

def spin_generator(i, j):
    """Spin(9) generator Σ_{ij} = (1/4i)[γ_i, γ_j] in the spinor rep.
    These are anti-Hermitian: Σ^† = -Σ."""
    return 0.25 * (gamma[i] @ gamma[j] - gamma[j] @ gamma[i])
    # Note: no factor of i here; these generate SO(9) rotations
    # as exp(θ Σ_{ij}) where Σ_{ij} is real-antisymmetric (for real gamma)
    # But our gamma are complex; Σ_{ij} is anti-Hermitian.

# Actually, for Hermitian gamma matrices:
# Σ_{ij} = (1/4)[γ_i, γ_j] = (1/2)γ_i γ_j for i≠j
# These satisfy [Σ_{ij}, Σ_{kl}] = δ_{jk}Σ_{il} - δ_{ik}Σ_{jl} - δ_{jl}Σ_{ik} + δ_{il}Σ_{jk}

# Let's use the convention: generators are ½ γ_i γ_j for i < j
# These are anti-Hermitian (since (γ_i γ_j)† = γ_j γ_i = -γ_i γ_j for i≠j)

def Sigma(i, j):
    """SO(9) generator in spinor rep: Σ_{ij} = ½ γ_i γ_j for i≠j.
    Anti-Hermitian."""
    return 0.5 * gamma[i] @ gamma[j]

# Verify anti-Hermiticity
for i in range(9):
    for j in range(i+1, 9):
        S = Sigma(i, j)
        if not np.allclose(S + S.conj().T, 0, atol=1e-12):
            print(f"  Σ_{i}{j} not anti-Hermitian!")

# ================================================================
# Step 3: Build SO(4) in the 9D isotropy representation
# ================================================================

# Basis for Sym_0^2(R^4): 9-dimensional
# Off-diagonal: (E_{ij} + E_{ji})/√2 for 0≤i<j≤3 → 6 elements
# Diagonal traceless: 3 elements

def make_sym_basis():
    """Orthonormal basis for 4×4 traceless symmetric matrices."""
    basis = []
    # Off-diagonal
    for i in range(4):
        for j in range(i+1, 4):
            B = np.zeros((4, 4))
            B[i, j] = B[j, i] = 1.0 / np.sqrt(2)
            basis.append(B)
    # Diagonal traceless (Gell-Mann-like)
    basis.append(np.diag([1, -1, 0, 0]) / np.sqrt(2))
    basis.append(np.diag([1, 1, -2, 0]) / np.sqrt(6))
    basis.append(np.diag([1, 1, 1, -3]) / np.sqrt(12))
    return basis

sym_basis = make_sym_basis()

# Verify orthonormality
for i in range(9):
    for j in range(9):
        ip = np.trace(sym_basis[i].T @ sym_basis[j])
        if abs(ip - (1 if i == j else 0)) > 1e-12:
            print(f"  Basis not orthonormal at ({i},{j}): {ip}")

# SO(4) generators in fundamental rep: L_{ab} = E_{ab} - E_{ba}
def so4_gen(a, b):
    """SO(4) generator L_{ab} in the fundamental 4D rep."""
    L = np.zeros((4, 4))
    L[a, b] = 1
    L[b, a] = -1
    return L

# All 6 generators
so4_fund = []
so4_pairs = []
for a in range(4):
    for b in range(a+1, 4):
        so4_fund.append(so4_gen(a, b))
        so4_pairs.append((a, b))

# Action on Sym_0^2: L · S = LS + SL^T = LS - SL (since L^T = -L)
def isotropy_action(L):
    """Given 4×4 SO(4) generator L, compute 9×9 matrix of its action on Sym_0^2."""
    M = np.zeros((9, 9))
    for col in range(9):
        S = sym_basis[col]
        LS = L @ S + S @ L.T  # = LS - SL since L is antisymmetric
        for row in range(9):
            M[row, col] = np.trace(sym_basis[row].T @ LS)
    return M

so4_9d = [isotropy_action(L) for L in so4_fund]

# Verify these are antisymmetric
for idx, M in enumerate(so4_9d):
    if not np.allclose(M + M.T, 0, atol=1e-12):
        print(f"  9D generator {idx} not antisymmetric!")

# ================================================================
# Step 4: Embed SO(4) generators into Spin(9) spinor rep
# ================================================================

# Each 9×9 antisymmetric matrix M can be decomposed as:
# M = Σ_{p<q} M_{pq} (E_{pq} - E_{qp})
# where M_{pq} is the (p,q) entry of M.
# The corresponding spinor generator is:
# Σ_M = Σ_{p<q} M_{pq} · Σ(p,q)

def embed_to_spinor(M9):
    """Map a 9×9 antisymmetric matrix to the 16D spinor rep."""
    result = np.zeros((N, N), dtype=complex)
    for p in range(9):
        for q in range(p+1, 9):
            result += M9[p, q] * Sigma(p, q)
    return result

so4_16d = [embed_to_spinor(M) for M in so4_9d]

# Verify anti-Hermiticity
for idx, S in enumerate(so4_16d):
    if not np.allclose(S + S.conj().T, 0, atol=1e-12):
        print(f"  16D generator {idx} not anti-Hermitian!")

# Verify so(4) commutation relations in 16D
# [L_{ab}, L_{cd}] = δ_{bc}L_{ad} - δ_{ac}L_{bd} - δ_{bd}L_{ac} + δ_{ad}L_{bc}
print("\nVerifying SO(4) algebra in 16D spinor representation:")
algebra_ok = True
for i, (a1, b1) in enumerate(so4_pairs):
    for j, (a2, b2) in enumerate(so4_pairs):
        comm = so4_16d[i] @ so4_16d[j] - so4_16d[j] @ so4_16d[i]
        # Expected: sum of generators with structure constant coefficients
        expected = np.zeros((N, N), dtype=complex)
        for k, (a3, b3) in enumerate(so4_pairs):
            # Structure constants of so(4)
            f = 0
            if b1 == a2 and (a1, b2) == (a3, b3): f += 1
            if b1 == a2 and (b2, a1) == (a3, b3): f -= 1
            if a1 == a2 and (b1, b2) == (a3, b3): f -= 1
            if a1 == a2 and (b2, b1) == (a3, b3): f += 1
            if b1 == b2 and (a2, a1) == (a3, b3): f -= 1
            if b1 == b2 and (a1, a2) == (a3, b3): f += 1
            if a1 == b2 and (a2, b1) == (a3, b3): f += 1
            if a1 == b2 and (b1, a2) == (a3, b3): f -= 1
            expected += f * so4_16d[k]
        if not np.allclose(comm, expected, atol=1e-10):
            # Try computing expected directly from 9D
            comm_9d = so4_9d[i] @ so4_9d[j] - so4_9d[j] @ so4_9d[i]
            expected2 = embed_to_spinor(comm_9d)
            if not np.allclose(comm, expected2, atol=1e-10):
                print(f"  Algebra FAILS for [{so4_pairs[i]}, {so4_pairs[j]}]")
                algebra_ok = False

# Simpler check: just verify via 9D commutators
print("  Verifying via 9D → 16D homomorphism:")
homo_ok = True
for i in range(6):
    for j in range(6):
        comm_16 = so4_16d[i] @ so4_16d[j] - so4_16d[j] @ so4_16d[i]
        comm_9 = so4_9d[i] @ so4_9d[j] - so4_9d[j] @ so4_9d[i]
        expected_16 = embed_to_spinor(comm_9)
        if not np.allclose(comm_16, expected_16, atol=1e-10):
            homo_ok = False
            print(f"    FAIL at ({i},{j})")
print(f"  Homomorphism preserved: {homo_ok}")

# ================================================================
# Step 5: Decompose into SU(2)_L × SU(2)_R
# ================================================================

print("\n" + "=" * 60)
print("DECOMPOSITION UNDER SU(2)_L × SU(2)_R")
print("=" * 60)

# Self-dual / anti-self-dual decomposition of SO(4):
# SU(2)_L generators: J_L^i = ½(L_{jk} + ½ε_{ijkl} L_{kl})
# Using the standard 't Hooft symbols:
# J_L^1 = ½(L_{23} + L_{01}), J_L^2 = ½(L_{31} + L_{02}), J_L^3 = ½(L_{12} + L_{03})
# where indices are 0,1,2,3

# Our labeling: so4_pairs = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
# Index map: L_{01}→0, L_{02}→1, L_{03}→2, L_{12}→3, L_{13}→4, L_{23}→5

idx = {(0,1):0, (0,2):1, (0,3):2, (1,2):3, (1,3):4, (2,3):5}

# Self-dual (SU(2)_L):
# η^i_{μν} ('t Hooft symbols, self-dual)
# η^1: (0,1)+(2,3), η^2: (0,2)-(1,3), η^3: (0,3)+(1,2)
JL = [
    0.5 * (so4_16d[idx[(0,1)]] + so4_16d[idx[(2,3)]]),   # J_L^1
    0.5 * (so4_16d[idx[(0,2)]] - so4_16d[idx[(1,3)]]),   # J_L^2
    0.5 * (so4_16d[idx[(0,3)]] + so4_16d[idx[(1,2)]]),   # J_L^3
]

# Anti-self-dual (SU(2)_R):
# η̄^1: (0,1)-(2,3), η̄^2: (0,2)+(1,3), η̄^3: (0,3)-(1,2)
JR = [
    0.5 * (so4_16d[idx[(0,1)]] - so4_16d[idx[(2,3)]]),   # J_R^1
    0.5 * (so4_16d[idx[(0,2)]] + so4_16d[idx[(1,3)]]),   # J_R^2
    0.5 * (so4_16d[idx[(0,3)]] - so4_16d[idx[(1,2)]]),   # J_R^3
]

# Verify SU(2)_L algebra: [J_a, J_b] = ε_{abc} J_c
# (Note: generators are anti-Hermitian, so [J_a, J_b] = ε_{abc} J_c, not iε)
print("\nSU(2)_L commutation relations:")
eps = {(0,1,2): 1, (1,2,0): 1, (2,0,1): 1,
       (1,0,2): -1, (2,1,0): -1, (0,2,1): -1}
su2L_ok = True
for (a, b, c), sign in eps.items():
    if sign != 1: continue
    comm = JL[a] @ JL[b] - JL[b] @ JL[a]
    if np.allclose(comm, JL[c], atol=1e-10):
        print(f"  [J_L^{a+1}, J_L^{b+1}] = J_L^{c+1} ✓")
    elif np.allclose(comm, -JL[c], atol=1e-10):
        print(f"  [J_L^{a+1}, J_L^{b+1}] = -J_L^{c+1} (sign convention)")
    else:
        print(f"  [J_L^{a+1}, J_L^{b+1}] ≠ ±J_L^{c+1} ✗")
        su2L_ok = False

print("\nSU(2)_R commutation relations:")
su2R_ok = True
for (a, b, c), sign in eps.items():
    if sign != 1: continue
    comm = JR[a] @ JR[b] - JR[b] @ JR[a]
    if np.allclose(comm, JR[c], atol=1e-10):
        print(f"  [J_R^{a+1}, J_R^{b+1}] = J_R^{c+1} ✓")
    elif np.allclose(comm, -JR[c], atol=1e-10):
        print(f"  [J_R^{a+1}, J_R^{b+1}] = -J_R^{c+1} (sign convention)")
    else:
        print(f"  [J_R^{a+1}, J_R^{b+1}] ≠ ±J_R^{c+1} ✗")
        su2R_ok = False

print("\n[SU(2)_L, SU(2)_R] = 0?")
cross_ok = True
for a in range(3):
    for b in range(3):
        comm = JL[a] @ JR[b] - JR[b] @ JL[a]
        if not np.allclose(comm, 0, atol=1e-10):
            cross_ok = False
            print(f"  [J_L^{a+1}, J_R^{b+1}] ≠ 0 ✗")
print(f"  All cross-commutators vanish: {cross_ok}")

# ================================================================
# Step 6: Compute Casimirs and find quantum numbers
# ================================================================

print("\n" + "=" * 60)
print("CASIMIR EIGENVALUES AND BRANCHING RULE")
print("=" * 60)

# Casimir C_L = J_L^1² + J_L^2² + J_L^3²
# Since J are anti-Hermitian, J² is negative-semidefinite
# Eigenvalues of -C_L = -(J_L^1² + J_L^2² + J_L^3²) should be j_L(j_L+1)

CL = JL[0] @ JL[0] + JL[1] @ JL[1] + JL[2] @ JL[2]
CR = JR[0] @ JR[0] + JR[1] @ JR[1] + JR[2] @ JR[2]

# -CL should have eigenvalues j(j+1) ≥ 0
neg_CL = -CL
neg_CR = -CR

# Check these are Hermitian
print(f"-C_L Hermitian? {np.allclose(neg_CL, neg_CL.conj().T, atol=1e-12)}")
print(f"-C_R Hermitian? {np.allclose(neg_CR, neg_CR.conj().T, atol=1e-12)}")

evals_L = np.sort(np.linalg.eigvalsh(neg_CL.real))
evals_R = np.sort(np.linalg.eigvalsh(neg_CR.real))

print(f"\nEigenvalues of -C_L: {np.unique(np.round(evals_L, 6))}")
print(f"Eigenvalues of -C_R: {np.unique(np.round(evals_R, 6))}")

# Diagonalize simultaneously: CL, CR, JL[2], JR[2] all commute
# Use J_L^3 and J_R^3 as Cartan generators
JL3 = JL[2]  # anti-Hermitian
JR3 = JR[2]

# The Hermitian operators are iJ_L^3 and iJ_R^3
hJL3 = 1j * JL3  # Hermitian
hJR3 = 1j * JR3

# Check commutativity
print(f"\n[C_L, C_R] = 0? {np.allclose(CL @ CR - CR @ CL, 0, atol=1e-10)}")
print(f"[C_L, J_L^3] = 0? {np.allclose(CL @ JL3 - JL3 @ CL, 0, atol=1e-10)}")
print(f"[C_R, J_R^3] = 0? {np.allclose(CR @ JR3 - JR3 @ CR, 0, atol=1e-10)}")
print(f"[J_L^3, J_R^3] = 0? {np.allclose(JL3 @ JR3 - JR3 @ JL3, 0, atol=1e-10)}")

# Simultaneously diagonalize using a combined Hermitian operator
# with non-degenerate spectrum
H_combined = 100 * neg_CL.real + 37 * neg_CR.real + 13 * hJL3.real + 7 * hJR3.real
evals_comb, evecs = np.linalg.eigh(H_combined)

print(f"\nQuantum numbers of each state in the 16-dim spinor:")
print(f"{'State':>5}  {'j_L(j_L+1)':>12}  {'j_L':>6}  {'m_L':>6}  {'j_R(j_R+1)':>12}  {'j_R':>6}  {'m_R':>6}")
print("-" * 75)

multiplets = {}
for k in range(N):
    v = evecs[:, k:k+1]  # column vector
    cl = (v.conj().T @ neg_CL @ v)[0, 0].real
    cr = (v.conj().T @ neg_CR @ v)[0, 0].real
    ml = (v.conj().T @ hJL3 @ v)[0, 0].real
    mr = (v.conj().T @ hJR3 @ v)[0, 0].real

    # Determine j from j(j+1) = c
    jl = (-1 + np.sqrt(1 + 4*cl)) / 2 if cl >= -0.01 else -1
    jr = (-1 + np.sqrt(1 + 4*cr)) / 2 if cr >= -0.01 else -1

    jl_round = round(2*jl) / 2 if jl >= 0 else -1
    jr_round = round(2*jr) / 2 if jr >= 0 else -1
    ml_round = round(2*ml) / 2
    mr_round = round(2*mr) / 2

    print(f"{k+1:>5}  {cl:>12.6f}  {jl_round:>6.1f}  {ml_round:>6.1f}  {cr:>12.6f}  {jr_round:>6.1f}  {mr_round:>6.1f}")

    key = (jl_round, jr_round)
    if key not in multiplets:
        multiplets[key] = 0
    multiplets[key] += 1

print(f"\n{'='*60}")
print("BRANCHING RULE: 16 of Spin(9) → SU(2)_L × SU(2)_R")
print(f"{'='*60}")
print(f"\n{'(j_L, j_R)':>12}  {'States':>8}  {'dim(j_L,j_R)':>14}  {'Copies':>8}")
print("-" * 50)
total = 0
for (jl, jr) in sorted(multiplets.keys()):
    count = multiplets[(jl, jr)]
    dim_rep = int((2*jl+1) * (2*jr+1))
    copies = count // dim_rep if dim_rep > 0 else 0
    remainder = count % dim_rep if dim_rep > 0 else count
    print(f"  ({jl:.1f}, {jr:.1f})    {count:>5}  {dim_rep:>12}      {copies:>5}" +
          (f" + {remainder}" if remainder else ""))
    total += count
print(f"\nTotal states: {total} (expected 16)")

# Count singlets (j_L = 0, j_R = 0)
singlets = multiplets.get((0, 0), 0)
print(f"\nSINGLETS (j_L=0, j_R=0): {singlets}")
print(f"These would be gauge-invariant zero modes → potential generations")

print(f"""
╔══════════════════════════════════════════════════════════════╗
║  INTERPRETATION                                              ║
║                                                              ║
║  The branching rule shows how the fiber spinor decomposes    ║
║  under the gauge group Spin(4) = SU(2)_L × SU(2)_R.        ║
║                                                              ║
║  Singlets (0,0) would be gauge-invariant fermion modes.      ║
║  Higher representations carry gauge quantum numbers.         ║
║                                                              ║
║  HOWEVER: as proven by Parthasarathy + Harish-Chandra,       ║
║  there are NO L² normalizable zero modes on the fiber        ║
║  SL(4,R)/SO(4) because rank(G) ≠ rank(K).                   ║
║  The branching rule gives representation CONTENT but not     ║
║  normalizable STATES.                                        ║
╚══════════════════════════════════════════════════════════════╝
""")
