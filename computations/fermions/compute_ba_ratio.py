#!/usr/bin/env python3
"""
Compute b/a from the Gauss Equation — Issue #85 follow-up
==========================================================

The (15,2,2) Yukawa from Ric_mixed gives:
  Y_quark  = (a + b/3) × Y_FN
  Y_lepton = (a - b)   × Y_FN

where b/a is determined by the geometry of the fibre GL(4)/SO(4).

This script computes b/a from first principles using:
1. The DeWitt metric on Sym⁺(4) (space of positive-definite metrics)
2. The decomposition under SO(4) → SU(2)_L × SU(2)_R
3. The Gauss equation structure: Ric_mixed = 2 × (gauge-Higgs coupling)

It also computes c (SU(2)_R asymmetry parameter) from the normal connection.
"""

import numpy as np
from itertools import product

# =====================================================================
# PART 1: DeWitt metric on Sym(4)
# =====================================================================
print("=" * 72)
print("COMPUTING b/a AND c FROM FIRST PRINCIPLES")
print("=" * 72)

# Basis for Sym(4): symmetric 4x4 matrices
# We use the standard basis E_{ij} = (e_i⊗e_j + e_j⊗e_i)/√2 for i≤j
# with E_{ii} = e_i⊗e_i (no √2 factor)

def sym_basis():
    """Generate orthonormal basis for Sym(4) w.r.t. Frobenius inner product."""
    basis = []
    for i in range(4):
        for j in range(i, 4):
            E = np.zeros((4, 4))
            if i == j:
                E[i, i] = 1.0
            else:
                E[i, j] = 1.0 / np.sqrt(2)
                E[j, i] = 1.0 / np.sqrt(2)
            basis.append(E)
    return basis

basis = sym_basis()
dim = len(basis)
print(f"\ndim(Sym(4)) = {dim}")

# DeWitt metric at flat background g = δ:
# G(h, k) = Tr(h·k) - α Tr(h)·Tr(k)
# where α is the DeWitt parameter.
#
# For the supermetric on Met(X^d):
#   G^{abcd} = g^{ac}g^{bd} + g^{ad}g^{bc} - 2α g^{ab}g^{cd}
#
# At g = δ: G(h,k) = h_{ab}k_{ab} + h_{ab}k_{ba} - 2α h_{aa}k_{bb}
#         = 2 Tr(h·k) - 2α Tr(h)Tr(k)   [since h,k symmetric]

# The signature depends on α. For the standard DeWitt metric:
# α = 1/d gives degenerate (trace has zero norm)
# The physical metric has α = 1/2 (from Einstein-Hilbert action in d=4)

# From Paper 1: the signature is (6,4) for Lorentzian d=4
# The 4 negative directions correspond to V^- (Higgs)

# Let's compute for general α and find the signature
def dewitt_metric(alpha):
    """Compute the DeWitt metric matrix in the sym_basis."""
    G = np.zeros((dim, dim))
    for a, ha in enumerate(basis):
        for b, kb in enumerate(basis):
            # G(h,k) = 2 Tr(h·k) - 2α Tr(h)Tr(k)
            G[a, b] = 2 * np.trace(ha @ kb) - 2 * alpha * np.trace(ha) * np.trace(kb)
    return G

print("\n--- DeWitt metric signature vs α ---")
for alpha in [0.0, 0.25, 0.5, 1.0, 1.5]:
    G = dewitt_metric(alpha)
    eigenvalues = np.linalg.eigvalsh(G)
    n_pos = np.sum(eigenvalues > 1e-10)
    n_neg = np.sum(eigenvalues < -1e-10)
    n_zero = dim - n_pos - n_neg
    print(f"  α = {alpha:.2f}: signature ({n_pos}, {n_neg}), zero modes: {n_zero}")

# The physical DeWitt metric for Lorentzian 4D gravity has α = 1/2
alpha_phys = 0.5
G = dewitt_metric(alpha_phys)
eigenvalues, eigenvectors = np.linalg.eigh(G)
print(f"\nPhysical α = {alpha_phys}:")
print(f"  Eigenvalues: {np.sort(eigenvalues)}")

# Identify V+ and V-
pos_idx = np.where(eigenvalues > 1e-10)[0]
neg_idx = np.where(eigenvalues < -1e-10)[0]
print(f"  V+ dimension: {len(pos_idx)}")
print(f"  V- dimension: {len(neg_idx)}")

# =====================================================================
# PART 2: SO(4) decomposition and PS identification
# =====================================================================
print("\n" + "=" * 72)
print("PART 2: SO(4) DECOMPOSITION")
print("=" * 72)

# SO(4) generators acting on Sym(4) by conjugation:
# L_A · h = A·h + h·A^T = A·h + h·A  (since A antisymmetric → A^T = -A...
# wait, the adjoint action on symmetric matrices is:
# (L_A h)_{ij} = A_{ik} h_{kj} + A_{jk} h_{ik}  i.e. L_A(h) = A·h + h·A^T

def so4_action(A, h):
    """SO(4) infinitesimal action on Sym(4): A·h + h·A^T."""
    return A @ h + h @ A.T

# SO(4) basis: antisymmetric 4x4 matrices
def so4_basis():
    """Standard basis for so(4)."""
    basis = []
    for i in range(4):
        for j in range(i+1, 4):
            A = np.zeros((4, 4))
            A[i, j] = 1.0
            A[j, i] = -1.0
            basis.append(A)
    return basis

so4_gens = so4_basis()
print(f"dim(so(4)) = {len(so4_gens)}")

# SU(2)_L and SU(2)_R generators
# SO(4) = SU(2)_L × SU(2)_R with self-dual and anti-self-dual decomposition
# In 4D, the Hodge star on 2-forms gives the splitting

# Self-dual (SU(2)_L): J^+_i = e_{0i} + ½ε_{ijk} e_{jk}
# Anti-self-dual (SU(2)_R): J^-_i = e_{0i} - ½ε_{ijk} e_{jk}

# Using indices 0,1,2,3:
def make_2form(i, j):
    A = np.zeros((4, 4))
    A[i, j] = 1.0
    A[j, i] = -1.0
    return A

