#!/usr/bin/env python3
"""
Do CP³ modes carry SU(2)_R charge?
====================================

The CP³ = SU(4)/U(3) tangent space has 6 directions that transform
as 3 ⊕ 3̄ under the selected SU(3)_c.

Question: Do these 6 modes also carry SU(2)_R charge?
If yes → their VEV can break SU(2)_R → U(1)_R at a high scale.

The CP³ modes live in V+ (the positive-norm sector).
SU(2)_R acts on V⁻ (the negative-norm sector).
But through the full SO(3,1) action, SU(2)_R also acts on V+.

We need to compute the SU(2)_R representation content of the CP³ modes.

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from scipy.linalg import expm
np.set_printoptions(precision=8, suppress=True, linewidth=120)

eta = np.diag([-1.0, 1.0, 1.0, 1.0])

def dewitt(h, k):
    t1 = np.einsum('mr,ns,mn,rs', eta, eta, h, k)
    trh = np.einsum('mn,mn', eta, h)
    trk = np.einsum('mn,mn', eta, k)
    return t1 - 0.5 * trh * trk

def proj_k(X):
    return (X - eta @ X.T @ eta) / 2

def proj_p(X):
    return (X + eta @ X.T @ eta) / 2

def bracket(X, Y):
    return X @ Y - Y @ X

# Build basis
p_raw = []
for i in range(4):
    for j in range(4):
        E = np.zeros((4, 4)); E[i,j] = 1.0
        Ep = proj_p(E)
        if np.linalg.norm(Ep) > 1e-10:
            p_raw.append(Ep)

def indep_basis(mats):
    n = mats[0].shape[0]
    vecs = np.array([M.flatten() for M in mats])
    U, S, Vt = np.linalg.svd(vecs, full_matrices=False)
    rank = np.sum(S > 1e-10)
    return [v.reshape(n, n) for v in Vt[:rank]]

p_ind = indep_basis(p_raw)
Gp = np.zeros((10, 10))
for a in range(10):
    for b in range(10):
        Gp[a, b] = dewitt(p_ind[a], p_ind[b])

eigvals_p, eigvecs_p = np.linalg.eigh(Gp)
pos_p = np.where(eigvals_p > 1e-10)[0]
neg_p = np.where(eigvals_p < -1e-10)[0]

vp = []
for idx in pos_p:
    v = eigvecs_p[:, idx]
    mat = sum(v[a] * p_ind[a] for a in range(10))
    mat = mat / np.sqrt(dewitt(mat, mat))
    vp.append(mat)

vm = []
for idx in neg_p:
    v = eigvecs_p[:, idx]
    mat = sum(v[a] * p_ind[a] for a in range(10))
    mat = mat / np.sqrt(-dewitt(mat, mat))
    vm.append(mat)

# SO(3,1) generators
def E4(i,j):
    m = np.zeros((4,4)); m[i,j] = 1; m[j,i] = -1; return m

R1 = E4(2, 3); R2 = E4(3, 1); R3 = E4(1, 2)
B1 = E4(0, 1); B2 = E4(0, 2); B3 = E4(0, 3)
L_gens = [(R1 + B1)/2, (R2 + B2)/2, (R3 + B3)/2]
R_gens = [(R1 - B1)/2, (R2 - B2)/2, (R3 - B3)/2]

print("=" * 72)
print("CP³ MODES: SU(2)_R CHARGE ANALYSIS")
print("=" * 72)

# =====================================================================
# PART 1: SU(2)_L × SU(2)_R ACTION ON V+
# =====================================================================

print("\n--- SU(2)_L × SU(2)_R action on V+ ---")

# For X ∈ so(3,1) = k, h ∈ p: ad_X(h) = [X, h]
# [X, h] has a p-component (stays in tangent space) and a k-component
# The p-component [X, h]_p is the action on tangent vectors

# Compute T_L and T_R matrices on V+ (6×6)
T_L_vp = np.zeros((3, 6, 6))
T_R_vp = np.zeros((3, 6, 6))

for g in range(3):
    for i in range(6):
        comm_L = bracket(L_gens[g], vp[i])
        comm_L_p = proj_p(comm_L)
        comm_R = bracket(R_gens[g], vp[i])
        comm_R_p = proj_p(comm_R)
        for j in range(6):
            T_L_vp[g, j, i] = dewitt(comm_L_p, vp[j])
            T_R_vp[g, j, i] = dewitt(comm_R_p, vp[j])

# Casimirs on V+
C2_L_vp = sum(T_L_vp[g] @ T_L_vp[g] for g in range(3))
C2_R_vp = sum(T_R_vp[g] @ T_R_vp[g] for g in range(3))

print("\nSU(2)_L Casimir on V+:")
print(f"  Eigenvalues: {np.linalg.eigvalsh(C2_L_vp)}")

print("\nSU(2)_R Casimir on V+:")
print(f"  Eigenvalues: {np.linalg.eigvalsh(C2_R_vp)}")

# =====================================================================
# PART 2: DECOMPOSE V+ UNDER SU(2)_L × SU(2)_R
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: V+ DECOMPOSITION UNDER SU(2)_L × SU(2)_R")
print("=" * 72)

# T3_L and T3_R on V+
print("\nT3_L eigenvalues on V+:", np.sort(np.linalg.eigvalsh(T_L_vp[2])))
print("T3_R eigenvalues on V+:", np.sort(np.linalg.eigvalsh(T_R_vp[2])))

# Simultaneous diagonalization
# Since [T3_L, T3_R] should = 0 on V+, we can find simultaneous eigenstates
comm_T3_vp = T_L_vp[2] @ T_R_vp[2] - T_R_vp[2] @ T_L_vp[2]
print(f"\n[T3_L, T3_R] on V+ = 0: {np.allclose(comm_T3_vp, 0, atol=1e-8)}")

# Diagonalize T3_L
evals_T3L, evecs_T3L = np.linalg.eigh(T_L_vp[2])
print(f"\nSimultaneous eigenstates on V+:")
print(f"{'State':>6} | {'T3_L':>8} | {'T3_R':>8} | {'C2_L':>8} | {'C2_R':>8}")
print("-" * 55)
for idx in range(6):
    v = evecs_T3L[:, idx]
    t3L = evals_T3L[idx]
    t3R = v @ T_R_vp[2] @ v
    c2L = v @ C2_L_vp @ v
    c2R = v @ C2_R_vp @ v
    print(f"{idx:>6} | {t3L:>+8.4f} | {t3R:>+8.4f} | {c2L:>8.4f} | {c2R:>8.4f}")

# Under SU(2)_L × SU(2)_R, the symmetric tensor S²(R⁴) = S²(2,2) decomposes as:
# S²(2,2) = (3,3) + (1,1) = 9 + 1 ... no that's for the antisymmetric
# Actually Sym²(2⊗2) is more complex. Let's just read off the quantum numbers.

# =====================================================================
# PART 3: CP³ MODES — EXTRACT AND CHECK CHARGES
# =====================================================================

print("\n" + "=" * 72)
print("PART 3: CP³ MODES AND THEIR SU(2)_R CHARGES")
print("=" * 72)

# Standard complex structure on V+ (in the V+ orthonormal basis)
J_std = np.zeros((6, 6))
for k in range(3):
    J_std[2*k, 2*k+1] = -1
    J_std[2*k+1, 2*k] = 1

# so(6) generators on V+
so6_gens = []
for i in range(6):
    for j in range(i+1, 6):
        E = np.zeros((6,6)); E[i,j] = 1; E[j,i] = -1
        so6_gens.append(E)

# m-generators (CP³ tangent at J_std)
m_raw = []
for X in so6_gens:
    Xm = (X + J_std @ X @ J_std) / 2
    if np.linalg.norm(Xm) > 1e-10:
        m_raw.append(Xm / np.linalg.norm(Xm))
m_gens = indep_basis(m_raw)

print(f"CP³ tangent directions: {len(m_gens)} (expected 6)")

# For each m-generator, compute its SU(2)_R quantum numbers
# The m-generator acts on V+ (internal 6D space)
# We need to relate this to the SU(2)_R action on V+

# The m-generator M_a ∈ so(6) acts on V+ basis as: v_i → Σ_j (M_a)_{ji} v_j
# This infinitesimal change δv = M_a · v maps to a tangent vector in p:
# δh = Σ_j (M_a)_{ji} vp[j] for input vp[i]

# The question is: does the SU(2)_R transformation of this δh have components
# in directions OUTSIDE the CP³ tangent space?

# More directly: compute [T_R_g, M_a] and check if it stays in m or mixes with u(3)

print("\n[SU(2)_R, CP³ tangent] analysis:")
print("If [T_R, m] ⊂ m: CP³ modes transform among themselves under SU(2)_R")
print("If [T_R, m] has u(3) component: CP³ modes mix with gauge modes")

for g in range(3):
    print(f"\n  R_{g+1} action on CP³ modes:")
    for a in range(len(m_gens)):
        # The m-generator M_a acts on V+ as a 6×6 matrix
        # T_R_g also acts on V+ as a 6×6 matrix
        # Their commutator [T_R_g, M_a] acts on V+
        comm = T_R_vp[g] @ m_gens[a] - m_gens[a] @ T_R_vp[g]

        # Decompose comm into u(3) part and m part
        comm_u3 = (comm - J_std @ comm @ J_std) / 2
        comm_m = (comm + J_std @ comm @ J_std) / 2

        norm_u3 = np.linalg.norm(comm_u3)
        norm_m = np.linalg.norm(comm_m)

        print(f"    [R_{g+1}, m_{a}]: |u(3)| = {norm_u3:.6f}, |m| = {norm_m:.6f}")

# =====================================================================
# PART 4: SU(2)_R REPRESENTATION ON CP³ TANGENT
# =====================================================================

print("\n" + "=" * 72)
print("PART 4: SU(2)_R REPRESENTATION ON CP³ = T_J(SU(4)/U(3))")
print("=" * 72)

# Project T_R onto the m-subspace
T_R_m = np.zeros((3, 6, 6))
for g in range(3):
    for a in range(len(m_gens)):
        # Action of T_R_g on m_a: project [T_R_g, m_a] back onto m basis
        comm = T_R_vp[g] @ m_gens[a] - m_gens[a] @ T_R_vp[g]
        # Only keep the m-part
        comm_m = (comm + J_std @ comm @ J_std) / 2
        # Express in m basis
        for b in range(len(m_gens)):
            # Use Killing form on so(6): <X,Y> = -tr(XY)/2
            T_R_m[g, b, a] = -np.trace(m_gens[b].T @ comm_m) / np.trace(m_gens[b].T @ m_gens[b])

print("T_R representation matrices on CP³ tangent space:")
for g in range(3):
    print(f"\n  T_R_{g+1} on m:")
    print(f"  {T_R_m[g]}")

# Casimir
C2_R_m = sum(T_R_m[g] @ T_R_m[g] for g in range(3))
print(f"\nSU(2)_R Casimir on CP³ tangent:")
print(C2_R_m)
c2_eigs = np.linalg.eigvalsh(C2_R_m)
print(f"Eigenvalues: {c2_eigs}")

# Check if any eigenvalues are non-zero
if np.max(np.abs(c2_eigs)) < 1e-6:
    print("\n*** CP³ MODES ARE SU(2)_R SINGLETS ***")
    print("→ They CANNOT break SU(2)_R")
    print("→ SU(2)_R breaking must come from a different mechanism")
else:
    print(f"\n*** CP³ MODES CARRY SU(2)_R CHARGE ***")
    # Identify the representation
    j_values = set()
    for c2 in c2_eigs:
        if abs(c2) > 1e-6:
            # C2 = -j(j+1) for our conventions
            discriminant = 1 + 4*abs(c2)
            j = (-1 + np.sqrt(discriminant)) / 2
            j_values.add(round(j * 2) / 2)  # round to nearest half-integer
    print(f"   j values: {j_values}")
    print(f"→ The CP³ modes include SU(2)_R charged components")
    print(f"→ A VEV on CP³ CAN break SU(2)_R!")

# =====================================================================
# PART 5: ALSO CHECK SU(2)_L
# =====================================================================

print("\n" + "=" * 72)
print("PART 5: SU(2)_L REPRESENTATION ON CP³ TANGENT")
print("=" * 72)

T_L_m = np.zeros((3, 6, 6))
for g in range(3):
    for a in range(len(m_gens)):
        comm = T_L_vp[g] @ m_gens[a] - m_gens[a] @ T_L_vp[g]
        comm_m = (comm + J_std @ comm @ J_std) / 2
        for b in range(len(m_gens)):
            T_L_m[g, b, a] = -np.trace(m_gens[b].T @ comm_m) / np.trace(m_gens[b].T @ m_gens[b])

C2_L_m = sum(T_L_m[g] @ T_L_m[g] for g in range(3))
c2L_eigs = np.linalg.eigvalsh(C2_L_m)
print(f"SU(2)_L Casimir eigenvalues on CP³: {c2L_eigs}")

# =====================================================================
# PART 6: FULL PS QUANTUM NUMBERS OF CP³ MODES
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: FULL PATI-SALAM QUANTUM NUMBERS OF CP³ MODES")
print("=" * 72)

# Under PS = SU(4) × SU(2)_L × SU(2)_R:
# CP³ tangent = T_J(SU(4)/U(3))
# Under SU(3) × U(1)_{B-L}: it's 3_{-2} + 3̄_{+2}
# Under SU(2)_L × SU(2)_R: we just computed

# The U(1)_{B-L} charge: from ad_J eigenvalues (should be ±2i)
gram_m = np.zeros((6, 6))
adJ_m = np.zeros((6, 6))
for i in range(6):
    for j in range(6):
        gram_m[i, j] = np.trace(m_gens[i].T @ m_gens[j])
        comm = bracket(J_std, m_gens[i])
        adJ_m[j, i] = np.trace(m_gens[j].T @ comm)

M_J = np.linalg.solve(gram_m, adJ_m)
bl_charges = np.linalg.eigvals(M_J)
print(f"U(1) charges (ad_J eigenvalues): {np.sort_complex(bl_charges)}")

# T3_R eigenvalues on m
T3R_m = T_R_m[2]  # The diagonal generator
t3R_eigs = np.linalg.eigvalsh(T3R_m)
print(f"T3_R eigenvalues on CP³: {np.sort(t3R_eigs)}")

# T3_L eigenvalues on m
T3L_m = T_L_m[2]
t3L_eigs = np.linalg.eigvalsh(T3L_m)
print(f"T3_L eigenvalues on CP³: {np.sort(t3L_eigs)}")

# Simultaneous eigenvalues
print(f"\nFull quantum numbers of CP³ modes:")
print(f"{'Mode':>6} | {'U(1)_BL':>10} | {'T3_L':>8} | {'T3_R':>8} | {'C2_L':>8} | {'C2_R':>8}")
print("-" * 65)

# Diagonalize the U(1) charge operator
bl_evals, bl_evecs = np.linalg.eig(M_J)
for idx in range(6):
    v = np.real(bl_evecs[:, idx])
    v = v / np.linalg.norm(v)
    bl = np.real(bl_evals[idx])
    t3L = v @ T3L_m @ v
    t3R = v @ T3R_m @ v
    c2L = v @ C2_L_m @ v
    c2R = v @ C2_R_m @ v
    print(f"{idx:>6} | {bl:>+10.4f}i | {t3L:>+8.4f} | {t3R:>+8.4f} | {c2L:>8.4f} | {c2R:>8.4f}")

# =====================================================================
# PART 7: IMPLICATIONS
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: IMPLICATIONS FOR SU(2)_R BREAKING")
print("=" * 72)

if np.max(np.abs(c2_eigs)) > 1e-6:
    print(f"""
RESULT: CP³ modes carry SU(2)_R charge!

This means the CP³ potential minimum (which selects U(3) ⊂ SU(4))
SIMULTANEOUSLY breaks SU(2)_R, because:

  1. The CP³ modes transform as some representation of SU(2)_R
  2. The CP³ potential has a minimum that selects a specific J
  3. This J necessarily breaks the SU(2)_R symmetry acting on CP³

The full breaking from the CP³ potential alone:
  SU(4) × SU(2)_L × SU(2)_R → SU(3) × SU(2)_L × U(1)_Y (?)

If this works, the ENTIRE breaking chain PS → SM comes from
the single CP³ potential on V+. No separate Δ_R or V⁻ mechanism needed!
""")
else:
    print(f"""
RESULT: CP³ modes are SU(2)_R singlets.

The CP³ potential breaks SU(4) → SU(3) × U(1)_{{B-L}} only.
SU(2)_R remains unbroken by V+ curvature.

SU(2)_R breaking must come from:
  - V⁻ sector (bidoublet VEV from Ricci anisotropy)
  - Or: radiative/dynamical mechanism
  - Or: the framework predicts LEFT-RIGHT SYMMETRY at high energies
    (which IS the Pati-Salam prediction — g_L = g_R at unification)
""")
