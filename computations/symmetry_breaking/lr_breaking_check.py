#!/usr/bin/env python3
"""
Left-Right Breaking Check
==========================

The CP³ modes carry equal SU(2)_L and SU(2)_R charge (C2_L = C2_R).
Does the CP³ minimum break SU(2)_R while PRESERVING SU(2)_L?

If both break equally → too much breaking (no SU(2)_L at low energies)
If only SU(2)_R breaks → correct Standard Model pattern

The key: the CP³ minimum selects a specific J. We need to check
which subgroup of SU(2)_L × SU(2)_R is preserved by this J.

Strategy:
1. Find J_min (refined minimum of E(J) on CP³)
2. Compute the residual symmetry: {g ∈ SU(2)_L × SU(2)_R : g·J_min = J_min}
3. Check if SU(2)_L is fully preserved while SU(2)_R is broken

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
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

# Riemann tensor on V+
R_vp = np.zeros((6, 6, 6, 6))
for i in range(6):
    for j in range(6):
        bij = bracket(vp[i], vp[j])
        bij_k = proj_k(bij)
        for k in range(6):
            Rk = -bracket(bij_k, vp[k])
            Rk_p = proj_p(Rk)
            for l in range(6):
                R_vp[i,j,k,l] = dewitt(Rk_p, vp[l])

# SO(3,1) generators
def E4(i,j):
    m = np.zeros((4,4)); m[i,j] = 1; m[j,i] = -1; return m

R1 = E4(2,3); R2 = E4(3,1); R3 = E4(1,2)
B1 = E4(0,1); B2 = E4(0,2); B3 = E4(0,3)
L_gens = [(R1+B1)/2, (R2+B2)/2, (R3+B3)/2]
R_gens = [(R1-B1)/2, (R2-B2)/2, (R3-B3)/2]

# SU(2) actions on V+
T_L_vp = np.zeros((3, 6, 6))
T_R_vp = np.zeros((3, 6, 6))
for g in range(3):
    for i in range(6):
        cL = proj_p(bracket(L_gens[g], vp[i]))
        cR = proj_p(bracket(R_gens[g], vp[i]))
        for j in range(6):
            T_L_vp[g, j, i] = dewitt(cL, vp[j])
            T_R_vp[g, j, i] = dewitt(cR, vp[j])

# J_std and m-generators
J_std = np.zeros((6, 6))
for k in range(3):
    J_std[2*k, 2*k+1] = -1
    J_std[2*k+1, 2*k] = 1

so6_gens = []
for i in range(6):
    for j in range(i+1, 6):
        E = np.zeros((6,6)); E[i,j] = 1; E[j,i] = -1
        so6_gens.append(E)

m_raw = []
for X in so6_gens:
    Xm = (X + J_std @ X @ J_std) / 2
    if np.linalg.norm(Xm) > 1e-10:
        m_raw.append(Xm / np.linalg.norm(Xm))
m_gens = indep_basis(m_raw)

def compute_E(J):
    eigs_J, vecs_J = np.linalg.eig(J)
    plus_i = np.where(np.abs(eigs_J - 1j) < 0.1)[0]
    if len(plus_i) < 3:
        return 1e10
    E = 0.0
    for a in range(3):
        z = vecs_J[:, plus_i[a]]
        v = np.real(z)
        nv = np.linalg.norm(v)
        if nv < 1e-10:
            v = np.imag(z)
            nv = np.linalg.norm(v)
        v = v / nv
        Jv = J @ v
        E += sum(v[i]*Jv[j]*Jv[k]*v[l]*R_vp[i,j,k,l]
                 for i in range(6) for j in range(6)
                 for k in range(6) for l in range(6))
    return E

# =====================================================================
# PART 1: FIND J_min PRECISELY
# =====================================================================

print("=" * 72)
print("PART 1: FINDING J_min")
print("=" * 72)

def E_from_params(params):
    X = sum(params[i] * m_gens[i] for i in range(6))
    R = expm(X)
    J = R @ J_std @ R.T
    if not np.allclose(J @ J, -np.eye(6), atol=1e-6):
        return 1e10
    return compute_E(J)

# Multiple restarts
best_E = 1e10
best_x = None
np.random.seed(42)
for trial in range(40):
    x0 = np.random.randn(6) * 1.5
    r = minimize(E_from_params, x0, method='Powell',
                 options={'maxiter': 5000, 'ftol': 1e-14})
    if r.fun < best_E:
        best_E = r.fun
        best_x = r.x.copy()

print(f"E_min = {best_E:.10f}")

X_min = sum(best_x[i] * m_gens[i] for i in range(6))
R_min = expm(X_min)
J_min = R_min @ J_std @ R_min.T

print(f"J_min:\n{J_min}")
print(f"J² = -I check: {np.max(np.abs(J_min @ J_min + np.eye(6))):.2e}")

# =====================================================================
# PART 2: RESIDUAL SYMMETRY — WHICH SU(2) IS PRESERVED?
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: RESIDUAL SYMMETRY OF J_min")
print("=" * 72)

# For each generator of SU(2)_L and SU(2)_R, check if it preserves J_min.
# "Preserves J" means [T_g, J_min] = 0 on V+.
# (The generator acts on V+ as T_g; J_min acts on V+ as a 6×6 matrix)

print("\nDoes SU(2)_L preserve J_min?")
print("  [T_L_g, J_min] = T_L_g · J_min - J_min · T_L_g")
for g in range(3):
    comm = T_L_vp[g] @ J_min - J_min @ T_L_vp[g]
    norm = np.linalg.norm(comm)
    print(f"  |[T_L_{g+1}, J_min]| = {norm:.8f}")

L_preserves = all(np.linalg.norm(T_L_vp[g] @ J_min - J_min @ T_L_vp[g]) < 1e-6
                   for g in range(3))
print(f"  SU(2)_L preserves J_min: {L_preserves}")

print("\nDoes SU(2)_R preserve J_min?")
for g in range(3):
    comm = T_R_vp[g] @ J_min - J_min @ T_R_vp[g]
    norm = np.linalg.norm(comm)
    print(f"  |[T_R_{g+1}, J_min]| = {norm:.8f}")

R_preserves = all(np.linalg.norm(T_R_vp[g] @ J_min - J_min @ T_R_vp[g]) < 1e-6
                   for g in range(3))
print(f"  SU(2)_R preserves J_min: {R_preserves}")

# Check individual generators for partial preservation
print("\nPartial preservation check:")
for g in range(3):
    comm_L = T_L_vp[g] @ J_min - J_min @ T_L_vp[g]
    comm_R = T_R_vp[g] @ J_min - J_min @ T_R_vp[g]
    # Check if any LINEAR COMBINATION of L and R preserves J
    # [αL_g + βR_g, J] = α[L_g, J] + β[R_g, J] = 0
    # requires [L_g, J] = -β/α [R_g, J], i.e., proportional

    # Check proportionality
    if np.linalg.norm(comm_L) > 1e-8 and np.linalg.norm(comm_R) > 1e-8:
        ratio = np.linalg.norm(comm_L) / np.linalg.norm(comm_R)
        # Check if comm_L + c*comm_R = 0 for some c
        # Minimize |comm_L + c*comm_R|²
        # d/dc = 0 → c = -<comm_L, comm_R> / |comm_R|²
        inner = np.sum(comm_L * comm_R)
        c_opt = -inner / np.sum(comm_R**2)
        residual = np.linalg.norm(comm_L + c_opt * comm_R)
        print(f"  g={g+1}: |[L,J]| = {np.linalg.norm(comm_L):.6f}, "
              f"|[R,J]| = {np.linalg.norm(comm_R):.6f}, "
              f"min|[L+cR, J]| = {residual:.6f} at c = {c_opt:.4f}")
    elif np.linalg.norm(comm_L) < 1e-8:
        print(f"  g={g+1}: L_{g+1} preserves J_min!")
    elif np.linalg.norm(comm_R) < 1e-8:
        print(f"  g={g+1}: R_{g+1} preserves J_min!")

# =====================================================================
# PART 3: CHECK J_std (the standard complex structure)
# =====================================================================

print("\n" + "=" * 72)
print("PART 3: RESIDUAL SYMMETRY OF J_std (for comparison)")
print("=" * 72)

print("\nDoes SU(2)_L preserve J_std?")
for g in range(3):
    comm = T_L_vp[g] @ J_std - J_std @ T_L_vp[g]
    print(f"  |[T_L_{g+1}, J_std]| = {np.linalg.norm(comm):.8f}")

print("\nDoes SU(2)_R preserve J_std?")
for g in range(3):
    comm = T_R_vp[g] @ J_std - J_std @ T_R_vp[g]
    print(f"  |[T_R_{g+1}, J_std]| = {np.linalg.norm(comm):.8f}")

# =====================================================================
# PART 4: WHAT SUBGROUP IS PRESERVED?
# =====================================================================

print("\n" + "=" * 72)
print("PART 4: FINDING THE PRESERVED SUBGROUP")
print("=" * 72)

# The full gauge group acting on V+ is SO(3,1) ≅ SL(2,C).
# In the compact form: SU(2)_L × SU(2)_R.
# The stabilizer of J_min in this group is the preserved gauge symmetry.

# Compute the full stabilizer Lie algebra:
# Find all X ∈ so(3,1) such that [ad_X, J_min] = 0 on V+

# so(3,1) generators acting on V+
so31_gens_on_vp = []
so31_gens_raw = [R1, R2, R3, B1, B2, B3]
so31_labels = ['R1', 'R2', 'R3', 'B1', 'B2', 'B3']

for gen in so31_gens_raw:
    T = np.zeros((6, 6))
    for i in range(6):
        comm = proj_p(bracket(gen, vp[i]))
        for j in range(6):
            T[j, i] = dewitt(comm, vp[j])
    so31_gens_on_vp.append(T)

print("Commutators [X, J_min] for all so(3,1) generators:")
stab_gens = []
for idx, (T, label) in enumerate(zip(so31_gens_on_vp, so31_labels)):
    comm = T @ J_min - J_min @ T
    norm = np.linalg.norm(comm)
    print(f"  |[{label}, J_min]| = {norm:.8f}")
    if norm < 1e-6:
        stab_gens.append((T, label))

print(f"\nStabilizer generators: {[s[1] for s in stab_gens]}")
print(f"Stabilizer dimension: {len(stab_gens)}")

if len(stab_gens) == 0:
    # Try linear combinations
    print("\nNo single generator preserves J_min.")
    print("Searching for linear combinations...")

    # Build the 6×36 matrix: [X, J_min] for each X ∈ so(3,1)
    # X = Σ c_a X_a, so [X, J_min] = Σ c_a [X_a, J_min]
    # We want Σ c_a [X_a, J_min] = 0
    # This is a linear system in the c_a

    comm_vecs = []
    for T in so31_gens_on_vp:
        comm = T @ J_min - J_min @ T
        comm_vecs.append(comm.flatten())

    comm_mat = np.array(comm_vecs)  # 6 × 36
    print(f"\nCommutator matrix shape: {comm_mat.shape}")
    print(f"Rank: {np.linalg.matrix_rank(comm_mat, tol=1e-8)}")

    # Null space = stabilizer
    U, S, Vt = np.linalg.svd(comm_mat)
    print(f"Singular values: {S}")

    null_dim = np.sum(S < 1e-8)
    print(f"Null space dimension (stabilizer dim): {null_dim}")

    if null_dim > 0:
        null_vecs = Vt[len(S)-null_dim:]
        print(f"\nStabilizer generators (as linear combinations):")
        for k in range(null_dim):
            coeffs = null_vecs[k]
            print(f"  Gen {k+1}: " + " + ".join(
                f"{c:.4f}·{l}" for c, l in zip(coeffs, so31_labels) if abs(c) > 1e-4))

            # Verify
            T_stab = sum(coeffs[a] * so31_gens_on_vp[a] for a in range(6))
            verify = T_stab @ J_min - J_min @ T_stab
            print(f"    Verification: |[X, J_min]| = {np.linalg.norm(verify):.2e}")

            # Check if it's in SU(2)_L, SU(2)_R, or mixed
            L_part = np.linalg.norm(coeffs[:3] + coeffs[3:])  # L = (R+B)/2
            R_part = np.linalg.norm(coeffs[:3] - coeffs[3:])  # R = (R-B)/2
            # Actually L_i = (R_i + B_i)/2, so in terms of R,B:
            # c_R1·R1 + c_B1·B1 = (c_R1+c_B1)·L1 + (c_R1-c_B1)·R1g ... no
            # L1 = (R1+B1)/2, R1g = (R1-B1)/2
            # So R1 = L1 + R1g, B1 = L1 - R1g
            # c_R1·R1 + c_B1·B1 = (c_R1+c_B1)·L1 + (c_R1-c_B1)·R1g
            l_coeffs = [(coeffs[k] + coeffs[k+3]) for k in range(3)]
            r_coeffs = [(coeffs[k] - coeffs[k+3]) for k in range(3)]
            print(f"    SU(2)_L part: ({l_coeffs[0]:.4f}, {l_coeffs[1]:.4f}, {l_coeffs[2]:.4f})")
            print(f"    SU(2)_R part: ({r_coeffs[0]:.4f}, {r_coeffs[1]:.4f}, {r_coeffs[2]:.4f})")

# =====================================================================
# PART 5: ALTERNATIVE — CHECK IF THE ENERGY E(J) IS
# SU(2)_L-INVARIANT BUT NOT SU(2)_R-INVARIANT
# =====================================================================

print("\n" + "=" * 72)
print("PART 5: IS E(J) INVARIANT UNDER SU(2)_L? UNDER SU(2)_R?")
print("=" * 72)

# Even if J_min doesn't commute with T_L, the ENERGY E(J) might be
# invariant: E(g·J·g^{-1}) = E(J) for g ∈ SU(2)_L.
# This would mean SU(2)_L is a symmetry of the potential, hence unbroken.

# Check: E(e^{tT_L_g} · J_min · e^{-tT_L_g}) vs E(J_min)
print("\nE(J) under SU(2)_L rotations of J_min:")
for g in range(3):
    print(f"  L_{g+1} direction:")
    for t in [0.1, 0.3, 0.5, 1.0]:
        R_rot = expm(t * T_L_vp[g])
        J_rot = R_rot @ J_min @ R_rot.T
        if np.allclose(J_rot @ J_rot, -np.eye(6), atol=1e-4):
            E_rot = compute_E(J_rot)
            print(f"    t={t:.1f}: E = {E_rot:.8f} (ΔE = {E_rot - best_E:+.6f})")
        else:
            print(f"    t={t:.1f}: J² ≠ -I (rotation left CP³)")

print("\nE(J) under SU(2)_R rotations of J_min:")
for g in range(3):
    print(f"  R_{g+1} direction:")
    for t in [0.1, 0.3, 0.5, 1.0]:
        R_rot = expm(t * T_R_vp[g])
        J_rot = R_rot @ J_min @ R_rot.T
        if np.allclose(J_rot @ J_rot, -np.eye(6), atol=1e-4):
            E_rot = compute_E(J_rot)
            print(f"    t={t:.1f}: E = {E_rot:.8f} (ΔE = {E_rot - best_E:+.6f})")
        else:
            print(f"    t={t:.1f}: J² ≠ -I (rotation left CP³)")

# =====================================================================
# PART 6: THE DIAGONAL SUBGROUP
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: DIAGONAL SU(2) CHECK")
print("=" * 72)

# In left-right symmetric models, the breaking often preserves
# the DIAGONAL subgroup SU(2)_V = {(g,g) : g ∈ SU(2)} ⊂ SU(2)_L × SU(2)_R
# This is the custodial symmetry.

# D_g = L_g + R_g (vector combination)
# A_g = L_g - R_g (axial combination)

D_gens = [T_L_vp[g] + T_R_vp[g] for g in range(3)]
A_gens = [T_L_vp[g] - T_R_vp[g] for g in range(3)]

print("Diagonal SU(2)_V = L+R:")
for g in range(3):
    comm = D_gens[g] @ J_min - J_min @ D_gens[g]
    print(f"  |[D_{g+1}, J_min]| = {np.linalg.norm(comm):.8f}")

print("\nAxial SU(2)_A = L-R:")
for g in range(3):
    comm = A_gens[g] @ J_min - J_min @ A_gens[g]
    print(f"  |[A_{g+1}, J_min]| = {np.linalg.norm(comm):.8f}")

# Check energy invariance under diagonal and axial
print("\nE(J) under SU(2)_V rotations:")
for g in range(3):
    for t in [0.3, 1.0]:
        R_rot = expm(t * D_gens[g])
        J_rot = R_rot @ J_min @ R_rot.T
        if np.allclose(J_rot @ J_rot, -np.eye(6), atol=1e-4):
            E_rot = compute_E(J_rot)
            print(f"  D_{g+1}, t={t}: E = {E_rot:.8f} (ΔE = {E_rot - best_E:+.6f})")

print("\nE(J) under SU(2)_A rotations:")
for g in range(3):
    for t in [0.3, 1.0]:
        R_rot = expm(t * A_gens[g])
        J_rot = R_rot @ J_min @ R_rot.T
        if np.allclose(J_rot @ J_rot, -np.eye(6), atol=1e-4):
            E_rot = compute_E(J_rot)
            print(f"  A_{g+1}, t={t}: E = {E_rot:.8f} (ΔE = {E_rot - best_E:+.6f})")

# =====================================================================
# PART 7: FULL SYMMETRY ANALYSIS
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: COMPLETE SYMMETRY ANALYSIS")
print("=" * 72)

# Compute gradients of E along all so(3,1) directions at J_min
print("Gradient of E(J) along so(3,1) directions at J_min:")
eps = 1e-4
for idx, label in enumerate(so31_labels):
    T = so31_gens_on_vp[idx]
    Jp = expm(eps * T) @ J_min @ expm(-eps * T)
    Jm = expm(-eps * T) @ J_min @ expm(eps * T)
    if np.allclose(Jp @ Jp, -np.eye(6), atol=1e-4) and \
       np.allclose(Jm @ Jm, -np.eye(6), atol=1e-4):
        Ep = compute_E(Jp)
        Em = compute_E(Jm)
        grad = (Ep - Em) / (2*eps)
        curv = (Ep - 2*best_E + Em) / eps**2
        print(f"  {label}: dE/dt = {grad:+.6f}, d²E/dt² = {curv:+.4f}")
    else:
        print(f"  {label}: rotation leaves CP³")

# Also for L, R combinations
print("\nGradient along SU(2)_L and SU(2)_R:")
for g in range(3):
    for label, T in [('L', T_L_vp[g]), ('R', T_R_vp[g])]:
        Jp = expm(eps * T) @ J_min @ expm(-eps * T)
        Jm = expm(-eps * T) @ J_min @ expm(eps * T)
        if np.allclose(Jp @ Jp, -np.eye(6), atol=1e-4) and \
           np.allclose(Jm @ Jm, -np.eye(6), atol=1e-4):
            Ep = compute_E(Jp)
            Em = compute_E(Jm)
            grad = (Ep - Em) / (2*eps)
            curv = (Ep - 2*best_E + Em) / eps**2
            print(f"  {label}_{g+1}: dE/dt = {grad:+.8f}, d²E/dt² = {curv:+.6f}")

# =====================================================================
# PART 8: SUMMARY
# =====================================================================

print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)

print(f"""
Key question: Does the CP³ minimum break SU(2)_R while preserving SU(2)_L?

The answer depends on whether E(J) is invariant under SU(2)_L rotations
of J_min but NOT invariant under SU(2)_R rotations.

If E is INVARIANT under both → neither breaks (symmetric space, no useful breaking)
If E is INVARIANT under L but not R → CORRECT pattern (SM!)
If E varies equally under L and R → left-right symmetric breaking (both break)
If E is invariant under diagonal (L+R) but not axial (L-R) → custodial symmetry

The gradients and curvatures computed above determine the answer.
""")
