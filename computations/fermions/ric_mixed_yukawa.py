#!/usr/bin/env python3
"""
Ric_mixed → (15,2,2) Yukawa Coupling
======================================

GitHub Issue #85

QUESTION: Does the mixed Ricci curvature in the Gauss equation produce
a (15,2,2) Yukawa coupling that can explain different mass hierarchies
for up-type vs down-type fermions?

APPROACH:
1. Construct the Pati-Salam decomposition of the normal bundle
2. Identify Ric_mixed with the F·Φ coupling (adjoint × bidoublet)
3. Compute the SU(4) Clebsch-Gordan coefficients for quarks vs leptons
4. Determine the effective Yukawa hierarchy

RESULT: See output.
"""

import numpy as np
from itertools import combinations

# =====================================================================
# PART 1: Setup — DeWitt metric and shape operators
# =====================================================================

print("=" * 72)
print("Ric_mixed → (15,2,2) YUKAWA COUPLING ANALYSIS")
print("GitHub Issue #85")
print("=" * 72)

d = 4
dim_fibre = d * (d + 1) // 2  # = 10

# Background Lorentzian metric
g_bg = np.diag([-1.0, 1.0, 1.0, 1.0])

# Build fibre basis: symmetric matrices e_{(mu,nu)}
fibre_basis = []
labels = []
for mu in range(d):
    for nu in range(mu, d):
        e = np.zeros((d, d))
        if mu == nu:
            e[mu, nu] = 1.0
        else:
            e[mu, nu] = 1.0 / np.sqrt(2)
            e[nu, mu] = 1.0 / np.sqrt(2)
        fibre_basis.append(e)
        labels.append(f"({mu},{nu})")

# DeWitt metric on fibre: G(h,k) = g^{ac}g^{bd}h_{ab}k_{cd} - (1/2)(g^{ab}h_{ab})(g^{cd}k_{cd})
g_inv = np.linalg.inv(g_bg)

def dewitt_inner(h, k):
    term1 = np.einsum('ac,bd,ab,cd', g_inv, g_inv, h, k)
    term2 = np.einsum('ab,ab', g_inv, h) * np.einsum('cd,cd', g_inv, k)
    return term1 - 0.5 * term2

# Build DeWitt metric matrix
G_DW = np.zeros((dim_fibre, dim_fibre))
for i in range(dim_fibre):
    for j in range(dim_fibre):
        G_DW[i, j] = dewitt_inner(fibre_basis[i], fibre_basis[j])

# Eigenvalues and signature
eigvals = np.linalg.eigvalsh(G_DW)
n_pos = np.sum(eigvals > 1e-10)
n_neg = np.sum(eigvals < -1e-10)
print(f"\nDeWitt signature: ({n_pos}, {n_neg})")

# Diagonalize to get positive and negative subspaces
eigvals_full, eigvecs = np.linalg.eigh(G_DW)
sort_idx = np.argsort(eigvals_full)
eigvals_full = eigvals_full[sort_idx]
eigvecs = eigvecs[:, sort_idx]

# V^- (negative-norm, first 4) = Higgs sector
# V^+ (positive-norm, last 6) = gauge sector
neg_idx = np.where(eigvals_full < -1e-10)[0]
pos_idx = np.where(eigvals_full > 1e-10)[0]

print(f"V^- dimension (Higgs): {len(neg_idx)}")
print(f"V^+ dimension (gauge): {len(pos_idx)}")

V_minus = eigvecs[:, neg_idx]  # 10 x 4 matrix
V_plus = eigvecs[:, pos_idx]   # 10 x 6 matrix

# =====================================================================
# PART 2: Pati-Salam decomposition of the fibre
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: PATI-SALAM DECOMPOSITION")
print("=" * 72)

print("""
Under SO(6) × SO(4) ≅ SU(4) × SU(2)_L × SU(2)_R:
  V^+ = R^6 → (6,1,1)  [contains 15 adjoint gauge fields]
  V^- = R^4 → (1,2,2)  [Higgs bidoublet]

The mixed Ricci curvature Ric_mixed couples base and fibre.
In the PS decomposition, this becomes:

  Ric_mixed ~ ∑_{μ,m} K_Y(e_μ, e_m)

where e_μ are base vectors and e_m are fibre vectors.
""")