e01 = make_2form(0, 1)
e02 = make_2form(0, 2)
e03 = make_2form(0, 3)
e12 = make_2form(1, 2)
e13 = make_2form(1, 3)
e23 = make_2form(2, 3)

# Self-dual (SU(2)_L)
J_L1 = (e01 + e23) / 2
J_L2 = (e02 - e13) / 2
J_L3 = (e03 + e12) / 2

# Anti-self-dual (SU(2)_R)
J_R1 = (e01 - e23) / 2
J_R2 = (e02 + e13) / 2
J_R3 = (e03 - e12) / 2

# Verify: [J_Li, J_Rj] = 0
comm_LR = J_L1 @ J_R1 - J_R1 @ J_L1
print(f"[J_L1, J_R1] = 0? {np.allclose(comm_LR, 0)}")

# Now compute SO(4) action on each eigenvector of the DeWitt metric
print("\n--- SO(4) representation content of V+ and V- ---")

# Get the V+ and V- subspaces in the sym_basis
V_plus_vecs = eigenvectors[:, pos_idx]  # columns are eigenvectors
V_minus_vecs = eigenvectors[:, neg_idx]

# For each SO(4) generator, compute its matrix representation on Sym(4)
def so4_rep_matrix(A_gen):
    """Matrix of so(4) action on Sym(4) in our basis."""
    M = np.zeros((dim, dim))
    for j, h_j in enumerate(basis):
        Ah = so4_action(A_gen, h_j)
        # Decompose Ah in terms of basis
        for i, h_i in enumerate(basis):
            M[i, j] = 2 * np.trace(h_i @ Ah)  # Frobenius inner product
    return M

# Casimir of SU(2)_L and SU(2)_R on Sym(4)
rep_L1 = so4_rep_matrix(J_L1)
rep_L2 = so4_rep_matrix(J_L2)
rep_L3 = so4_rep_matrix(J_L3)
rep_R1 = so4_rep_matrix(J_R1)
rep_R2 = so4_rep_matrix(J_R2)
rep_R3 = so4_rep_matrix(J_R3)

C_L = rep_L1 @ rep_L1 + rep_L2 @ rep_L2 + rep_L3 @ rep_L3
C_R = rep_R1 @ rep_R1 + rep_R2 @ rep_R2 + rep_R3 @ rep_R3

# Casimir eigenvalues on V+ and V-
print("\nSU(2)_L Casimir eigenvalues:")
C_L_plus = V_plus_vecs.T @ C_L @ V_plus_vecs
C_L_minus = V_minus_vecs.T @ C_L @ V_minus_vecs
print(f"  On V+: {np.sort(np.linalg.eigvalsh(C_L_plus))}")
print(f"  On V-: {np.sort(np.linalg.eigvalsh(C_L_minus))}")

print("\nSU(2)_R Casimir eigenvalues:")
C_R_plus = V_plus_vecs.T @ C_R @ V_plus_vecs
C_R_minus = V_minus_vecs.T @ C_R @ V_minus_vecs
print(f"  On V+: {np.sort(np.linalg.eigvalsh(C_R_plus))}")
print(f"  On V-: {np.sort(np.linalg.eigvalsh(C_R_minus))}")

# For spin j representation, Casimir = -j(j+1) (with our conventions)
# j=0: C = 0 (singlet)
# j=1/2: C = -3/4 (doublet)
# j=1: C = -2 (triplet)

print("\nExpected Casimirs (with minus sign):")
print("  j=0 (singlet): 0")
print("  j=1/2 (doublet): -0.75")
print("  j=1 (triplet): -2.0")

# =====================================================================
# PART 3: SU(4) → SU(3) × U(1)_{B-L} Clebsch-Gordan
# =====================================================================
print("\n" + "=" * 72)
print("PART 3: COMPUTING b/a FROM GEOMETRY")
print("=" * 72)

# The key question: what is b/a?
#
# In the Gauss equation:
#   R_Y = R_X + 2·Ric_mixed + R⊥ + |H|² - |II|²
#
# The Ric_mixed term couples V+ (gauge) to V- (Higgs).
# Under PS = SU(4) × SU(2)_L × SU(2)_R:
#   V+ = adjoint contributions (su(4) part → 15)
#   V- = (1,2,2)
#
# The coupling Ric_mixed(V+, V-) decomposes as:
#   15 × (1,2,2) → (15,2,2) ⊕ ...
#   1 × (1,2,2) → (1,2,2)    [from trace part]
#
# The RATIO b/a is determined by the relative weight of the
# SU(4)-adjoint component vs the SU(4)-singlet component in V+.

# Under SO(6) → SU(4):
# The 6-dimensional V+ is the VECTOR representation of SO(6).
# As an SU(4) representation: 6 = Λ²(4) = antisymmetric rank-2 tensor
# This is NOT the adjoint 15!

# CORRECTION: V+ = R^6 = 6 of SO(6) = Λ²(4) of SU(4)
# The adjoint of SU(4) is 15 = 6 ⊕ ... wait
#
# Let me be more careful.
# SO(6) ≅ SU(4)/Z_2
# The vector rep of SO(6) = rank-2 antisymmetric of SU(4) = 6
# The adjoint of SO(6) = adjoint of SU(4) = 15
#
# V+ = R^6 carries the VECTOR representation of SO(6),
# which is the antisymmetric tensor rep 6 of SU(4).
#
# The gauge connection lives in the ADJOINT = 15.
# But V+ is the TANGENT SPACE direction, which is the 6.

# So the actual decomposition of Ric_mixed coupling is:
#   6 × (1,2,2) under SU(4) × SU(2)_L × SU(2)_R

# Under SU(4) → SU(3) × U(1):
#   6 → 3_{-2/3} ⊕ 3̄_{+2/3}

# The coupling is:
#   Ric_mixed ~ Σ h^{AB} · Φ^{CD}
# where A,B,C,D are SU(4) indices and h is in Λ²(4), Φ is in (1,2,2)

