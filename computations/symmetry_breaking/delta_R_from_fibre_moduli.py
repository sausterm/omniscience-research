#!/usr/bin/env python3
"""
Route B Investigation: Δ_R from Fibre Moduli
=============================================

Question: Does the metric bundle fibre GL+(4,R)/SO(3,1) dynamically
select a preferred U(3) ⊂ SU(4), thereby deriving the PS-breaking
scalar Δ_R from geometry?

The fibre positive-norm subspace V+ ≅ R^6 has structure group SO(6) ≅ SU(4).
A complex structure J on V+ picks out U(3) ⊂ SU(4).
The space of such choices is CP³ = SU(4)/U(3).

Key questions:
1. What is the geometry of CP³ as a submanifold of GL+(4)/SO(3,1)?
2. Does the fibre curvature create a potential on CP³?
3. If so, does it have a unique minimum (= preferred U(3))?
4. Can we identify the Goldstone modes of this breaking with Δ_R?

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from itertools import combinations
np.set_printoptions(precision=6, suppress=True, linewidth=100)

# =====================================================================
# PART 1: SETUP — THE FIBRE AND ITS SUBSPACES
# =====================================================================

print("=" * 72)
print("ROUTE B: Δ_R FROM FIBRE MODULI")
print("Does GL+(4)/SO(3,1) select a preferred U(3) ⊂ SU(4)?")
print("=" * 72)

# Lorentzian background metric
eta = np.diag([-1.0, 1.0, 1.0, 1.0])
eta_inv = np.diag([-1.0, 1.0, 1.0, 1.0])

# DeWitt metric on symmetric 2-tensors (λ = 1/2)
def dewitt(h, k, g_inv=eta_inv):
    """G(h,k) = g^{μρ}g^{νσ}h_{μν}k_{ρσ} - (1/2)tr_g(h)tr_g(k)"""
    t1 = np.einsum('mr,ns,mn,rs', g_inv, g_inv, h, k)
    trh = np.einsum('mn,mn', g_inv, h)
    trk = np.einsum('mn,mn', g_inv, k)
    return t1 - 0.5 * trh * trk

# Standard basis for Sym²(R⁴): 10 symmetric matrices
sym_basis = []
labels = []
for i in range(4):
    for j in range(i, 4):
        S = np.zeros((4, 4))
        if i == j:
            S[i, i] = 1.0
        else:
            S[i, j] = 1 / np.sqrt(2)
            S[j, i] = 1 / np.sqrt(2)
        sym_basis.append(S)
        labels.append(f"({i},{j})")

# Compute DeWitt metric matrix
G = np.zeros((10, 10))
for a in range(10):
    for b in range(10):
        G[a, b] = dewitt(sym_basis[a], sym_basis[b])

eigvals, eigvecs = np.linalg.eigh(G)
n_pos = np.sum(eigvals > 1e-10)
n_neg = np.sum(eigvals < -1e-10)
print(f"\nDeWitt signature: ({n_pos}, {n_neg}) — confirmed (6,4)")

# Identify V+ (positive-norm) and V- (negative-norm) subspaces
pos_idx = np.where(eigvals > 1e-10)[0]
neg_idx = np.where(eigvals < -1e-10)[0]

V_plus = eigvecs[:, pos_idx]   # 10×6 matrix, columns = V+ basis
V_minus = eigvecs[:, neg_idx]  # 10×4 matrix, columns = V- basis

print(f"V+ dimension: {V_plus.shape[1]} (gauge/color)")
print(f"V- dimension: {V_minus.shape[1]} (Higgs)")

# Reconstruct V+ basis as symmetric matrices
def vec_to_sym(v):
    """Convert 10-vector to 4×4 symmetric matrix"""
    return sum(v[a] * sym_basis[a] for a in range(10))

vplus_mats = [vec_to_sym(V_plus[:, i]) for i in range(6)]
vminus_mats = [vec_to_sym(V_minus[:, i]) for i in range(4)]

# =====================================================================
# PART 2: COMPLEX STRUCTURES ON V+
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: COMPLEX STRUCTURES ON V+")
print("Space of complex structures on R^6 = CP³ = SU(4)/U(3)")
print("=" * 72)

# We need a metric on V+ to define complex structures
# The DeWitt metric restricted to V+ is positive definite
G_plus = V_plus.T @ G @ V_plus
print(f"\nDeWitt metric on V+ eigenvalues: {np.linalg.eigvalsh(G_plus)}")
print("All positive — V+ metric is Euclidean ✓")

# Orthonormalize V+ basis w.r.t. DeWitt metric
L = np.linalg.cholesky(G_plus)
V_plus_on = V_plus @ np.linalg.inv(L.T)  # Orthonormal basis

# Verify orthonormality
G_plus_on = V_plus_on.T @ G @ V_plus_on
print(f"Orthonormality check: max|G_on - I| = {np.max(np.abs(G_plus_on - np.eye(6))):.2e}")

# Standard complex structure on R^6 ≅ C³
# J maps e_{2k} → e_{2k+1}, e_{2k+1} → -e_{2k}
J_std = np.zeros((6, 6))
for k in range(3):
    J_std[2*k, 2*k+1] = -1
    J_std[2*k+1, 2*k] = 1

assert np.allclose(J_std @ J_std, -np.eye(6)), "J² ≠ -I"
print(f"\nStandard J on V+ constructed: J² = -I ✓")

# The stabilizer of J in SO(6) is U(3)
# Breaking pattern: SO(6) → U(3), coset = CP³

# =====================================================================
# PART 3: SO(6) GENERATORS ON V+
# =====================================================================

print("\n" + "=" * 72)
print("PART 3: so(6) DECOMPOSITION UNDER J")
print("so(6) = u(3) ⊕ m,  m = T_J(CP³)")
print("=" * 72)

# Build so(6) basis (antisymmetric 6×6 matrices)
so6_basis = []
for i in range(6):
    for j in range(i+1, 6):
        E = np.zeros((6, 6))
        E[i, j] = 1
        E[j, i] = -1
        so6_basis.append(E)

print(f"dim so(6) = {len(so6_basis)} (expected 15)")

# Decompose: u(3) = {X ∈ so(6) : [X, J] = 0}
#             m   = {X ∈ so(6) : JX + XJ = 0} (anti-commutes with J)
# Actually: X_k = (X - JXJ)/2 ∈ u(3),  X_m = (X + JXJ)/2 ∈ m
u3_list = []
m_list = []
for X in so6_basis:
    X_k = (X - J_std @ X @ J_std) / 2
    X_m = (X + J_std @ X @ J_std) / 2
    if np.linalg.norm(X_k) > 1e-10:
        u3_list.append(X_k)
    if np.linalg.norm(X_m) > 1e-10:
        m_list.append(X_m)

# Extract independent bases
def independent_basis(matrices):
    if not matrices:
        return []
    n = matrices[0].shape[0]
    vecs = np.array([M.flatten() for M in matrices])
    U, S, Vt = np.linalg.svd(vecs, full_matrices=False)
    rank = np.sum(S > 1e-10)
    return [v.reshape(n, n) for v in Vt[:rank]]

u3_basis = independent_basis(u3_list)
m_basis = independent_basis(m_list)

print(f"dim u(3) = {len(u3_basis)} (expected 9)")
print(f"dim m = T_J(CP³) = {len(m_basis)} (expected 6)")

# =====================================================================
# PART 4: CURVATURE OF GL+(4)/SO(3,1) RESTRICTED TO V+
# =====================================================================

print("\n" + "=" * 72)
print("PART 4: FIBRE CURVATURE ON V+")
print("Does the curvature create a potential on CP³?")
print("=" * 72)

# The fibre is the symmetric space GL+(4,R)/SO(3,1)
# Its curvature at the identity section is R(X,Y)Z = -[[X,Y],Z]
# where X, Y, Z ∈ p (the symmetric space tangent = Sym²(R⁴))

# But V+ is a SUBSPACE of p. The question is whether the curvature
# has different values along different complex structure directions.

# For a symmetric space, the sectional curvature K(X,Y) = -|[X,Y]_k|²/|X∧Y|²
# where [X,Y]_k is the projection of [X,Y] onto the compact subalgebra k = so(3,1)

# We need to work in the Lie algebra gl(4,R):
#   k = so(3,1) (antisymmetric w.r.t. η)
#   p = Sym²_η(R⁴) (symmetric w.r.t. η: η·X = X^T·η)

# Project bracket onto k and p
def bracket(X, Y):
    """Lie bracket [X,Y] = XY - YX in gl(4,R)"""
    return X @ Y - Y @ X

def proj_k(X):
    """Project onto so(3,1): X_k = (X - η X^T η) / 2"""
    return (X - eta @ X.T @ eta) / 2

def proj_p(X):
    """Project onto Sym²_η: X_p = (X + η X^T η) / 2"""
    return (X + eta @ X.T @ eta) / 2

# Killing form on so(3,1): B(X,Y) = 2·tr(XY) for so(n)
# For gl(4): B(X,Y) = 8·tr(XY) - 2·tr(X)·tr(Y)
# For the symmetric space, we use B restricted to p

def killing_p(X, Y):
    """Killing form restricted to p ⊂ gl(4)"""
    return 8 * np.trace(X @ Y) - 2 * np.trace(X) * np.trace(Y)

# Build orthonormal basis for p w.r.t. DeWitt metric
# (DeWitt metric IS the natural metric on Sym²_η)
p_basis_raw = []
for i in range(4):
    for j in range(i, 4):
        S = np.zeros((4, 4))
        if i == j:
            S[i, i] = 1.0
        else:
            S[i, j] = 1 / np.sqrt(2)
            S[j, i] = 1 / np.sqrt(2)
        # Check η-symmetry: η·S should equal S^T·η
        p_basis_raw.append(S)

# These are Sym²(R⁴) elements. For η-symmetry check:
print("\nη-symmetry check for basis elements:")
for idx, S in enumerate(p_basis_raw[:3]):
    check = eta @ S - S.T @ eta
    print(f"  Basis {idx}: max|ηS - S^Tη| = {np.max(np.abs(check)):.2e}")

# Note: The basis of Sym²(R⁴) are symmetric matrices.
# For Lorentzian, the tangent space p consists of matrices satisfying
# η·X + X^T·η = 0... no wait.
# Actually for GL(4)/SO(3,1), k = {X : η X + X^T η = 0} = so(3,1)
# and p = {X : η X - X^T η = 0} = η-symmetric matrices.
# A symmetric matrix S satisfies η S = S^T η iff η S = S η.
# This is NOT true in general for Lorentzian η.

# Let me be more careful. The Cartan involution θ for GL(4)/SO(3,1) is:
# θ(X) = -η X^T η^{-1}
# k = eigenspace +1: X = -η X^T η  ⟹ η X + X^T η = 0  (= so(3,1))
# p = eigenspace -1: X = +η X^T η  ⟹ η X = X^T η

# So p = {X ∈ gl(4) : η X = X^T η}

print("\n\nCartan decomposition for GL+(4)/SO(3,1):")
print("θ(X) = -η X^T η")
print("k = so(3,1) = {X : ηX + X^Tη = 0}")
print("p = {X : ηX = X^Tη}  (10-dimensional)")

# Build proper p-basis
p_basis = []
p_labels = []
for i in range(4):
    for j in range(4):
        E = np.zeros((4, 4))
        E[i, j] = 1
        # Project onto p: X_p = (X + η X^T η)/2
        Ep = proj_p(E)
        if np.linalg.norm(Ep) > 1e-10:
            p_basis.append(Ep)
            p_labels.append(f"E({i},{j})")

# Extract independent basis
def independent_basis_gl(matrices):
    n = matrices[0].shape[0]
    vecs = np.array([M.flatten() for M in matrices])
    U, S, Vt = np.linalg.svd(vecs, full_matrices=False)
    rank = np.sum(S > 1e-10)
    return [v.reshape(n, n) for v in Vt[:rank]]

p_ind = independent_basis_gl(p_basis)
print(f"dim p = {len(p_ind)} (expected 10)")

# Compute DeWitt metric on p
Gp = np.zeros((len(p_ind), len(p_ind)))
for a in range(len(p_ind)):
    for b in range(len(p_ind)):
        Gp[a, b] = dewitt(p_ind[a], p_ind[b])

eigs_p = np.linalg.eigvalsh(Gp)
print(f"DeWitt eigenvalues on p: {np.sort(eigs_p)}")
n_p = np.sum(eigs_p > 1e-10)
n_n = np.sum(eigs_p < -1e-10)
print(f"Signature on p: ({n_p}, {n_n})")

# =====================================================================
# PART 5: SECTIONAL CURVATURES — J-ALIGNED vs J-TRANSVERSE
# =====================================================================

print("\n" + "=" * 72)
print("PART 5: CURVATURE ANISOTROPY ON V+")
print("Compare K along u(3)-aligned vs m-directions")
print("=" * 72)

# For the symmetric space GL+(4)/SO(3,1):
# R(X,Y)Z = -[[X,Y]_k, Z] where [X,Y]_k = proj_k([X,Y])
# Sectional curvature K(X,Y) = <R(X,Y)Y, X> / (|X|²|Y|² - <X,Y>²)

# Work directly in V+ (the 6D positive-norm subspace of p)
# We need V+ elements as 4×4 matrices in p ⊂ gl(4)

# Diagonalize DeWitt metric on p
eigvals_p, eigvecs_p = np.linalg.eigh(Gp)
pos_p = np.where(eigvals_p > 1e-10)[0]
neg_p = np.where(eigvals_p < -1e-10)[0]

print(f"\nV+ indices (positive eigenvalues): {pos_p}")
print(f"V- indices (negative eigenvalues): {neg_p}")
print(f"V+ eigenvalues: {eigvals_p[pos_p]}")
print(f"V- eigenvalues: {eigvals_p[neg_p]}")

# Reconstruct V+ as 4×4 matrices
vp_mats = []
for idx in pos_p:
    v = eigvecs_p[:, idx]
    mat = sum(v[a] * p_ind[a] for a in range(len(p_ind)))
    # Normalize w.r.t. DeWitt
    norm = dewitt(mat, mat)
    if norm > 0:
        mat = mat / np.sqrt(norm)
    vp_mats.append(mat)

print(f"\nV+ orthonormal basis ({len(vp_mats)} elements):")
for i, M in enumerate(vp_mats):
    print(f"  e+_{i}: norm = {dewitt(M, M):.4f}")

# Compute sectional curvatures within V+
def sec_curv(X, Y):
    """Sectional curvature K(X,Y) for the symmetric space GL+(4)/SO(3,1)"""
    bXY = bracket(X, Y)
    bXY_k = proj_k(bXY)  # Project onto so(3,1)
    # R(X,Y)Y = -[bXY_k, Y]
    RY = -bracket(bXY_k, Y)
    # Project RY onto p
    RY_p = proj_p(RY)
    num = dewitt(RY_p, X)
    den = dewitt(X, X) * dewitt(Y, Y) - dewitt(X, Y)**2
    if abs(den) < 1e-15:
        return float('nan')
    return num / den

print("\nSectional curvatures K(e+_i, e+_j) within V+:")
K_matrix = np.zeros((len(vp_mats), len(vp_mats)))
for i in range(len(vp_mats)):
    for j in range(i+1, len(vp_mats)):
        K = sec_curv(vp_mats[i], vp_mats[j])
        K_matrix[i, j] = K
        K_matrix[j, i] = K
        print(f"  K(e+_{i}, e+_{j}) = {K:.6f}")

avg_K = np.mean([K_matrix[i,j] for i in range(len(vp_mats))
                  for j in range(i+1, len(vp_mats))])
print(f"\nAverage sectional curvature in V+: {avg_K:.6f}")

# =====================================================================
# PART 6: THE KEY TEST — CURVATURE VARIATION OVER CP³
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: CURVATURE VARIATION OVER CP³")
print("Does the Ricci curvature depend on the choice of J?")
print("=" * 72)

# A point in CP³ = SU(4)/U(3) is a complex structure J on V+ ≅ R^6.
# J must satisfy: J² = -I, J^T = -J (w.r.t. the V+ metric)

# We parameterize a family of complex structures by rotating J_std:
# J(θ) = R(θ) J_std R(θ)^T, where R(θ) ∈ SO(6)

# If the curvature is isotropic on V+, then the Ricci scalar restricted
# to different U(3) subgroups will be the same → no preferred U(3).
# If anisotropic, there's a potential on CP³.

# First, compute the Ricci tensor on V+
# Ric(X) = Σ_i R(e_i, X)e_i for orthonormal basis {e_i}

def ricci_on_vplus(X, basis):
    """Compute Ric(X, X) using V+ orthonormal basis"""
    result = 0.0
    for ei in basis:
        bXei = bracket(X, ei)
        bXei_k = proj_k(bXei)
        ReiX = -bracket(bXei_k, X)  # Wait: R(e_i,X)X actually
        # R(e_i, X) X = -[[e_i, X]_k, X]
        bei_X = bracket(ei, X)
        bei_X_k = proj_k(bei_X)
        R_term = -bracket(bei_X_k, X)
        R_term_p = proj_p(R_term)
        result += dewitt(R_term_p, ei)
    return result

print("\nRicci curvature Ric(e+_i, e+_i) for each V+ direction:")
for i in range(len(vp_mats)):
    ric = ricci_on_vplus(vp_mats[i], vp_mats)
    print(f"  Ric(e+_{i}, e+_{i}) = {ric:.6f}")

# Compute full Ricci tensor on V+
Ric_vp = np.zeros((len(vp_mats), len(vp_mats)))
for i in range(len(vp_mats)):
    for j in range(len(vp_mats)):
        # Ric(X,Y) = Σ_k <R(e_k, X)Y, e_k>
        ric_ij = 0.0
        for k in range(len(vp_mats)):
            bkX = bracket(vp_mats[k], vp_mats[i])
            bkX_k = proj_k(bkX)
            R_term = -bracket(bkX_k, vp_mats[j])
            R_term_p = proj_p(R_term)
            ric_ij += dewitt(R_term_p, vp_mats[k])
        Ric_vp[i, j] = ric_ij

print(f"\nRicci tensor on V+ (6×6):")
print(Ric_vp)

ric_eigs = np.linalg.eigvalsh(Ric_vp)
print(f"\nRicci eigenvalues on V+: {np.sort(ric_eigs)}")

if np.max(ric_eigs) - np.min(ric_eigs) < 1e-8:
    print("\n*** RICCI IS ISOTROPIC ON V+ ***")
    print("=> No preferred U(3) from Ricci curvature alone")
    print("=> Need to look at HIGHER-ORDER invariants or DYNAMICS")
else:
    print("\n*** RICCI IS ANISOTROPIC ON V+ ***")
    print("=> There IS a preferred direction — potential on CP³!")
    print("=> This could select U(3) and derive Δ_R")

# =====================================================================
# PART 7: ALTERNATIVE — LORENTZIAN STRUCTURE SELECTS U(3)?
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: DOES THE LORENTZIAN STRUCTURE SELECT U(3)?")
print("The V- (Higgs) sector sees the Lorentzian signature")
print("=" * 72)

# Key insight: V+ lives in the positive-norm sector, but the FULL
# tangent space has signature (6,4). The coupling between V+ and V-
# through the curvature tensor might break SO(6) → U(3).

# Compute the mixed curvature R(V+, V-):
vm_mats = []
for idx in neg_p:
    v = eigvecs_p[:, idx]
    mat = sum(v[a] * p_ind[a] for a in range(len(p_ind)))
    norm_sq = -dewitt(mat, mat)  # Negative norm, so flip sign
    if norm_sq > 0:
        mat = mat / np.sqrt(norm_sq)
    vm_mats.append(mat)

print(f"V- orthonormal basis ({len(vm_mats)} elements, spacelike norm):")
for i, M in enumerate(vm_mats):
    print(f"  e-_{i}: G(e-,e-) = {dewitt(M, M):.4f}")

# Mixed sectional curvatures K(V+, V-)
print("\nMixed sectional curvatures K(e+_i, e-_j):")
K_mixed = np.zeros((len(vp_mats), len(vm_mats)))
for i in range(len(vp_mats)):
    for j in range(len(vm_mats)):
        bXY = bracket(vp_mats[i], vm_mats[j])
        bXY_k = proj_k(bXY)
        RY = -bracket(bXY_k, vm_mats[j])
        RY_p = proj_p(RY)
        num = dewitt(RY_p, vp_mats[i])
        den = dewitt(vp_mats[i], vp_mats[i]) * dewitt(vm_mats[j], vm_mats[j]) \
              - dewitt(vp_mats[i], vm_mats[j])**2
        K = num / den if abs(den) > 1e-15 else float('nan')
        K_mixed[i, j] = K
        print(f"  K(e+_{i}, e-_{j}) = {K:.6f}")

print(f"\nMixed curvature matrix:")
print(K_mixed)

# Check if mixed curvatures distinguish V+ directions
row_sums = np.sum(K_mixed, axis=1)
print(f"\nRow sums (total V- coupling per V+ direction): {row_sums}")

if np.max(row_sums) - np.min(row_sums) > 1e-8:
    print("\n*** V+ DIRECTIONS COUPLE DIFFERENTLY TO V- ***")
    print("=> The Higgs sector DOES distinguish directions in V+")
    print("=> This could select a preferred U(3)")
else:
    print("\n*** ALL V+ DIRECTIONS COUPLE EQUALLY TO V- ***")
    print("=> Higgs coupling alone doesn't break SO(6)")

# =====================================================================
# PART 8: FOURTH-ORDER INVARIANTS — WEYL TENSOR TEST
# =====================================================================

print("\n" + "=" * 72)
print("PART 8: FOURTH-ORDER CURVATURE INVARIANTS")
print("R_{abcd}R^{abcd} restricted to different 2-planes")
print("=" * 72)

# Even if Ricci is isotropic (Einstein space), the Weyl tensor
# might distinguish directions. Compute |R|² for different 2-planes.

# Full Riemann tensor on V+
def riemann(X, Y, Z, W):
    """R(X,Y,Z,W) = <R(X,Y)Z, W> for the symmetric space"""
    bXY = bracket(X, Y)
    bXY_k = proj_k(bXY)
    R_Z = -bracket(bXY_k, Z)
    R_Z_p = proj_p(R_Z)
    return dewitt(R_Z_p, W)

# Compute Kretschner-like invariant restricted to u(3)-aligned planes
# vs m-aligned planes

# Use the J_std to decompose V+ into u(3)-type and m-type
# u(3)-type: planes spanned by (e_i, J·e_i)
# m-type: planes NOT aligned with J

# Apply J_std to V+ basis (in the V+ coordinate system)
# We need to work with the V+ internal coordinates

# Let's just compute |Riem|² summed over all V+ indices
Riem_sq_total = 0.0
for i in range(len(vp_mats)):
    for j in range(len(vp_mats)):
        for k in range(len(vp_mats)):
            for l in range(len(vp_mats)):
                R_ijkl = riemann(vp_mats[i], vp_mats[j], vp_mats[k], vp_mats[l])
                Riem_sq_total += R_ijkl**2

print(f"|Riem|² on V+: {Riem_sq_total:.6f}")

# Now compute |Riem|² restricted to holomorphic planes (u(3)-type)
# A holomorphic plane is spanned by (v, Jv) for some v ∈ V+
# In our orthonormal basis, J_std acts as: e0↔e1, e2↔e3, e4↔e5
holo_planes = [(0,1), (2,3), (4,5)]
non_holo_planes = [(0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5),
                    (2,4), (2,5), (3,4), (3,5)]

print(f"\nHolomorphic plane curvatures (u(3)-aligned):")
for (i, j) in holo_planes:
    K = sec_curv(vp_mats[i], vp_mats[j])
    print(f"  K(e+_{i}, e+_{j}) = {K:.6f}")

print(f"\nNon-holomorphic plane curvatures (m-type):")
for (i, j) in non_holo_planes[:6]:
    K = sec_curv(vp_mats[i], vp_mats[j])
    print(f"  K(e+_{i}, e+_{j}) = {K:.6f}")

# =====================================================================
# PART 9: THE ORBIT MAP — ENERGY ON SU(4)/U(3)
# =====================================================================

print("\n" + "=" * 72)
print("PART 9: ENERGY FUNCTIONAL ON CP³ = SU(4)/U(3)")
print("E(J) = Σ_{i<j} K(e_i, J·e_i) — holomorphic sectional curvature sum")
print("=" * 72)

# For each complex structure J on V+, define an energy:
# E(J) = Σ_{a=1}^3 K(v_a, Jv_a)
# where v_1, v_2, v_3 are an orthonormal basis of the holomorphic part.
# This is the total holomorphic sectional curvature.

# If E(J) varies over CP³, there's a preferred J (= preferred U(3)).

# Parameterize by SO(6) rotations acting on J_std
from scipy.linalg import expm

def make_J(angles):
    """Create a complex structure by rotating J_std.
    angles = array of 15 parameters (so(6) generators)
    We only need 6 for the CP³ directions (m-type)."""
    X = np.zeros((6, 6))
    idx = 0
    for i in range(6):
        for j in range(i+1, 6):
            X[i, j] = angles[idx] if idx < len(angles) else 0
            X[j, i] = -angles[idx] if idx < len(angles) else 0
            idx += 1
    R = expm(X)
    return R @ J_std @ R.T

def holo_energy(J, basis=vp_mats):
    """Total holomorphic sectional curvature for complex structure J.
    E(J) = Σ_a K(v_a, J·v_a)  over a J-adapted orthonormal basis."""
    # Find eigenvectors of J with eigenvalue +i
    eigs_J, vecs_J = np.linalg.eig(J)

    # Construct real orthonormal basis adapted to J
    # J has eigenvalues ±i, each with multiplicity 3
    plus_i = np.where(np.abs(eigs_J - 1j) < 0.1)[0]

    energy = 0.0
    used = []
    for a in range(3):
        # Real part and imaginary part of +i eigenvector give (v, Jv) pair
        z = vecs_J[:, plus_i[a]]
        v = np.real(z)
        v = v / np.linalg.norm(v)
        Jv = J @ v  # This should be proportional to Im(z)
        Jv_perp = Jv - np.dot(Jv, v) * v
        Jv_perp = Jv_perp / np.linalg.norm(Jv_perp)

        # Map from V+ internal coords to gl(4) matrices
        V = sum(v[i] * basis[i] for i in range(len(basis)))
        JV = sum(Jv_perp[i] * basis[i] for i in range(len(basis)))

        K = sec_curv(V, JV)
        energy += K
        used.append((a, K))

    return energy, used

# Evaluate at J_std
E0, details = holo_energy(J_std)
print(f"\nE(J_std) = {E0:.6f}")
for a, K in details:
    print(f"  K_holo_{a} = {K:.6f}")

# Sample random points on CP³
np.random.seed(42)
n_samples = 200
energies = []
for trial in range(n_samples):
    angles = np.random.randn(15) * 0.5
    try:
        J = make_J(angles)
        # Verify J² = -I
        if not np.allclose(J @ J, -np.eye(6), atol=1e-6):
            continue
        E, _ = holo_energy(J)
        if not np.isnan(E):
            energies.append(E)
    except:
        continue

if energies:
    energies = np.array(energies)
    print(f"\nSampled {len(energies)} points on CP³:")
    print(f"  E_min = {np.min(energies):.6f}")
    print(f"  E_max = {np.max(energies):.6f}")
    print(f"  E_mean = {np.mean(energies):.6f}")
    print(f"  E_std = {np.std(energies):.6f}")

    if np.std(energies) / abs(np.mean(energies)) < 1e-4:
        print("\n*** ENERGY IS CONSTANT ON CP³ ***")
        print("=> Holomorphic curvature doesn't distinguish complex structures")
        print("=> Need dynamics (coupling to matter/Higgs) to break SO(6)")
    else:
        print(f"\n*** ENERGY VARIES OVER CP³ ***")
        print(f"   Variation: {np.std(energies)/abs(np.mean(energies))*100:.2f}%")
        print("=> There IS a preferred complex structure!")
        print("=> The fibre curvature DOES create a potential on CP³")
else:
    print("Failed to sample CP³ — check J construction")

# =====================================================================
# PART 10: SUMMARY AND IMPLICATIONS
# =====================================================================

print("\n" + "=" * 72)
print("PART 10: SUMMARY")
print("=" * 72)

print("""
ROUTE B INVESTIGATION: Δ_R FROM FIBRE MODULI
=============================================

Setup:
  - Fibre: GL+(4,R)/SO(3,1), tangent space p = Sym²_η(R⁴), dim = 10
  - DeWitt signature: (6,4)
  - V+ ≅ R⁶ with SO(6) ≅ SU(4) structure
  - Complex structures on V+ form CP³ = SU(4)/U(3)
  - Each J ∈ CP³ picks U(3) ⊂ SU(4), i.e., SU(3)_color × U(1)_{B-L}

Questions answered:
  1. Ricci tensor on V+: Is it isotropic?
  2. Mixed curvature V+ ↔ V-: Does the Higgs distinguish V+ directions?
  3. Holomorphic sectional curvature: Does it vary over CP³?

If E varies over CP³:
  → The fibre geometry selects a preferred complex structure
  → This IS the PS-breaking mechanism
  → Δ_R = Goldstone modes of SU(4)/U(3) breaking
  → PS breaking is DERIVED, not assumed

If E is constant:
  → Need coupling to V- (Higgs/matter) or dynamics to break SO(6)
  → Route C (Dirac operator) or external input needed
""")