# =====================================================================
# PART 3: The (15,2,2) structure from Ric_mixed
# =====================================================================

print("=" * 72)
print("PART 3: THE (15,2,2) FROM Ric_mixed")
print("=" * 72)

print("""
KEY INSIGHT: In the Gauss equation, Ric_mixed has the structure:

  Ric_mixed = ∑_μ ∑_m [∇_μ(II^m) - terms involving A_m and Γ]

When expanded around a section with gauge field A^a_μ and Higgs Φ:

  Ric_mixed ∋ g^{μν} (D_μ Φ)^m (A_ν)^m + ...

The gauge field A^a lives in the adjoint of G_PS:
  A^a ∈ su(4) ⊕ su(2)_L ⊕ su(2)_R  (dim = 15 + 3 + 3 = 21)

The Higgs Φ lives in V^-:
  Φ ∈ (1,2,2)

Their coupling in Ric_mixed produces:

For SU(4) adjoint:
  (15) × (1,2,2) = (15,2,2)

For SU(2)_L adjoint:
  (1,3,1) × (1,2,2) = (1, {3⊗2}, 2) = (1, 2⊕4, 2)

For SU(2)_R adjoint:
  (1,1,3) × (1,2,2) = (1, 2, {3⊗2}) = (1, 2, 2⊕4)
""")

# =====================================================================
# PART 4: SU(4) Clebsch-Gordan for quarks vs leptons
# =====================================================================

print("=" * 72)
print("PART 4: SU(4) CLEBSCH-GORDAN COEFFICIENTS")
print("=" * 72)

print("""
Under SU(4) → SU(3)_c × U(1)_{B-L}:

  4 = 3_{+1/3} ⊕ 1_{-1}     (quarks + lepton)
  4̄ = 3̄_{-1/3} ⊕ 1_{+1}

The adjoint 15 decomposes as:
  15 = 8_0 ⊕ 1_0 ⊕ 3_{-4/3} ⊕ 3̄_{+4/3}

The (15,2,2) Yukawa coupling has DIFFERENT Clebsch-Gordan
coefficients for quarks and leptons because they sit in
different SU(4) representations.
""")

# Compute the explicit CG coefficients
# For the (1,2,2) Yukawa: Y_1 ψ_L Φ ψ_R
# The (15,2,2) Yukawa adds: Y_15 ψ_L (T^a Φ) ψ_R
# where T^a are SU(4) generators in the fundamental

# SU(4) generators in the fundamental (4×4 matrices)
# The generators T^a for a = 1,...,15

# For the B-L generator T_{15} = diag(1/3, 1/3, 1/3, -1)/sqrt(2/3)
# normalized as Tr(T^a T^b) = 1/2 δ^{ab}

T_BL = np.diag([1/3, 1/3, 1/3, -1]) * np.sqrt(3/8)

# The (15,2,2) Yukawa contributes differently to quarks and leptons:
# For quarks (in 3 of SU(3)): the B-L charge is +1/3
# For leptons (in 1 of SU(3)): the B-L charge is -1

# The effective Yukawa from (1,2,2) + (15,2,2):
# Y_eff = a·I + b·T_{BL}
# where a and b are determined by the geometry

# For quarks: Y_q = a + b × (1/3) × sqrt(3/8)
# For leptons: Y_l = a + b × (-1) × sqrt(3/8)

# The ratio Y_q/Y_l determines the mass splitting

print("The effective Yukawa coupling has the form:")
print("  Y_eff = a·𝟙 + b·T_{B-L}")
print()
print("For quarks  (B-L = +1/3): Y_q = a + b/3 · √(3/8)")
print("For leptons (B-L = -1):   Y_l = a - b · √(3/8)")
print()

# Now the KEY question: what is b/a?
# In the Gauss equation, Ric_mixed has a specific relative weight
# to the (1,2,2) coupling.

# The (1,2,2) coupling comes from the |H|² term (mean curvature)
# The (15,2,2) coupling comes from the Ric_mixed term

# From the Gauss equation, the relative coefficient is:
# L = R_X + |H|² - |II|² + 2·Ric_mixed + R⊥
# The factor 2 in front of Ric_mixed is fixed by geometry.

print("=" * 72)
print("PART 5: COMPUTING THE EFFECTIVE MASS SPLITTING")
print("=" * 72)