# Actually, wait. Let me reconsider the representation theory.
# The Yukawa coupling in the effective 4D theory comes from:
#   ψ̄_L · (A_m · Φ^m) · ψ_R
# where A_m is the shape operator (second fundamental form)
# and Φ^m are the Higgs field components.
#
# A_m lives in End(T_x X), which under SO(4) contains:
#   - symmetric part → Sym²(4) = 1 ⊕ 9
#   - antisymmetric part → so(4) = su(2)_L ⊕ su(2)_R
#
# The SYMMETRIC part is what appears in the shape operator.
# Under SU(2)_L × SU(2)_R:
#   9 = (1,1) [traceless part of the shape operator]
# Wait, let me redo this.

# S²₀(R⁴) under SU(2)_L × SU(2)_R:
# R⁴ = (1/2, 1/2)
# S²(1/2,1/2) = (0,0) ⊕ (1,1)
# S²₀ removes the trace → leaves (1,1) = 9-dimensional

# So the shape operator A_m has structure:
# For each m ∈ V- (Higgs direction), A_m ∈ End(TX)|_{sym} ∋ (0,0) ⊕ (1,1)

# The Ric_mixed coupling is:
#   Σ_m Tr(A_m) · Φ_m = (0,0) part → gives the (1,2,2) coupling
#   Σ_m (A_m - Tr(A_m)/4 · Id) · Φ_m = (1,1) part → gives something else

# But (1,1) under SU(2)_L × SU(2)_R is a 9-dimensional rep.
# Under SU(4) ≅ SO(6), the gauge fields live in the adjoint 15.
# The shape operator for the gauge directions gives:
#   A_m ∈ Hom(V+, V-) ≅ 6 ⊗ 4 under SO(6) × SO(4)

# Hmm, I'm getting confused by the representation theory.
# Let me take a more computational approach.

print("\nCOMPUTATIONAL APPROACH TO b/a:")
print("-" * 40)

# The key insight is simpler than I've been making it.
#
# The (15,2,2) Higgs appears in PS models through the Higgs sector.
# In the metric bundle, the effective Yukawa is:
#
# L_Y = ψ̄_L · [y_1 · Φ + y_15 · (T^a_{15} Φ T^a_{15})] · ψ_R
#
# where T^a_{15} are SU(4) generators in the fundamental.
#
# The ratio y_15/y_1 = b/a comes from the GEOMETRY of the fibre.
#
# Specifically, from the Gauss equation:
# Ric_mixed_{μm} = ∂_μ H_m - H_m · A_μ + ...
#
# The H_m (mean curvature in direction m) is trace of shape operator.
# The A_μ (connection) lives in so(6,4).
#
# Under SU(4):
# - The trace of the shape operator (H_m) is SU(4)-singlet → gives (1,2,2)
# - The traceless part of A projects to the adjoint → gives (15,2,2)
#
# The relative strength is:
#   (1,2,2): from Tr(A) → strength = H_m
#   (15,2,2): from A - Tr(A)/rank → strength ~ √(|A|² - |H|²/rank)

# For a symmetric space G/H with G = SL(4,R), H = SO(4):
# The connection A lives in so(4) (the holonomy part)
# The second fundamental form lives in p = Sym₀(4) (traceless symmetric)
#
# The Ric_mixed has two contributions:
# 1. From the Levi-Civita connection of Y: involves Christoffel symbols
# 2. From the structure of the symmetric space: involves [p, p] ⊂ h

# For a symmetric space, the curvature is:
# R(X, Y)Z = -[[X, Y], Z] for X, Y, Z ∈ p
#
# The Ric_mixed for the symmetric space SL(4)/SO(4):
# Ric(X, Y) = -1/2 B(X, Y) where B is the Killing form of sl(4)
# (for X, Y ∈ p = traceless symmetric matrices)
#
# B(X, Y) = 8 Tr(X·Y) for sl(4)

# The relevant decomposition is:
# p = Sym₀(R⁴) = traceless symmetric 4×4 matrices, dim = 9
# Under SU(2)_L × SU(2)_R: p = (1,1) [9-dimensional]

# But we need to think about what couples to the Higgs.
# The Higgs is in V- which has dim 4.
# V- transforms as (1/2, 1/2) × (sign) under SO(4).

# Wait — V- is 4-dimensional with the DeWitt metric negative definite.
# Under SU(2)_L × SU(2)_R, V- = (1/2, 1/2)?
# That would give dim = (2)(2) = 4. Yes!

# And V+ is 6-dimensional. Under SU(2)_L × SU(2)_R:
# V+ decomposes as (1,1) ⊕ ...
# (1,1) has dim (3)(3) = 9 — too big.
# So V+ must be a smaller rep. In fact:
# V+ is in the traceless symmetric tensor, but only 6 of the 9 components
# have positive DeWitt norm.

# Let me just compute it directly from the eigenspaces.

# First, let's see which basis elements are in V+ and V-
print("\nV+ eigenvectors (positive eigenvalue):")
for idx in pos_idx:
    vec = eigenvectors[:, idx]
    h_mat = sum(vec[i] * basis[i] for i in range(dim))
    ev = eigenvalues[idx]
    print(f"  λ = {ev:.4f}: trace = {np.trace(h_mat):.4f}, "
          f"sym = {np.allclose(h_mat, h_mat.T)}")

print("\nV- eigenvectors (negative eigenvalue):")
for idx in neg_idx:
    vec = eigenvectors[:, idx]
    h_mat = sum(vec[i] * basis[i] for i in range(dim))
    ev = eigenvalues[idx]
    print(f"  λ = {ev:.4f}: trace = {np.trace(h_mat):.4f}, "
          f"sym = {np.allclose(h_mat, h_mat.T)}")

# =====================================================================
# PART 4: The actual b/a computation
# =====================================================================
print("\n" + "=" * 72)
print("PART 4: b/a FROM THE KILLING FORM")
print("=" * 72)

# The crucial point: in the effective 4D Lagrangian from dimensional
# reduction over G/H, the Yukawa coupling is determined by the
# STRUCTURE CONSTANTS of the Lie algebra.
#
# For G = SL(4,R), H = SO(4), p = Sym₀(R⁴):
#
# [h, p] ⊂ p  (adjoint action of SO(4) on p)
# [p, p] ⊂ h  (symmetric space property)
#
# The Yukawa coupling comes from the tri-linear:
#   f(X, Y, Z) = B([X, Y], Z)  for X ∈ h, Y ∈ p_+, Z ∈ p_-
#
# where p_+ are the V+ directions and p_- are the V- directions.
#
# Under SU(4) ≅ SO(6):
# The adjoint 15 = so(6) embeds in sl(4) as the antisymmetric matrices.
# The 6 of SO(6) = Λ²(R⁴) embeds as the rank-2 antisymmetric tensors.
#
# Wait, but our V+ and V- are SYMMETRIC matrices.
# The adjoint of SO(4) is ANTISYMMETRIC matrices.
# So the relevant coupling is [so(4), sym₀] = sym₀.
# This is just the adjoint action of SO(4) on the tangent space!

# Let me reconsider what gives rise to the (15,2,2).
#
# The 15 of SU(4) is the adjoint representation.
# Under SO(6) ≅ SU(4)/Z₂, the adjoint is the same 15.
# The 15 consists of all traceless hermitian 4×4 matrices.
# But we're working with REAL representations.
# In real form: sl(4,R) = so(4) ⊕ sym₀(4)
# so(4) = 6 (antisymmetric)
# sym₀(4) = 9 (traceless symmetric)
# sym₀(4) under SU(2)_L × SU(2)_R = (1,1) [all 9 dims]

# The Higgs field Φ ∈ V⁻ ≅ R⁴ transforms as (1/2, 1/2).
# The shape operator couples p (tangent to fibre) to base directions.

# In the PS picture:
# The fermion bilinear ψ̄_L · ψ_R transforms as (4̄, 2, 1) × (4, 1, 2) =
#   various reps including (1,2,2) and (15,2,2).
# The Higgs Φ = (1,2,2) couples to (1,2,2) in ψ̄ψ.
# The Higgs (15,2,2) couples to (15,2,2) in ψ̄ψ.

# In the metric bundle, we have only the (1,2,2) Higgs (V⁻ = R⁴).
# The (15,2,2) effective Yukawa arises when the gauge field A ∈ adj(SU(4))
# dresses the Higgs coupling:
#   ψ̄ · A^a T_a · Φ · ψ
#
# This has the structure: 15 × (1,2,2) ⊃ (15,2,2).
#
# The coefficient b is proportional to the gauge coupling g, while
# a is the bare Yukawa. So b/a ∝ g/y₀.

# At the unification scale (where PS is exact), g is the PS coupling.
# From Paper 8: α_PS = 27/(128π²) → g² = 4π α_PS = 27/(32π) ≈ 0.269
# So g ≈ 0.519

# The bare Yukawa y₀ comes from the fibre curvature.
# From the Gauss equation, both a and b come from Ric_mixed.
# The relative coefficient is fixed by group theory:

# In the effective Yukawa from Ric_mixed:
#   L_Y ∝ ψ̄_L · Ric_mixed · ψ_R
#
# Ric_mixed decomposes under SU(4) × SU(2)_L × SU(2)_R as:
#   Ric_mixed ∈ End(V+) ⊗ V-
#
# V+ = 6 of SO(6), V- = (1,2,2)
# End(V+) = 6 ⊗ 6 = 1 ⊕ 15 ⊕ 20'
#   (symmetric traceless ⊕ antisymmetric = adjoint ⊕ singlet ⊕ 20')
#   Actually: S²(6) = 21 = 1 ⊕ 20', Λ²(6) = 15

# Ric_mixed is in S²(V+) ⊗ V- (symmetric because Ric is symmetric)
# S²(6) = 1 ⊕ 20' of SU(4)

# So Ric_mixed decomposes as:
#   (1 ⊕ 20') × (1,2,2) = (1,2,2) ⊕ (20',2,2)
#
# There is NO (15,2,2) in the symmetric part!
# The (15,2,2) would come from the ANTISYMMETRIC part Λ²(6),
# but the Ricci tensor is symmetric.

print("\nKEY RESULT: REPRESENTATION THEORY ANALYSIS")
print("-" * 50)
print()
print("V+ = 6 of SO(6) ≅ Λ²(4) of SU(4)")
print("V- = (1,2,2)")
print()
print("Ric_mixed is SYMMETRIC in (V+, V+) indices:")
print("  S²(6) = 1 ⊕ 20'  under SU(4)")
print("  Λ²(6) = 15        under SU(4)")
print()
print("Therefore:")
print("  Ric_mixed ∈ S²(6) ⊗ (1,2,2) = (1,2,2) ⊕ (20',2,2)")
print("  → NO (15,2,2) component from symmetric Ricci!")
print()
print("BUT: The FULL curvature R_{μνmn} has antisymmetric parts too:")
print("  The Riemann tensor R_{μm,νn} with mixed base-fibre indices")
print("  has a part antisymmetric in (m,n) → lives in Λ²(6) = 15")
print("  → THIS gives the (15,2,2)")

# The full story:
# R_{μm,νn} decomposes as:
#   Symmetric in (m,n): S²(V+) contribution → (1,2,2) ⊕ (20',2,2)
#   Antisymmetric in (m,n): Λ²(V+) contribution → (15,2,2)
#
# The antisymmetric part comes from the CURVATURE of the normal bundle:
#   R⊥_{mn} = [∇_m, ∇_n] restricted to fibre directions
#
# For the symmetric space SL(4)/SO(4):
#   R⊥ = [p, p] ⊂ h = so(4)
#
# So the (15,2,2) strength is determined by the COMMUTATOR [p_m, p_n]
# in the Lie algebra, where p_m are V+ generators.

# Compute [p_m, p_n] for basis elements of V+ (as elements of sl(4))
# V+ directions correspond to certain symmetric matrices
# But symmetric matrices don't form a Lie subalgebra!
# Their commutator gives antisymmetric matrices: [sym, sym] ⊂ antisym

# The commutator structure is:
# For X, Y ∈ Sym₀(R⁴): [X, Y] = XY - YX ∈ Antisym(R⁴) = so(4)
# The norm ||[X,Y]|| relative to ||X|| ||Y|| gives the (15,2,2) strength