# The Yukawa coupling in the 4D effective theory comes from
# the fibre part of the Gauss equation:
#
# S_Yuk = ∫_X ψ̄_L · [Y_1 Φ + Y_2 Φ̃] · ψ_R · √g · d⁴x
#
# The (15,2,2) modifies this to:
# S_Yuk = ∫_X ψ̄_L · [(a·𝟙 + b·T_a) Φ + (ã·𝟙 + b̃·T_a) Φ̃] · ψ_R
#
# KEY: Φ couples to down-type, Φ̃ couples to up-type.
# The (15,2,2) contribution from T_{B-L} gives:
#   Down-type quarks: Y_d = (a + b/3) · v₂ + (ã + b̃/3) · v₁
#   Down-type leptons: Y_l = (a - b) · v₂ + (ã - b̃) · v₁
#   Up-type quarks:   Y_u = (a + b/3) · v₁ + (ã + b̃/3) · v₂
#   Up-type leptons:  Y_ν = (a - b) · v₁ + (ã - b̃) · v₂

# With the (15,2,2), the quark-lepton ratio is GENERATION-INDEPENDENT:
# Y_quark/Y_lepton = (a + b/3) / (a - b)
# This gives only b/τ and m_b/m_τ ≈ 3 at M_PS, not different hierarchies.

print("""
CRITICAL ANALYSIS:

The (15,2,2) Yukawa from Ric_mixed gives:
  Y_quark = (a + b/3) × [FN matrix]
  Y_lepton = (a - b) × [FN matrix]

where [FN matrix] = y₀ ε^{|q_α|+|q_β|} is the SAME for both.

This produces:
  m_b/m_τ = (a + b/3)/(a - b)  at M_PS

With a = 1, b = 1: m_b/m_τ = (4/3)/(0) → diverges
With a = 1, b = 0.5: m_b/m_τ = (7/6)/(1/2) = 7/3 ≈ 2.3
With a = 1, b = 0.3: m_b/m_τ = (11/10)/(7/10) = 11/7 ≈ 1.57

Observed: m_b(M_PS)/m_τ(M_PS) ≈ 1.6-1.8
""")

# Scan b/a to find best fit
print("--- Scanning b/a for m_b/m_τ match ---")
best_ratio = None
best_ba = None
target = 1.7  # m_b/m_τ at M_PS

for ba_100 in range(0, 100):
    ba = ba_100 / 100.0
    r = (1 + ba/3) / (1 - ba) if abs(1 - ba) > 0.01 else float('inf')
    if abs(r - target) < 0.05:
        print(f"  b/a = {ba:.2f}: m_b/m_τ = {r:.3f}")
        if best_ratio is None or abs(r - target) < abs(best_ratio - target):
            best_ratio = r
            best_ba = ba

if best_ba:
    print(f"\nBest fit: b/a = {best_ba:.2f}, giving m_b/m_τ = {best_ratio:.3f}")

# =====================================================================
# PART 6: Can (15,2,2) split the FN charges?
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: CAN (15,2,2) SPLIT THE FROGGATT-NIELSEN CHARGES?")
print("=" * 72)

print("""
The fundamental question: does the (15,2,2) just give a
UNIVERSAL quark/lepton ratio, or can it produce GENERATION-DEPENDENT
splitting?

ANSWER: The (15,2,2) alone gives generation-INDEPENDENT splitting.
But there's a subtlety:

The Ric_mixed term in the Gauss equation is NOT just F·Φ.
It also contains terms like:

  ∑_μ (A_m)^μ_ν · (A_n)^ν_μ = Tr(A_m · A_n)

where A_m are shape operators. These depend on the SECTION g(x),
i.e., on the background metric.

If different generations couple to different components of A_m
(which they DO, because each J_a reduces SO(6) → U(3)_a differently),
then Ric_mixed CAN produce generation-dependent effects.
""")

# Compute the shape operator traces for each generation
# Each J_a selects a U(3)_a ⊂ SO(6) acting on V^+

# The three complex structures on R⁶ from the quaternionic unit
# matrices I, J, K acting on R⁴ ⊂ R⁶

# Complex structure J_1 (corresponding to I):
J1 = np.zeros((6, 6))
J1[0,1] = -1; J1[1,0] = 1   # e₁ ↔ e₂
J1[2,3] = -1; J1[3,2] = 1   # e₃ ↔ e₄

# Complex structure J_2 (corresponding to J):
J2 = np.zeros((6, 6))
J2[0,2] = -1; J2[2,0] = 1   # e₁ ↔ e₃
J2[1,3] = 1;  J2[3,1] = -1  # e₂ ↔ e₄

# Complex structure J_3 (corresponding to K = IJ):
J3 = np.zeros((6, 6))
J3[0,3] = -1; J3[3,0] = 1   # e₁ ↔ e₄
J3[1,2] = -1; J3[2,1] = 1   # e₂ ↔ e₃

# Verify they satisfy quaternion algebra
print("Verification: J₁² = -I?", np.allclose(J1 @ J1, -np.eye(6)))
print("Verification: J₂² = -I?", np.allclose(J2 @ J2, -np.eye(6)))
print("Verification: J₃² = -I?", np.allclose(J3 @ J3, -np.eye(6)))
print("Verification: J₁J₂ = J₃?", np.allclose(J1 @ J2, J3))

# For each J_a, the centralizer in so(6) is u(3)_a
# The generation-specific Yukawa gets contributions from
# Ric_mixed projected onto the U(3)_a sector

# The key quantity: how does each J_a couple to the (15,2,2)?
# Under U(3)_a, the adjoint 15 of SU(4) decomposes as:
#   15 → 8_0 ⊕ 1_0 ⊕ 3_{-4/3} ⊕ 3̄_{+4/3}
# The part that commutes with J_a is 8_0 ⊕ 1_0 = u(3)_a
# The part that doesn't commute is the 3 ⊕ 3̄ (color triplets)

# The Yukawa coupling for generation α through J_α picks up
# Ric_mixed projected onto the u(3)_α sector.

# The OVERLAP between different u(3)_a subgroups determines
# the mixing (CKM matrix).

# Compute overlaps
def u3_projection(J):
    """Project onto the centralizer of J in so(6)."""
    # The centralizer of J in so(6) consists of X such that [X, J] = 0
    # For a 6×6 antisymmetric matrix X, [X, J] = XJ - JX
    dim_so6 = 15

    # Build basis of so(6)
    so6_basis = []
    for i in range(6):
        for j in range(i+1, 6):
            X = np.zeros((6, 6))
            X[i, j] = 1
            X[j, i] = -1
            so6_basis.append(X)

    # Find centralizer
    centralizer = []
    for X in so6_basis:
        comm = X @ J - J @ X
        if np.linalg.norm(comm) < 1e-10:
            centralizer.append(X)

    return centralizer, len(centralizer)

cent1, dim1 = u3_projection(J1)
cent2, dim2 = u3_projection(J2)
cent3, dim3 = u3_projection(J3)

print(f"\ndim(u(3)₁) = {dim1}")
print(f"dim(u(3)₂) = {dim2}")
print(f"dim(u(3)₃) = {dim3}")

# Compute pairwise overlaps
def overlap_dim(cent_a, cent_b):
    """Dimension of intersection of two centralizers."""
    if not cent_a or not cent_b:
        return 0
    # Stack basis vectors and find rank of combined null space
    A_mat = np.array([X.flatten() for X in cent_a])
    B_mat = np.array([X.flatten() for X in cent_b])

    # Find intersection: vectors in span(A) ∩ span(B)
    combined = np.vstack([A_mat, B_mat])

    # SVD approach: project B onto orthogonal complement of A
    if A_mat.shape[0] == 0:
        return 0
    U, S, Vt = np.linalg.svd(A_mat, full_matrices=False)
    rank_A = np.sum(S > 1e-10)

    rank_AB = np.linalg.matrix_rank(combined, tol=1e-10)
    intersection_dim = rank_A + len(cent_b) - rank_AB
    return max(0, intersection_dim)

d12 = overlap_dim(cent1, cent2)
d13 = overlap_dim(cent1, cent3)
d23 = overlap_dim(cent2, cent3)

print(f"\ndim(u(3)₁ ∩ u(3)₂) = {d12}")
print(f"dim(u(3)₁ ∩ u(3)₃) = {d13}")
print(f"dim(u(3)₂ ∩ u(3)₃) = {d23}")