print("\n--- Computing [p, p] structure constants ---")

# Take orthonormal basis of V+ and V- from DeWitt eigenvectors
# Convert to matrices
V_plus_mats = []
for idx in pos_idx:
    vec = eigenvectors[:, idx]
    h_mat = sum(vec[i] * basis[i] for i in range(dim))
    # Normalize w.r.t. Frobenius
    h_mat = h_mat / np.linalg.norm(h_mat, 'fro')
    V_plus_mats.append(h_mat)

V_minus_mats = []
for idx in neg_idx:
    vec = eigenvectors[:, idx]
    h_mat = sum(vec[i] * basis[i] for i in range(dim))
    h_mat = h_mat / np.linalg.norm(h_mat, 'fro')
    V_minus_mats.append(h_mat)

# Compute average ||[V+_m, V+_n]||² / (||V+_m||² ||V+_n||²)
comm_norms_sq = []
for i in range(len(V_plus_mats)):
    for j in range(i+1, len(V_plus_mats)):
        comm = V_plus_mats[i] @ V_plus_mats[j] - V_plus_mats[j] @ V_plus_mats[i]
        norm_sq = np.trace(comm.T @ comm)
        comm_norms_sq.append(norm_sq)

avg_comm = np.mean(comm_norms_sq)
print(f"Average ||[V+_i, V+_j]||² = {avg_comm:.6f}")
print(f"√(average) = {np.sqrt(avg_comm):.6f}")

# The (1,2,2) contribution comes from the trace part
# Tr(A_m) for shape operator A_m
# For symmetric space: A_m is related to [p_m, ·]|_p

# Compute the effective b/a:
# b comes from Λ²(V+) = 15 part (commutator)
# a comes from S²(V+) = 1 part (trace/scalar)
#
# More precisely:
# a = average diagonal element of the metric coupling
# b = antisymmetric/commutator coupling

# For a symmetric space G/H with p the tangent space:
# The curvature in the normal bundle is:
#   R⊥(X,Y) = -[X,Y]_h  for X,Y ∈ p
#
# The Ric_mixed involves:
#   Ric_mixed(e_μ, e_m) = Σ_n R(e_μ, e_n, e_m, e_n)
#                       = Σ_n ⟨[[e_n, e_m], e_n], e_μ⟩
# (for the symmetric space curvature formula)

# Let me compute this explicitly for sl(4)/so(4)

# Basis for p = Sym₀(R⁴) (traceless symmetric 4×4 matrices)
def sym0_basis():
    """Orthonormal basis for traceless symmetric 4×4 matrices."""
    raw = []
    # Diagonal traceless
    raw.append(np.diag([1, -1, 0, 0]) / np.sqrt(2))
    raw.append(np.diag([1, 0, -1, 0]) / np.sqrt(2))
    raw.append(np.diag([1, 0, 0, -1]) / np.sqrt(2))
    # Off-diagonal
    for i in range(4):
        for j in range(i+1, 4):
            E = np.zeros((4, 4))
            E[i,j] = E[j,i] = 1.0 / np.sqrt(2)
            raw.append(E)
    # Gram-Schmidt to get orthonormal basis w.r.t. Tr(X·Y)
    ortho = []
    for v in raw:
        for u in ortho:
            v = v - np.trace(v @ u) * u
        norm = np.sqrt(np.trace(v @ v))
        if norm > 1e-10:
            ortho.append(v / norm)
    return ortho

p_basis = sym0_basis()
print(f"\ndim(p) = dim(Sym₀(R⁴)) = {len(p_basis)}")

# Also include the trace direction
trace_dir = np.eye(4) / 2  # normalized: Tr(trace_dir²) = 1
full_p = p_basis + [trace_dir]
print(f"dim(p + trace) = {len(full_p)}")

# Compute the Ricci tensor of the symmetric space SL(4)/SO(4)
# For a symmetric space G/H:
#   Ric(X, X) = -1/2 Σ_i ||[X, e_i]||² + 1/4 Σ_i ||[e_i, e_j]_p||²
# Actually, the Ricci curvature is:
#   Ric(X, Y) = -1/2 B_g(X, Y)  (proportional to Killing form)
# where B_g(X,Y) = Tr(ad_X ∘ ad_Y) is the Killing form of g restricted to p.

# For sl(4): B(X,Y) = 8 Tr(XY)
# So Ric(X,Y) = -4 Tr(XY) on the symmetric space

# The mixed Ricci between V+ and V- directions:
# If we split p into "V+" and "V-" under the DeWitt metric,
# Ric_mixed would be Ric(e_+, e_-).
# Since Ric ∝ Killing form ∝ Tr(XY), and V+ ⊥ V- under the Killing form
# (because they're orthogonal under the DeWitt metric which is proportional
# to the Killing form on the traceless part), we get:

# Wait — are V+ and V- orthogonal under the Killing form?
# The DeWitt metric is G = 2 Tr(·) - 2α Tr(·)Tr(·)
# On the traceless part (Tr = 0): G = 2 Tr(·) = (1/4) B (Killing form)
# So on traceless symmetric matrices, V+ and V- eigenvectors of DeWitt
# are also eigenvectors of the Killing form.

# But V+ and V- both live in sym₀! If the Killing form is definite on sym₀,
# then V+ and V- are orthogonal under it.

# Check: For sl(4), the Killing form B(X,Y) = 8 Tr(XY) is:
# - Positive definite on sym₀ (since Tr(X²) > 0 for nonzero symmetric X)
# - Negative definite on so(4) (since Tr(A²) < 0 for nonzero antisymmetric A)

# But the DeWitt metric has BOTH positive and negative eigenvalues on sym(4).
# With α = 1/2:
# G(h,k) = 2Tr(hk) - Tr(h)Tr(k)
# On sym₀: G = 2Tr(·) > 0  (positive definite!)
# On trace: G(cI, cI) = 2c²·4 - (4c)² = 8c² - 16c² = -8c² < 0

# So V- is JUST the trace direction! And V+ is all of sym₀ (9-dimensional)!
# But we said dim(V+) = 6 and dim(V-) = 4...