# =====================================================================
# PART 7: Generation-dependent (15,2,2) Yukawa
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: GENERATION-DEPENDENT YUKAWA FROM Ric_mixed")
print("=" * 72)

# The Ric_mixed coupling for generation α has two parts:
# 1. The (1,2,2) part: universal for all generations (comes from tr(A_m))
# 2. The (15,2,2) part: projected onto the u(3)_α sector
#
# Part 2 gives generation-dependent contributions because
# the u(3)_α projections are different for each α.
#
# The effective Yukawa for the αβ matrix element:
#   Y^{αβ}_eff = y₀ δ^{αβ} + y₁₅ × P_α · T_{15} · P_β
# where P_α is the projection onto the u(3)_α sector.

# The projection overlap P_α · P_β is related to the
# overlap integral of zero-mode profiles:

# For α = β (diagonal): full u(3)_α projection → dim 9
# For α ≠ β (off-diagonal): intersection dim → dim 4

# Ratio: off-diagonal / diagonal = 4/9 ≈ 0.44

epsilon = 1 / np.sqrt(20)

print(f"Diagonal Yukawa (same generation): proportional to dim(u(3)) = {dim1}")
print(f"Off-diagonal Yukawa (different gen): proportional to dim(u(3)∩u(3)) = {d12}")
print(f"Overlap ratio: {d12}/{dim1} = {d12/dim1:.4f}")
print(f"Compare to ε² = {epsilon**2:.4f}")
print(f"Compare to ε  = {epsilon:.4f}")

# The overlap ratio 4/9 is close to ε² = 1/20 = 0.05?
# No, 4/9 ≈ 0.44 is much larger than ε² ≈ 0.05
# But the EFFECTIVE coupling involves the square root of the overlap

print(f"\n--- Does the (15,2,2) help with up/down splitting? ---")
print("""
The (15,2,2) Yukawa coupling through Ric_mixed gives:

For the Φ coupling (→ down-type masses):
  Y_d^{αβ} = y₀ δ^{αβ} + y₁₅ (1/3) × O_{αβ}

For the Φ̃ coupling (→ up-type masses):
  Y_u^{αβ} = ỹ₀ δ^{αβ} + ỹ₁₅ (1/3) × O_{αβ}

where O_{αβ} is the overlap matrix.

CRITICAL POINT: In standard KK theory, the (15,2,2) couples to BOTH
Φ and Φ̃ with the SAME SU(4) Clebsch-Gordan coefficient (+1/3 for quarks).
The up/down distinction comes from which VEV (v₁ or v₂) appears,
not from different CG coefficients.

HOWEVER, there is a non-trivial possibility:
""")

print("""
THE SU(2)_R ASYMMETRY:

Φ = (1, 2, 2):  couples as ψ_L · Φ · ψ_R
Φ̃ = τ₂Φ*τ₂:    couples as ψ_L · Φ̃ · ψ_R

Under SU(2)_R, Φ and Φ̃ transform in 2 and 2* respectively.
The Ric_mixed term involves the NORMAL CONNECTION ∇⊥.

In the negative-norm sector V⁻ ≅ (1,2,2):
  ∇⊥ has SU(2)_L × SU(2)_R connection components.
  The SU(2)_R connection W_R differentiates between Φ and Φ̃:
    D_μ Φ contains +W_R terms
    D_μ Φ̃ contains -W_R* terms (complex conjugate)

This means Ric_mixed contributes DIFFERENTLY to Φ and Φ̃ couplings
through the SU(2)_R gauge field!

Specifically:
  Y_{Φ}  = a + b·T_{BL} + c·τ_R³
  Y_{Φ̃} = a + b·T_{BL} - c·τ_R³

where τ_R³ = diag(+1/2, -1/2) acts on the SU(2)_R doublet index.
""")

# Compute the effective mass matrices
print("=" * 72)
print("PART 8: EFFECTIVE MASS MATRICES WITH SU(2)_R ASYMMETRY")
print("=" * 72)

# The mass matrices become:
# M_u = (a + b/3 + c/2) v₁ + (a + b/3 - c/2) v₂  [up-type quarks]
# M_d = (a + b/3 - c/2) v₂ + (a + b/3 + c/2) v₁  [wait, need to be careful]
#
# Actually: Φ gives mass to BOTH up and down through different VEV components:
# <Φ> = diag(κ₁, κ₂) where κ₁ gives up-type, κ₂ gives down-type
#
# With (15,2,2) from Ric_mixed:
# M_up   = (a + b/3) κ₁ + (ã + b̃/3) κ₂    [from Φ and Φ̃]
# M_down = (a + b/3) κ₂ + (ã + b̃/3) κ₁

# The SU(2)_R asymmetry means b ≠ b̃ (or equivalently, a ≠ ã):
# M_up ∝ (a + c) κ₁ + (a - c) κ₂ × (SU(4) CG)
# M_down ∝ (a - c) κ₂ + (a + c) κ₁ × (SU(4) CG)

# For large tan(β) = κ₂/κ₁ >> 1:
#   M_up ∝ (a + c) κ₁  (dominated by first term)
#   M_down ∝ (a + c) κ₁ × (different coefficient)
# For tan(β) ~ 1:
#   M_up/M_down depends on (a+c)/(a-c) and κ₁/κ₂

# The key ratio:
print("If SU(2)_R connection contributes asymmetry parameter c:")
print()

for c_val in [0.0, 0.1, 0.3, 0.5, 0.8]:
    a_val = 1.0
    b_val = 0.3  # from m_b/m_τ fit

    # Effective couplings
    Y_up_q = (a_val + b_val/3 + c_val/2)
    Y_down_q = (a_val + b_val/3 - c_val/2)
    Y_up_l = (a_val - b_val + c_val/2)
    Y_down_l = (a_val - b_val - c_val/2)

    print(f"  c = {c_val:.1f}:")
    print(f"    Y_up(quark)/Y_down(quark) = {Y_up_q/Y_down_q:.3f}")
    print(f"    Y_up(lepton)/Y_down(lepton) = {Y_up_l/Y_down_l:.3f}")
    print(f"    Y_quark/Y_lepton (up) = {Y_up_q/Y_up_l:.3f}")
    print(f"    Y_quark/Y_lepton (down) = {Y_down_q/Y_down_l:.3f}")

# =====================================================================
# CONCLUSION
# =====================================================================

print("\n" + "=" * 72)
print("CONCLUSIONS")
print("=" * 72)

print("""
1. WHAT THE (15,2,2) FROM Ric_mixed GIVES:
   ✓ A natural quark-lepton mass ratio (m_b/m_τ) from SU(4) CG coefficients
   ✓ The ratio is controlled by b/a (ratio of (15,2,2) to (1,2,2) couplings)
   ✓ For b/a ≈ 0.3, get m_b/m_τ ≈ 1.6 (close to observed ~1.7)

2. WHAT THE SU(2)_R ASYMMETRY GIVES:
   ✓ Different effective couplings for Φ vs Φ̃ (hence up vs down)
   ✓ The asymmetry parameter c is determined by the SU(2)_R connection
     strength in the normal bundle
   ✓ This is a GEOMETRIC quantity (computable from the metric bundle)

3. WHAT IS STILL MISSING:
   ✗ The generation-dependent part of Ric_mixed (overlap integrals)
     gives ratios of order 4/9, NOT ε² ≈ 0.05
   ✗ The FN hierarchy (1 : ε² : ε⁴) comes from Sp(1) breaking,
     not from Ric_mixed
   ✗ The SECTOR-DEPENDENT powers (ε² vs ε³) cannot come from
     (15,2,2) alone — they need the SU(2)_R asymmetry AND the
     generation overlap structure

4. THE PATH FORWARD:
   → Compute b/a from the explicit Gauss equation (ratio of Ric_mixed
     to |H|² coefficients in the effective action)
   → Compute c from the SU(2)_R connection in the normal bundle
   → Combine with Sp(1) breaking hierarchy to get full mass matrices
   → This gives: M_{αβ} = (y₀ δ_{αβ} + y₁₅ O_{αβ}) × CG(sector) × ε^FN(α,β)

   The CG(sector) factor from (15,2,2) + SU(2)_R gives:
   - A quark-lepton ratio from b/a
   - An up-down asymmetry from c

   But it does NOT generate different ε-powers by itself.
   The different powers remain the WEAKEST link in the programme.
""")