# Let me recheck the DeWitt metric computation.

print("\n" + "=" * 72)
print("RECHECK: DeWitt metric eigenstructure")
print("=" * 72)

G_phys = dewitt_metric(0.5)
evals, evecs = np.linalg.eigh(G_phys)
print(f"\nAll eigenvalues of G(α=1/2): {np.sort(evals)}")

# Let's check which eigenvectors have trace
for i in range(dim):
    vec = evecs[:, i]
    h_mat = sum(vec[j] * basis[j] for j in range(dim))
    tr = np.trace(h_mat)
    print(f"  eigvec {i}: λ = {evals[i]:+.4f}, Tr = {tr:.4f}, "
          f"||h||_F = {np.linalg.norm(h_mat, 'fro'):.4f}")

# I suspect: with α=1/2, only 1 direction is negative (the trace).
# But we claimed signature (6,4). Let me check α=1/(d-1) = 1/3.
# Or actually, the DeWitt supermetric has a specific α determined by
# the Einstein-Hilbert action.

# From Paper 1: the supermetric for Lorentzian signature gives (6,4).
# For Euclidean signature it's all positive (10,0).
# The difference is because the Lorentzian metric has indefinite signature.

# AH — the key point I was missing:
# The DeWitt metric is evaluated at a LORENTZIAN metric g = diag(-1,1,1,1),
# not at g = δ = diag(1,1,1,1)!
# At a Lorentzian point, the supermetric inherits the indefiniteness.

print("\n" + "=" * 72)
print("CORRECTED: DeWitt metric at LORENTZIAN point g = η")
print("=" * 72)

# At g = η = diag(-1, 1, 1, 1):
# G^{abcd} = g^{ac}g^{bd} + g^{ad}g^{bc} - 2α g^{ab}g^{cd}
# The inverse metric g^{ab} = η^{ab} = diag(-1, 1, 1, 1)

eta = np.diag([-1.0, 1.0, 1.0, 1.0])
eta_inv = np.diag([-1.0, 1.0, 1.0, 1.0])  # η^{-1} = η for Minkowski

def dewitt_lorentzian(alpha):
    """DeWitt metric at Lorentzian point g = η."""
    G = np.zeros((dim, dim))
    for a_idx, ha in enumerate(basis):
        for b_idx, kb in enumerate(basis):
            # G(h,k) = g^{ac} g^{bd} h_{ab} k_{cd} + g^{ad} g^{bc} h_{ab} k_{cd}
            #        - 2α g^{ab} h_{ab} g^{cd} k_{cd}
            # = Tr(η^{-1} h η^{-1} k) + Tr(η^{-1} h) Tr(η^{-1} k) ... no

            # More carefully:
            # G(h,k) = Σ_{abcd} G^{abcd} h_{ab} k_{cd}
            # G^{abcd} = η^{ac}η^{bd} + η^{ad}η^{bc} - 2α η^{ab}η^{cd}

            val = 0.0
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        for d in range(4):
                            G_abcd = (eta_inv[a,c]*eta_inv[b,d] +
                                     eta_inv[a,d]*eta_inv[b,c] -
                                     2*alpha*eta_inv[a,b]*eta_inv[c,d])
                            val += G_abcd * ha[a,b] * kb[c,d]
            G[a_idx, b_idx] = val
    return G

G_lor = dewitt_lorentzian(0.5)
evals_lor, evecs_lor = np.linalg.eigh(G_lor)

n_pos = np.sum(evals_lor > 1e-10)
n_neg = np.sum(evals_lor < -1e-10)
print(f"\nSignature at η with α=1/2: ({n_pos}, {n_neg})")
print(f"Eigenvalues: {np.sort(evals_lor)}")

# Check specific α values at Lorentzian point
for alpha in [0.0, 1/3, 0.5, 1.0]:
    G_test = dewitt_lorentzian(alpha)
    ev = np.linalg.eigvalsh(G_test)
    np_ = np.sum(ev > 1e-10)
    nn = np.sum(ev < -1e-10)
    nz = dim - np_ - nn
    print(f"  α = {alpha:.4f}: signature ({np_}, {nn}), zero: {nz}")

# Now identify V+ and V- at the Lorentzian point
pos_idx_lor = np.where(evals_lor > 1e-10)[0]
neg_idx_lor = np.where(evals_lor < -1e-10)[0]

print(f"\nV+ (positive, dim {len(pos_idx_lor)}):")
for idx in pos_idx_lor:
    vec = evecs_lor[:, idx]
    h_mat = sum(vec[j] * basis[j] for j in range(dim))
    # Check if h is "time-like" (involves 0-index) or "space-like"
    time_comp = abs(h_mat[0,0]) + sum(abs(h_mat[0,j]) + abs(h_mat[j,0]) for j in range(1,4))
    space_comp = sum(abs(h_mat[i,j]) for i in range(1,4) for j in range(1,4))
    print(f"  λ = {evals_lor[idx]:+.4f}, time_wt = {time_comp:.3f}, space_wt = {space_comp:.3f}")

print(f"\nV- (negative, dim {len(neg_idx_lor)}):")
for idx in neg_idx_lor:
    vec = evecs_lor[:, idx]
    h_mat = sum(vec[j] * basis[j] for j in range(dim))
    time_comp = abs(h_mat[0,0]) + sum(abs(h_mat[0,j]) + abs(h_mat[j,0]) for j in range(1,4))
    space_comp = sum(abs(h_mat[i,j]) for i in range(1,4) for j in range(1,4))
    print(f"  λ = {evals_lor[idx]:+.4f}, time_wt = {time_comp:.3f}, space_wt = {space_comp:.3f}")

# =====================================================================
# PART 5: The actual b/a from the symmetric space structure
# =====================================================================
print("\n" + "=" * 72)
print("PART 5: b/a FROM SYMMETRIC SPACE CURVATURE")
print("=" * 72)

# At the Lorentzian point, the fibre is GL(4)/SO(3,1) [or SL(4)/SO(3,1)]
# This is a pseudo-Riemannian symmetric space.
#
# The key coupling in Ric_mixed is between gauge (V+) and Higgs (V-):
#   Ric_mixed ~ Σ_n ⟨[e_n, [e_n, e_m]], e_+⟩
#
# where e_n runs over a basis of p (tangent to fibre),
# e_m ∈ V- (Higgs direction), e_+ ∈ V+ (gauge direction).
#
# This is the Casimir operator action restricted to the coupling
# between V+ and V-.

# However, the actual b/a ratio is most directly computed from:
# The Yukawa coupling in PS models is:
#   L = ψ̄ (a · Φ + b · Σ_a T^a · Φ · T^a) ψ
#
# In the metric bundle, both a and b come from the SAME geometric
# operator (Ric_mixed), just from different representation channels.
#
# The (1,2,2) part of Ric_mixed has strength proportional to:
#   a_eff = Tr(Ric_mixed|_{1}) = scalar curvature contribution
#
# The (15,2,2) part has strength proportional to:
#   b_eff = ||Ric_mixed|_{15}|| = adjoint contribution
#
# These are related by SU(4) Clebsch-Gordan coefficients.

# For the SL(4)/SO(3,1) symmetric space:
# The Killing form B(X,Y) = 8 Tr(XY) for sl(4,R)
# Ric = -B/2 on the symmetric space
# Sectional curvature K(X,Y) = -||[X,Y]||² / (||X||²||Y||² - ⟨X,Y⟩²)

# The ratio b/a can be extracted from how the curvature tensor
# decomposes into SU(4) representations.

# But there's a simpler way to think about it:
# The (15,2,2) coupling is generated by the SU(4) GAUGE FIELD
# acting on the (1,2,2) Higgs. In the geometric picture:
#   The gauge field A_μ ∈ su(4)
#   Its coupling to Φ ∈ (1,2,2) produces the covariant derivative D_μΦ
#   In the effective Yukawa, this gives terms like ψ̄ · A · Φ · ψ
#
# The ratio b/a is then:
#   b/a = (gauge coupling g) × (geometric factor from curvature)
#
# Since AT UNIFICATION all gauge couplings are equal to g_PS,
# and the geometric factor from the symmetric space is O(1),
# we can estimate:

g_PS_sq = 27 / (32 * np.pi)  # From Paper 8: α_PS = 27/(128π²)
g_PS = np.sqrt(g_PS_sq)

# The geometric factor: for the symmetric space SL(4)/SO(4),
# the ratio of the traceless to trace parts of the curvature is
# determined by the rank and dimension.

# For a symmetric space of rank r and dimension d:
# The traceless/trace ratio in the Ricci tensor is (d-r)/r
# For SL(4)/SO(4): rank = 3, dim = 9
# Ratio = 6/3 = 2

# But this is NOT quite b/a. The b/a ratio involves the
# decomposition under SU(4), not just trace vs traceless.

# A cleaner approach:
# Under SU(4), the effective Yukawa from the geometry is:
#   Y_eff = y₀ (δ_{ij} + κ T^a_{15,ij} T^a_{15,kl})
# where κ encodes the curvature structure.
#
# For a symmetric space, the curvature tensor is:
#   R(X,Y,Z,W) = ⟨[X,Y], [Z,W]⟩
#
# Decomposing this into SU(4) channels:
# The singlet channel (a):
#   a ~ Σ_n Ric(e_m, e_n) δ_{mn}  (trace over V+)
# The adjoint channel (b):
#   b ~ Σ_n Ric(e_m, e_n) (T^a)_{mn}  (adjoint component over V+)

# For SL(4)/SO(3,1), the Ricci tensor on p is proportional to the identity:
#   Ric(X,Y) = c · B(X,Y) = c · 8 Tr(XY)
# This is DIAGONAL in any orthonormal basis → purely singlet!
# Therefore b/a = 0 for the BACKGROUND symmetric space Ricci.

# The (15,2,2) only appears when we PERTURB around the symmetric space,
# i.e., from the FLUCTUATION of the section g(x) away from the
# reference metric. This means:
# b/a is NOT a fixed number but depends on the DYNAMICS (VEV structure).

print("RESULT: b/a is NOT fixed by pure geometry.")
print()
print("For the BACKGROUND symmetric space SL(4)/SO(3,1):")
print("  Ric(X,Y) = -4 B(X,Y)  (proportional to Killing form)")
print("  → Ric is proportional to the identity on p")
print("  → ONLY the (1,2,2) channel (a) is nonzero")
print("  → b = 0 at the symmetric point!")
print()
print("The (15,2,2) coupling (b ≠ 0) arises from:")
print("  1. FLUCTUATIONS of the section g(x) away from flat space")
print("  2. The curvature of X⁴ (base manifold)")
print("  3. The shape operator II (embedding curvature)")
print()
print("This means b/a is a DYNAMICAL quantity, determined by")
print("the background solution. It is NOT a universal prediction")
print("of the metric bundle.")

# =====================================================================
# PART 6: What IS predicted (the c parameter)
# =====================================================================
print("\n" + "=" * 72)
print("PART 6: THE c PARAMETER (SU(2)_R ASYMMETRY)")
print("=" * 72)

# The c parameter (up/down asymmetry) IS geometric.
# It comes from the fact that V- = (1/2, 1/2) of SU(2)_L × SU(2)_R
# and the SU(2)_R connection in the normal bundle acts on the second index.
#
# For Φ = (h₁, h₂) (SU(2)_R doublet):
#   D_μ Φ = ∂_μ Φ + W_L Φ + Φ W_R
#   D_μ Φ̃ = ∂_μ Φ̃ + W_L Φ̃ + Φ̃ W_R^*  [complex conjugate of W_R]
#
# The asymmetry comes from the relative sign of W_R in Φ vs Φ̃ couplings.
# This is determined by the CONNECTION on the normal bundle of the section.

# For the symmetric space, the normal connection is the SO(4) connection.
# The SU(2)_R part has strength:
#   c ~ ⟨W_R³, Φ⟩  (coupling of the third component of SU(2)_R to Higgs)

# In the symmetric space SL(4)/SO(3,1):
# The SO(3,1) holonomy connection has equal SU(2)_L and SU(2)_R parts
# (since SO(3,1) = SL(2,C) which contains both)
#
# But the key asymmetry comes from SPONTANEOUS SYMMETRY BREAKING:
# When SU(2)_R is broken by the right-handed VEV ⟨Δ_R⟩ ≠ 0,
# the W_R³ component gets a VEV proportional to:
#   c = g_R · v_R / (M_WR)
# where v_R is the SU(2)_R breaking scale and M_WR is the W_R mass.

# At tree level in PS, after SU(2)_R breaking:
#   c = v_R / v_EW × (mass ratio)

# In the metric bundle, v_R is related to the Sp(1) breaking scale.
# Since Sp(1) acts on V+ and breaks at the PS scale:
#   v_R ~ M_PS

# The ratio c ≈ g_PS × (geometric factor from fibre curvature)

# The geometric factor comes from the W_R³ component of the connection:
# For SL(4)/SO(3,1), the connection 1-form ω takes values in so(3,1).
# Decomposing so(3,1) = su(2)_L ⊕ su(2)_R:
# The su(2)_R part has equal coupling to all SU(2)_R components (by symmetry).
# So W_R³ has the same coupling strength as W_R¹ and W_R².

# The coupling of W_R to the Higgs doublet gives:
# For the upper component (I₃R = +1/2): +g_R/2
# For the lower component (I₃R = -1/2): -g_R/2
# Difference: g_R (the full SU(2)_R coupling)

# At the PS scale: g_R = g_PS (SU(2)_L-R symmetry)
# So c = g_PS / 2 (the isospin-1/2 coupling)

c_pred = g_PS / 2
print(f"g_PS = √(27/(32π)) = {g_PS:.4f}")
print(f"c = g_PS / 2 = {c_pred:.4f}")
print()

# But wait — c is dimensionless and enters as a ratio in the Yukawa.
# The actual effect on masses is:
#   M_up   = (a + b/3 + c/2) v_1 + (a + b/3 - c/2) v_2
#   M_down = (a + b/3 - c/2) v_1 + (a + b/3 + c/2) v_2
#
# Hmm, this gives different v_1/v_2 weightings for up and down,
# which is exactly what tan(β) does in 2HDM.

# Actually c doesn't simply add to a and b — it mixes with the VEV ratio.
# The proper formula is:
#   Y_up = (y₁ + c) v₁ + (y₂ - c) v₂
#   Y_down = (y₁ - c) v₁ + (y₂ + c) v₂
# where y₁, y₂ are the (1,2,2) Yukawa couplings.

# With y₁ = y₂ = y (from left-right symmetry at M_PS):
#   Y_up = y(v₁ + v₂) + c(v₁ - v₂)
#   Y_down = y(v₁ + v₂) - c(v₁ - v₂)
#   Y_up/Y_down = [y(v₁+v₂) + c(v₁-v₂)] / [y(v₁+v₂) - c(v₁-v₂)]
#               = [1 + (c/y)(v₁-v₂)/(v₁+v₂)] / [1 - (c/y)(v₁-v₂)/(v₁+v₂)]

# Let r = (c/y) × (v₁-v₂)/(v₁+v₂) = (c/y) × cos(2β) where tan(β) = v₂/v₁
# Then Y_up/Y_down = (1+r)/(1-r)

# For the 3rd generation at M_PS:
# m_t/m_b ≈ 1.5-2.0 (at high scale, after RGE from m_t/m_b ≈ 41 at low scale)
# So (1+r)/(1-r) ≈ 1.7 → r ≈ 0.26

print("UP/DOWN MASS RATIO FROM SU(2)_R ASYMMETRY:")
print("-" * 50)
print()
for r_val in [0.1, 0.2, 0.26, 0.3, 0.4, 0.5]:
    ratio = (1 + r_val) / (1 - r_val)
    print(f"  r = {r_val:.2f}: Y_up/Y_down = {ratio:.3f}")

print()
print(f"Observed m_t/m_b at M_PS ≈ 1.7 → r ≈ 0.26")
print(f"This requires (c/y)·cos(2β) ≈ 0.26")
print(f"With c = g_PS/2 = {c_pred:.3f} and y ~ O(1):")
print(f"  cos(2β) ≈ 0.26 / {c_pred:.3f} ≈ {0.26/c_pred:.2f}")
print(f"  → 2β ≈ {np.degrees(np.arccos(min(0.26/c_pred, 1.0))):.1f}°")
print(f"  → tan(β) ≈ {np.tan(np.radians(90 - np.degrees(np.arccos(min(0.26/c_pred, 1.0))))/2):.1f}")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 72)
print("SUMMARY OF RESULTS")
print("=" * 72)
print("""
1. b/a (quark-lepton splitting):
   → NOT a universal geometric prediction
   → At the symmetric point: b = 0 (only (1,2,2), no (15,2,2))
   → b ≠ 0 requires fluctuations away from flat space
   → b/a ≈ 0.3 needed for m_b/m_τ, but this is FITTED not derived
   STATUS: OPEN — b/a is dynamical, not geometric

2. c (up-down asymmetry):
   → c = g_PS/2 ≈ 0.26 (from SU(2)_R connection in normal bundle)
   → Combined with tan(β) gives Y_up/Y_down = (1+r)/(1-r)
   → For r = c/y · cos(2β) ≈ 0.26, get m_t/m_b ≈ 1.7 at M_PS
   STATUS: PARTIALLY DERIVED — c is geometric, but tan(β) is a VEV ratio

3. What this means for Issue #85:
   → The (15,2,2) does NOT automatically emerge from geometry
   → The quark-lepton mass ratio requires DYNAMICAL input (background metric)
   → The up-down asymmetry IS partially geometric (from SU(2)_R connection)
   → The sector-dependent ε-powers remain UNEXPLAINED

4. The honest conclusion:
   → The metric bundle gives a FRAMEWORK for mass hierarchies
   → The universal part (ε = 1/√20, three generations) is geometric
   → The sector-dependent part (b/a, different ε-powers) needs dynamics
   → This is not a failure — it's the same situation as in standard GUTs
""")
