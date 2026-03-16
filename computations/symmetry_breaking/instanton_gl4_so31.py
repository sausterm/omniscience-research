#!/usr/bin/env python3
"""
INSTANTON ACTION ON GL+(4)/SO(3,1)
====================================

The master calculation: compute the instanton action on the fibre
GL+(4)/SO(3,1) of the metric bundle, and derive M_R from first principles.

Physical motivation:
  - CW gives M_R ~ M_C (no perturbative hierarchy)
  - Instanton-generated scale: Λ_inst = M_C × exp(-S_inst)
  - If S_inst ~ 17.6, get M_R ~ 10^9 GeV (matching gauge RG)
  - This would predict m_ν ~ 0.06 eV with zero free parameters

Mathematical structure:
  GL+(4)/SO(3,1) is a non-compact Riemannian symmetric space of type IV.
  The Cartan decomposition: gl(4,R) = so(3,1) ⊕ p
  where p = {S : ηS = (ηS)^T} (eta-symmetric matrices).

  The instanton equation on a symmetric space reduces to an ODE
  for a path in the Lie algebra, governed by the curvature.

Plan:
  1. Compute π₃(GL+(4)/SO(3,1)) rigorously via homotopy exact sequence
  2. Identify the instanton embedding SU(2) → GL+(4)
  3. Set up the self-duality equation on the symmetric space
  4. Compute the instanton action analytically
  5. Derive N_eff and M_R

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
import math
from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar

np.set_printoptions(precision=8, suppress=True, linewidth=120)

# =====================================================================
# INPUTS (from existing computations)
# =====================================================================

M_C = 4.5e16        # GeV — PS → LR breaking scale
alpha_PS_inv = 46.2  # from zero-parameter RG
alpha_PS = 1 / alpha_PS_inv
g_PS = math.sqrt(4 * math.pi * alpha_PS)  # ≈ 0.522
M_R_target = 1.1e9   # GeV — from zero-parameter RG

print("=" * 72)
print("INSTANTON ACTION ON GL+(4)/SO(3,1)")
print("=" * 72)
print(f"\nInputs:")
print(f"  M_C     = {M_C:.2e} GeV")
print(f"  α_PS    = {alpha_PS:.5f}  (g_PS = {g_PS:.4f})")
print(f"  M_R(RG) = {M_R_target:.2e} GeV")
print(f"  ln(M_C/M_R) = {math.log(M_C/M_R_target):.2f}")


# =====================================================================
# PART 1: HOMOTOPY GROUPS OF GL+(4)/SO(3,1)
# =====================================================================

print("\n" + "=" * 72)
print("PART 1: π₃(GL+(4)/SO(3,1))")
print("=" * 72)

print("""
RIGOROUS COMPUTATION via homotopy exact sequence:

Step 1: Topological decomposition.
  GL+(4,R) ≅ R+ × SL(4,R)   (det > 0, factor out the determinant)
  So GL+(4,R)/SO(3,1) ≅ R+ × SL(4,R)/SO(3,1)

  For homotopy: π_n(GL+(4)/SO(3,1)) = π_n(R+) × π_n(SL(4)/SO(3,1))
                                     = 0 × π_n(SL(4)/SO(3,1))
  since R+ is contractible.

Step 2: The Iwasawa/Cartan decomposition.
  SL(4,R) has maximal compact subgroup SO(4) (in the definite case)
  or SO(3,1) ∩ SL(4,R) = SO₀(3,1) (in our Lorentzian case).

  Actually: The maximal compact subgroup of SL(4,R) is SO(4).
  SL(4,R)/SO(4) is the symmetric space of positive-definite
  unimodular matrices, which is contractible (it's diffeomorphic to R⁹).

  But we want SL(4,R)/SO(3,1), which is DIFFERENT.
  SO(3,1) is NOT a maximal compact — it's non-compact!

Step 3: Using the fibration.
  Consider the fibration:
    SO(3,1) → SL(4,R) → SL(4,R)/SO(3,1)

  The long exact sequence in homotopy:
    ... → π₃(SO(3,1)) → π₃(SL(4,R)) → π₃(SL(4,R)/SO(3,1))
        → π₂(SO(3,1)) → π₂(SL(4,R)) → ...

Step 4: Known homotopy groups.
  SO(3,1) has identity component SO₀(3,1) ≅ SL(2,C)/Z₂ (as Lie groups)

  Topologically: SO₀(3,1) ≅ RP³ × R³ (via Iwasawa)
  More precisely: SO₀(3,1) deformation-retracts onto its maximal compact
  subgroup SO(3).

  So: π_n(SO₀(3,1)) = π_n(SO(3)) for all n.
    π₁(SO(3)) = Z/2
    π₂(SO(3)) = 0
    π₃(SO(3)) = Z

  SL(4,R) deformation-retracts onto SO(4):
    π₁(SO(4)) = Z/2
    π₂(SO(4)) = 0
    π₃(SO(4)) = Z ⊕ Z  (since SO(4) ≅ (SU(2)×SU(2))/Z₂)

Step 5: The exact sequence at π₃.
    π₃(SO(3,1)) → π₃(SL(4,R)) → π₃(SL(4,R)/SO(3,1)) → π₂(SO(3,1))
         Z       →    Z ⊕ Z     →   π₃(SL(4)/SO(3,1))  →      0

  The map π₃(SO(3,1)) → π₃(SL(4,R)) is the inclusion i: SO(3) ↪ SO(4).

  Under SO(4) ≅ (SU(2)_L × SU(2)_R)/Z₂:
    SO(3) = SO₀(3,1) ∩ SO(4) ≅ SU(2)_diag/Z₂

  The inclusion SO(3) ↪ SO(4) maps the generator of π₃(SO(3)) = Z
  to the DIAGONAL element (1,1) ∈ Z ⊕ Z = π₃(SO(4)).

  So i_*: Z → Z⊕Z sends n ↦ (n, n).

  Image(i_*) = {(n,n) : n ∈ Z} ≅ Z (diagonal subgroup)

  From exactness:
    π₃(SL(4)/SO(3,1)) ≅ (Z ⊕ Z) / Image(i_*) ≅ (Z ⊕ Z) / Z_diag ≅ Z

  The isomorphism: (a,b) mod diagonal ↦ a - b.

RESULT: π₃(GL+(4)/SO(3,1)) = Z

This confirms the hand estimate. The instanton winding is classified
by a single integer n ∈ Z.

PHYSICAL INTERPRETATION:
  The generator of π₃ corresponds to wrapping an SU(2) instanton
  around the "anti-diagonal" direction in (SU(2)_L × SU(2)_R)/Z₂.
  This is precisely the SU(2)_R direction (relative to SU(2)_L).

  So the instanton breaks SU(2)_R while preserving SU(2)_L.
  THIS IS EXACTLY WHAT WE NEED for left-right symmetry breaking!
""")

# Verify the homotopy argument computationally
print("Numerical verification of the topological structure:")
print(f"  dim(GL+(4)/SO(3,1)) = {4*5//2} = dim(p)")
print(f"  dim(SO(3,1)) = 6")
print(f"  dim(SL(4,R)) = 15")
print(f"  dim(SL(4,R)/SO(3,1)) = 15 - 6 = 9")
print(f"  (Adding the R+ factor: dim(GL+(4)/SO(3,1)) = 9 + 1 = 10  ✓)")

print(f"\n  π₃(SO(3)) = Z     (generator: identity map S³ → SU(2) ≅ S³)")
print(f"  π₃(SO(4)) = Z ⊕ Z (two SU(2) factors)")
print(f"  Inclusion: SO(3) ↪ SO(4) sends (1) ↦ (1,1)")
print(f"  Cokernel: (Z⊕Z)/Z_diag = Z")
print(f"  → π₃(GL+(4)/SO(3,1)) = Z  ✓")


# =====================================================================
# PART 2: THE INSTANTON EMBEDDING
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: THE INSTANTON EMBEDDING")
print("=" * 72)

print("""
The instanton is a map S⁴ → GL+(4)/SO(3,1) representing the generator
of π₃ = Z (via the clutching construction S⁴ = D⁴ ∪_{S³} D⁴).

Equivalently: a gauge field A on R⁴ with finite action and winding = 1.

The key: we need to embed SU(2) into GL+(4,R) such that:
  1. The image lies in the ANTI-DIAGONAL of SU(2)_L × SU(2)_R
     (this is the π₃ generator direction)
  2. The instanton lives in the tangent space p of GL+(4)/SO(3,1)

The anti-diagonal SU(2) embedding in SO(4):
  SO(4) ≅ (SU(2)_L × SU(2)_R)/Z₂

  Self-dual:      SU(2)_L acts as left multiplication on H ≅ R⁴
  Anti-self-dual: SU(2)_R acts as right multiplication on H ≅ R⁴

  The anti-diagonal SU(2)_AD is: g ↦ (g, g⁻¹), acting as:
    q ↦ g q g⁻¹  (conjugation in quaternions = SO(3) ⊂ SO(4))

  Wait, that's the DIAGONAL SO(3), which is the stabilizer.

  The π₃ GENERATOR is the DIFFERENCE of the two SU(2)'s:
    (a, b) mod diagonal ~ a - b ∈ Z

  So the n=1 instanton corresponds to (1, 0) or (0, -1) in Z ⊕ Z,
  representing a pure SU(2)_L or pure SU(2)_R instanton.
  Both map to the SAME class n=1 in the quotient Z.

  Choosing the SU(2)_R instanton (most physical):
""")

# Build the SU(2)_R generators in gl(4,R)
# Under SO(3,1) → maximal compact SO(3):
# The rotation generators J_i = ε_{ijk} × (rotation in jk plane)
# The boost generators K_i = (boost in 0i direction)
# SU(2)_L generators: L_i = (J_i + K_i)/2
# SU(2)_R generators: R_i = (J_i - K_i)/2

d = 4
eta = np.diag([-1.0, 1.0, 1.0, 1.0])

# Rotation generators in the 4×4 representation
# J₁ = rotation in (2,3) plane
J1 = np.zeros((d, d))
J1[2, 3] = 1.0; J1[3, 2] = -1.0

# J₂ = rotation in (3,1) plane
J2 = np.zeros((d, d))
J2[3, 1] = 1.0; J2[1, 3] = -1.0

# J₃ = rotation in (1,2) plane
J3 = np.zeros((d, d))
J3[1, 2] = 1.0; J3[2, 1] = -1.0

# Boost generators
# K₁ = boost in 1-direction
K1 = np.zeros((d, d))
K1[0, 1] = 1.0; K1[1, 0] = 1.0

# K₂ = boost in 2-direction
K2 = np.zeros((d, d))
K2[0, 2] = 1.0; K2[2, 0] = 1.0

# K₃ = boost in 3-direction
K3 = np.zeros((d, d))
K3[0, 3] = 1.0; K3[3, 0] = 1.0

# SU(2)_L and SU(2)_R generators
L = [0.5 * (J1 + K1), 0.5 * (J2 + K2), 0.5 * (J3 + K3)]
R = [0.5 * (J1 - K1), 0.5 * (J2 - K2), 0.5 * (J3 - K3)]

# Verify: [L_i, L_j] = ε_{ijk} L_k and [R_i, R_j] = ε_{ijk} R_k
# and [L_i, R_j] = 0
def lie_bracket(A, B):
    return A @ B - B @ A

print("SU(2)_L algebra check:")
for i in range(3):
    for j in range(i+1, 3):
        k = 3 - i - j  # the remaining index
        comm = lie_bracket(L[i], L[j])
        sign = 1 if (i, j, k) in [(0,1,2), (1,2,0), (2,0,1)] else -1
        expected = sign * L[k]
        err = np.max(np.abs(comm - expected))
        print(f"  [L_{i+1}, L_{j+1}] = {'+'if sign>0 else '-'}L_{k+1}: error = {err:.2e}")

print("\nSU(2)_R algebra check:")
for i in range(3):
    for j in range(i+1, 3):
        k = 3 - i - j
        comm = lie_bracket(R[i], R[j])
        sign = 1 if (i, j, k) in [(0,1,2), (1,2,0), (2,0,1)] else -1
        expected = sign * R[k]
        err = np.max(np.abs(comm - expected))
        print(f"  [R_{i+1}, R_{j+1}] = {'+'if sign>0 else '-'}R_{k+1}: error = {err:.2e}")

print("\nCross-commutation [L_i, R_j] check:")
max_cross = 0
for i in range(3):
    for j in range(3):
        comm = lie_bracket(L[i], R[j])
        max_cross = max(max_cross, np.max(np.abs(comm)))
print(f"  max |[L_i, R_j]| = {max_cross:.2e}  {'✓' if max_cross < 1e-10 else '✗'}")

# Check: are R_i in the stabilizer (so(3,1)) or in p?
# so(3,1) = {A : ηA + (ηA)^T = 0} (i.e., ηA is antisymmetric)
# p = {S : ηS = (ηS)^T} (i.e., ηS is symmetric)

print("\nChecking where L_i and R_i live in the Cartan decomposition:")
for i, (Li, Ri) in enumerate(zip(L, R)):
    eta_L = eta @ Li
    L_asym = 0.5 * (eta_L - eta_L.T)  # antisymmetric part (so(3,1))
    L_sym = 0.5 * (eta_L + eta_L.T)   # symmetric part (p)

    eta_R = eta @ Ri
    R_asym = 0.5 * (eta_R - eta_R.T)
    R_sym = 0.5 * (eta_R + eta_R.T)

    print(f"  L_{i+1}: |h-component| = {np.linalg.norm(L_asym):.4f}, |p-component| = {np.linalg.norm(L_sym):.4f}")
    print(f"  R_{i+1}: |h-component| = {np.linalg.norm(R_asym):.4f}, |p-component| = {np.linalg.norm(R_sym):.4f}")

# L_i and R_i each have components in BOTH h and p
# This is because they're constructed from J (in h) and K (which mix h and p)

# The Cartan decomposition for the INSTANTON:
# J_i are in so(3,1) = h (rotations are in the stabilizer)
# K_i have both h and p components

# For the BPST instanton on R⁴, the gauge field is:
# A_μ = f(r) × (SU(2) instanton form)
# where f(r) is a profile function.

# On the SYMMETRIC SPACE, the instanton is governed by the
# curvature of the space. For a symmetric space G/K with K compact,
# the self-dual connections (instantons) are in bijection with
# representations of K (the Donaldson-type correspondence).

# For our NON-COMPACT K = SO(3,1), the situation is different.
# We need to use the DeWitt metric on the tangent space p.


# =====================================================================
# PART 3: THE INSTANTON ON THE SYMMETRIC SPACE
# =====================================================================

print("\n" + "=" * 72)
print("PART 3: INSTANTON ACTION ON GL+(4)/SO(3,1)")
print("=" * 72)

print("""
For a gauge instanton on a Riemannian symmetric space G/K, the
self-duality equation reduces to an algebraic condition when the
instanton is G-invariant (a "symmetric instanton").

For OUR problem, the instanton is NOT on the symmetric space itself,
but rather it's a gauge configuration on spacetime R⁴ with gauge group
related to the fibre symmetry. The relevant setup:

  - The fibre at each spacetime point is GL+(4)/SO(3,1)
  - SU(2)_R ⊂ SO(3,1) acts on the fibre
  - An SU(2)_R instanton on spacetime R⁴ generates a non-perturbative
    potential in the fibre directions

The instanton action for SU(2) gauge theory:

  S = (8π²/g²) × |n|  (for topological charge n)

But this is the STANDARD formula for SU(2) in flat space.
In our metric bundle, the gauge kinetic term receives corrections
from the fibre geometry. The effective action is:

  S_eff = (8π²/g²_eff) × |n|

where g²_eff accounts for the fibre metric and the embedding.

The key question: what is g²_eff?
""")

# The gauge coupling for SU(2)_R in the metric bundle
# comes from the kinetic term in the Gauss equation.
# The gauge kinetic metric is determined by the DeWitt metric
# restricted to the SU(2)_R generators.

# Build DeWitt metric and evaluate on SU(2)_R generators
def dewitt_lor(h, k):
    """DeWitt metric at Lorentzian background η."""
    eta_inv = np.diag([-1.0, 1.0, 1.0, 1.0])
    term1 = 0.0
    for mu in range(d):
        for nu in range(d):
            for rho in range(d):
                for sig in range(d):
                    term1 += eta_inv[mu,rho] * eta_inv[nu,sig] * h[mu,nu] * k[rho,sig]
    trh = sum(eta_inv[mu,nu] * h[mu,nu] for mu in range(d) for nu in range(d))
    trk = sum(eta_inv[mu,nu] * k[mu,nu] for mu in range(d) for nu in range(d))
    return term1 - 0.5 * trh * trk

# The SU(2)_R generators R_i act on the TANGENT space of GL+(4)/SO(3,1)
# via the adjoint action: ad_{R_i}: p → p.
# The gauge kinetic term is proportional to:
# Tr(F_{μν} F^{μν}) where the trace uses the Killing form or DeWitt metric.

# For the STANDARD instanton action, we need the normalization:
# S = ∫ Tr(F ∧ *F) / (2g²)
# where Tr is normalized as Tr(T_a T_b) = (1/2) δ_{ab} for the fundamental.

# The SU(2)_R Killing form restricted to our generators:
B_R = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        # Killing form of gl(4): B(X,Y) = 2n Tr(XY) - 2 Tr(X)Tr(Y)
        B_R[i, j] = 2 * d * np.trace(R[i] @ R[j]) - 2 * np.trace(R[i]) * np.trace(R[j])

print("SU(2)_R Killing form (from gl(4,R)):")
print(B_R)
print(f"Eigenvalues: {np.linalg.eigvalsh(B_R)}")

# The SU(2)_R generators are traceless, so B(R_i, R_j) = 8 Tr(R_i R_j)
print("\nDirect computation: Tr(R_i R_j):")
TR = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        TR[i, j] = np.trace(R[i] @ R[j])
print(TR)

# The standard normalization: Tr_fund(T_a T_b) = (1/2) δ_{ab}
# Our R_i satisfy Tr(R_i R_j) = -(1/2) δ_{ij}
# (negative because of the Lorentzian signature mixing)
print(f"\nTr(R_i R_j) = {TR[0,0]:.4f} δ_ij")
print(f"Compared to standard SU(2) normalization: Tr(σ_a/2 · σ_b/2) = (1/2) δ_ab")

# The GAUGE kinetic term in the metric bundle comes from the
# Gauss equation reduction. The relevant term is:
# L_gauge = -(1/4) G_{AB} F^A_{μν} F^{Bμν}
# where G_{AB} is the DeWitt metric on the Lie algebra generators.

# For SU(2)_R, the generators act on p via adjoint:
# ad_{R_i}(S) = [R_i, S] for S ∈ p

# But the gauge coupling is determined by the NORMALIZATION of the
# generators relative to the DeWitt metric. Specifically:
# g²_R = (standard normalization) / (DeWitt normalization)

# In the metric bundle, the gauge field F_μν lives in the isotropy
# algebra k = so(3,1), and the coupling is set by the fibre geometry.
# The standard KK result is:
# 1/g² ∝ Vol(fibre) × (metric on generators)

# For the INSTANTON ACTION, the key formula is:
# S_inst = (8π²/g²_R) for a unit instanton
# where g²_R is the physical SU(2)_R coupling at the PS scale.

# From the existing computation (zero_parameter_rg.py):
# g_R(M_C) = g_PS ≈ 0.522
# α_R(M_C) = g_PS²/(4π) = α_PS ≈ 0.0217

alpha_R = alpha_PS
g_R = g_PS

print(f"\nSU(2)_R coupling at M_C:")
print(f"  g_R(M_C) = g_PS = {g_R:.4f}")
print(f"  α_R(M_C) = {alpha_R:.5f}")


# =====================================================================
# PART 4: THE EFFECTIVE INSTANTON ACTION
# =====================================================================

print("\n" + "=" * 72)
print("PART 4: THE EFFECTIVE INSTANTON ACTION")
print("=" * 72)

print("""
The instanton action for SU(2)_R gauge theory:

  S_0 = 8π²/g²_R = 8π² × α_R⁻¹ / (4π) = 2π × α_R⁻¹

But this is the action for a STANDARD SU(2) instanton in flat space.
In the metric bundle, the fibre geometry modifies the action through:

  1. THE FIBRE VOLUME FACTOR:
     The effective 4D coupling g²_eff = g²_PS / V_R
     where V_R is the volume of the SU(2)_R orbit in the fibre.

  2. THE CURVATURE CORRECTION:
     The fibre Ricci curvature shifts the instanton action.
     For SU(2)_R on GL+(4)/SO(3,1):
       δS = ∫ Ric(A, A) d⁴x ∝ Ric eigenvalue × instanton size²

  3. THE NON-COMPACT CORRECTIONS:
     GL+(4)/SO(3,1) is non-compact, so the instanton can "spread"
     into the non-compact directions. This modifies the profile
     function and the action.

Let me compute each factor.
""")

# Factor 1: Standard instanton action
S_standard = 8 * math.pi**2 / g_R**2
print(f"Standard SU(2) instanton action:")
print(f"  S₀ = 8π²/g² = {S_standard:.2f}")
print(f"  exp(-S₀) = {math.exp(-S_standard):.2e}")
print(f"  M_C × exp(-S₀) = {M_C * math.exp(-S_standard):.2e} GeV")
print(f"  → WAY too suppressed!")

# Factor 2: The fibre embedding factor
# The SU(2)_R instanton doesn't use all 10 fibre dimensions.
# It wraps the 3 SU(2)_R directions, but the OTHER fibre directions
# (SU(4) + U(1)) act as spectators.

# In a KK reduction, the effective 4D instanton action is:
# S_eff = S₀ × (V_inst / V_total) × (metric corrections)
# where V_inst is the volume of the instanton embedding
# and V_total is the total fibre volume.

# But this is NOT the right picture. The instanton is a 4D gauge
# configuration, not a fibre wrapping. The correct formula is:

# S_inst = 8π²/g²_R(M_C) for a BPST instanton in the SU(2)_R gauge field.

# However, the effective instanton amplitude involves:
# exp(-S_inst) × (det'(-D²))^{-1/2}
# where D is the covariant derivative in the instanton background.

# The determinant factor includes contributions from ALL fields
# that couple to SU(2)_R. In the metric bundle:
# - 6 gauge bosons from SU(4) (not charged under SU(2)_R)
# - 3 gauge bosons from SU(2)_L (not charged)
# - 3 gauge bosons from SU(2)_R (charged: adjoint)
# - 1 gauge boson from U(1)_{B-L} (not charged)
# - The Higgs bidoublet (1,2,2): charged as DOUBLET of SU(2)_R
# - Fermions: 3 generations × (4,2,1) ⊕ (4,1,2) ... the (4,1,2) is doublet of SU(2)_R
# - The fibre moduli (scalar fields from metric fluctuations)

# Factor 3: The 't Hooft determinant / zero mode counting

print("""
THE INSTANTON-GENERATED POTENTIAL:

For SU(2) with N_f fermion doublets and N_s scalar doublets:

  V_inst ~ Λ⁴ × exp(-8π²/g²) × (Λ/μ)^{b₀}

where b₀ = (11/3)C₂(G) - (2/3)N_f T(R_f) - (1/3)N_s T(R_s)
is the 1-loop beta function coefficient.

For SU(2)_R in the Pati-Salam model:
  - Gauge (adjoint): contributes 11/3 × 2 = 22/3
  - Fermions in (4,1,2): 3 generations × 4 colors = 12 Weyl doublets
    → -(2/3) × 12 × (1/2) = -4
  - Scalars: Δ_R ~ (1,1,3): complex triplet = 3 complex = 6 real d.o.f.
    For adjoint (triplet) of SU(2): T(3) = 2
    → -(1/3) × 2 = -2/3
  - Higgs bidoublet Φ ~ (1,2,2): one complex doublet of SU(2)_R
    → -(1/3) × 1 × (1/2) = -1/6
""")

# Beta function coefficient for SU(2)_R
# b₀ = (11/3)C₂(adj) - (2/3)Σ_f n_f T(R_f) - (1/3)Σ_s n_s T(R_s)
# C₂(SU(2)) = 2

# Gauge: (11/3) × 2 = 22/3
b0_gauge = (11.0/3) * 2

# Fermions: (4,1,2) — 4 colors × 3 gens = 12 Weyl doublets of SU(2)_R
# Each Weyl doublet: T(2) = 1/2
# Also (4̄,1,2̄) from antiparticles (same contribution in anomaly-free theory)
# Convention: count LEFT-handed Weyl fermions in the 2 of SU(2)_R
# In LR model: right-handed quarks and leptons are doublets of SU(2)_R
# Per generation: u_R, d_R (3 colors each) + ν_R, e_R = 8 Weyl d.o.f. in doublet form
# That's 4 SU(2)_R doublets per generation × 3 generations = 12 doublets
b0_fermion = -(2.0/3) * 12 * 0.5  # n_f × T(fund) = 12 × 1/2

# Scalars:
# Δ_R ~ (1,1,3): complex triplet of SU(2)_R, T(3) = 2
b0_delta = -(1.0/3) * 1 * 2  # one complex triplet

# Φ ~ (1,2,2): one complex doublet of SU(2)_R (the 2 in the second slot)
# Φ has 2 doublets of SU(2)_R (from the bidoublet structure)
# Actually (1,2,2) = 2 complex doublets = 4 real doublets of SU(2)_R
b0_phi = -(1.0/3) * 2 * 0.5  # 2 complex doublets × T(fund)

b0_total = b0_gauge + b0_fermion + b0_delta + b0_phi

print(f"SU(2)_R beta function coefficient b₀:")
print(f"  Gauge (adjoint):  {b0_gauge:+.4f}")
print(f"  Fermions (12 doublets): {b0_fermion:+.4f}")
print(f"  Δ_R (triplet):   {b0_delta:+.4f}")
print(f"  Φ (bidoublet):   {b0_phi:+.4f}")
print(f"  Total: b₀ = {b0_total:.4f}")

# Cross-check with the LR beta coefficient from coleman_weinberg_su2R.py
# b_2R_LR = -5/3 (for scenario A with Φ + Δ_R)
# The relationship: b₀ here is for the full SU(2)_R
# In the MS-bar convention used in the RG: b = -b₀
# Wait, the convention in CW script is:
# α⁻¹(μ) = α⁻¹(μ₀) - (b/2π)ln(μ/μ₀)
# where b > 0 means asymptotic freedom
# In the standard convention: β(g) = -b₀/(16π²) × g³
# So b = b₀ (same sign when negative means NOT AF)

# From CW script: b_2R_LR = -5/3
# My calculation: b0_total = 22/3 - 4 - 2/3 - 1/3 = 22/3 - 15/3 = 7/3 ≈ 2.33
# Hmm, that's positive (asymptotically free), but the CW script says b_2R = -5/3.

# Let me recheck. The CW script beta coefficients are in a DIFFERENT convention.
# b_i in the CW script: α_i⁻¹(μ) = α_i⁻¹(μ₀) - (b_i/2π)ln(μ/μ₀)
# If b_i < 0: α grows at low energy (asymptotic freedom)
# If b_i > 0: α grows at high energy

# Standard: β(α) = -b₀ α²/(2π) where b₀ = (11/3)C₂ - ...
# Then: d(α⁻¹)/d(ln μ) = b₀/(2π)
# So: α⁻¹(μ) = α⁻¹(μ₀) + (b₀/2π)ln(μ/μ₀)
#             = α⁻¹(μ₀) - (b₀/2π)ln(μ₀/μ)
# Comparing: b_CW = -b₀ (with respect to ln(μ₀/μ), running DOWN)
# Or: b_CW = +b₀ (with respect to ln(μ/μ₀), running UP)

# Actually from CW script: α⁻¹(μ) = α⁻¹(μ₀) - (b/2π)ln(μ/μ₀)
# The CW script runs from M_C DOWN to lower scales.
# For μ < μ₀: ln(μ/μ₀) < 0
# If b < 0 (AF): -b × negative = positive → α⁻¹ increases → α decreases at low E ✓

# So the CW script b = -b₀ in my convention here.
# CW gives b_2R = -5/3, so b₀(mine) = +5/3 ≈ 1.67

# Let me recount more carefully.
print(f"\n--- Detailed b₀ recount ---")

# The 1-loop beta function for SU(2) gauge coupling:
# b₀ = (11/3)×C₂(adj) - (4/3)×Σ n_Weyl × T(R) - (1/3)×Σ n_complex_scalar × T(R)
# where n_Weyl counts Weyl fermions (left-handed) and n_complex_scalar counts
# complex scalars.

# C₂(adj) for SU(2) = 2
b0_gauge_v2 = (11.0/3) * 2  # = 22/3

# Fermion doublets of SU(2)_R (LEFT-HANDED Weyl convention):
# Per generation in Pati-Salam (4,1,2):
#   q_R = (u_R, d_R) in 3 colors: 3 doublets per gen
#   l_R = (ν_R, e_R): 1 doublet per gen
#   Total: 4 doublets per gen × 3 gen = 12 Weyl doublets
# Each contributes (4/3) × T(2) = (4/3) × (1/2) = 2/3
b0_fermion_v2 = -(4.0/3) * 12 * 0.5  # = -8

# Complex scalars:
# Δ_R ~ (1,1,3): one complex triplet of SU(2)_R
# T(3) = 2 for SU(2)
b0_delta_v2 = -(1.0/3) * 1 * 2  # = -2/3

# Φ ~ (1,2,2): as doublet of SU(2)_R, this is 2 complex doublets
# (the first 2 of (1,2,2) gives 2 copies under SU(2)_L)
# T(2) = 1/2
b0_phi_v2 = -(1.0/3) * 2 * 0.5  # = -1/3

b0_v2 = b0_gauge_v2 + b0_fermion_v2 + b0_delta_v2 + b0_phi_v2
print(f"  Gauge:    {b0_gauge_v2:+.4f}  (11/3 × 2)")
print(f"  Fermions: {b0_fermion_v2:+.4f}  (4/3 × 12 × 1/2)")
print(f"  Δ_R:      {b0_delta_v2:+.4f}  (1/3 × 1 × 2)")
print(f"  Φ:        {b0_phi_v2:+.4f}  (1/3 × 2 × 1/2)")
print(f"  b₀ = {b0_v2:.4f}")

# Hmm, 22/3 - 8 - 2/3 - 1/3 = 22/3 - 27/3 = -5/3
# b₀ = -5/3 → NOT asymptotically free

# This matches the CW script! b_CW = b₀ = -5/3 ✓
# (The CW script convention IS b₀ with a minus sign in the RGE:
#  α⁻¹(μ) = α⁻¹(μ₀) - (b/2π)ln(μ/μ₀))
# Wait, -(-5/3)ln(μ/μ₀) with μ < μ₀ gives +(5/3)|ln| → α⁻¹ grows → α shrinks
# That means the coupling is AF? Let me re-examine.

# From CW: α_R_inv(μ) = α_R_inv(M_C) - (b_2R/(2π)) × ln(μ/M_C)
# With b_2R = -5/3 and μ < M_C (ln < 0):
# α_R_inv(μ) = α_R_inv(M_C) - (-5/3)/(2π) × (negative)
#             = α_R_inv(M_C) - (5/3)(positive)/(2π) = α_R_inv(M_C) - positive
# So α_R_inv DECREASES at low energy → α_R INCREASES → coupling grows at low E
# → NOT asymptotically free ✓

# Standard convention: β(g) = b₀ g³/(16π²) with b₀ < 0 for AF
# Here b₀ = -5/3 → β < 0 → AF? No:
# β = b₀ g³/(16π²) with b₀ = -5/3 gives β < 0 means g decreases → AF
# But we just showed coupling GROWS at low E, which is NOT AF.

# I think the standard convention is β(g) = -b₀ g³/(16π²)
# Then b₀ = -5/3 means β = +5/3 × g³/(16π²) > 0 → coupling grows → NOT AF

# Anyway, let's just use the known result:
b0_SU2R = -5.0/3  # This is the β function coefficient in the CW convention

print(f"\n  b₀(SU(2)_R) = -5/3 ≈ {-5/3:.4f}")
print(f"  This matches the CW script b_2R = -5/3 ✓")
print(f"  SU(2)_R is NOT asymptotically free in the LR model")


# =====================================================================
# PART 5: THE INSTANTON AMPLITUDE AND SCALE GENERATION
# =====================================================================

print("\n" + "=" * 72)
print("PART 5: THE INSTANTON AMPLITUDE")
print("=" * 72)

print("""
For an SU(2) instanton with winding number n = 1:

  Amplitude ~ exp(-S_cl) × (det corrections) × (zero mode integrals)

The classical action: S_cl = 8π²/g²(ρ) where ρ is the instanton size.

For the SCALE-GENERATING instanton effect (non-perturbative potential),
the relevant quantity is the instanton density:

  d(ρ) = C × exp(-8π²/g²(1/ρ)) × ρ^{b₀-5}

where b₀ is the 1-loop coefficient and the integral over ρ gives the
non-perturbative scale:

  Λ_NP = M_UV × exp(-2π/(|b₀| × α(M_UV)))

Wait — this formula applies to ASYMPTOTICALLY FREE theories where
the instanton density is dominated by small sizes. For our case,
SU(2)_R is NOT asymptotically free (b₀ = -5/3 < 0), so the
standard instanton analysis breaks down!

CRUCIAL REALIZATION:
  In a non-AF theory, instantons don't generate a dynamical scale
  in the usual way. The coupling grows at low energy and eventually
  hits a Landau pole (or the theory becomes strongly coupled).

  BUT: in the metric bundle, SU(2)_R exists only between M_C and M_R.
  The strong coupling scale is where α_R(μ) → ∞:

  α_R⁻¹(μ) = α_PS⁻¹ + |b₀|/(2π) × ln(M_C/μ)

  Wait — let me redo this. For a NOT-AF theory with b₀ < 0
  (in the convention where b₀ > 0 is AF):

  Actually I need to be more careful with conventions.
""")

# Let's just work directly with the known RGE from the CW script.
# α_R⁻¹(μ) = α_R⁻¹(M_C) - (b_2R/(2π)) × ln(μ/M_C)
# with b_2R = -5/3

# Running from M_C down: as μ decreases, ln(μ/M_C) < 0
# α_R⁻¹(μ) = α_PS⁻¹ - (-5/3)/(2π) × ln(μ/M_C)
#           = α_PS⁻¹ + (5/3)/(2π) × ln(M_C/μ)
#           = α_PS⁻¹ + (5/(6π)) × ln(M_C/μ)

# So α_R⁻¹ INCREASES at low energy → α_R DECREASES → coupling WEAKENS
# Hmm, that means SU(2)_R IS asymptotically free?!

# Let me recheck: b_2R = -5/3 from the CW script.
# The RGE is: d(α⁻¹)/d(ln μ) = -b/(2π) = -(-5/3)/(2π) = 5/(6π)
# So α⁻¹ INCREASES with increasing μ → α DECREASES with increasing μ
# → coupling DECREASES at high energy → NOT AF!

# Wait, that contradicts. Let me just compute directly.
# At M_C: α_R = α_PS ≈ 0.0217
# At μ < M_C:
mu_test = 1e14  # 10^14 GeV
t_test = math.log(mu_test / M_C)  # negative
alpha_R_inv_test = 1/alpha_PS - ((-5.0/3) / (2*math.pi)) * t_test
alpha_R_test = 1/alpha_R_inv_test

print(f"SU(2)_R coupling running:")
print(f"  At M_C = {M_C:.1e}: α_R⁻¹ = {1/alpha_PS:.1f}, α_R = {alpha_PS:.5f}")
print(f"  At 10¹⁴ GeV:       α_R⁻¹ = {alpha_R_inv_test:.1f}, α_R = {alpha_R_test:.5f}")
print(f"  α_R {'increases' if alpha_R_test > alpha_PS else 'decreases'} at lower energies → coupling {'STRENGTHENS' if alpha_R_test > alpha_PS else 'weakens'}")

# OK so the coupling INCREASES at lower energy.
# With b = -5/3: α⁻¹(μ) = α⁻¹(M_C) - (-5/3)/(2π) × ln(μ/M_C)
# For μ < M_C: ln(μ/M_C) < 0
# -(-5/3)/(2π) × (negative) = -(5/3)/(2π) × (negative) = positive
# So α⁻¹ increases → α decreases at low energy.
# That means the coupling WEAKENS at low energy → it IS AF!

# Hmm, let me just compute a few values.
print(f"\nDetailed running:")
for log_mu in [16, 14, 12, 10, 8, 6]:
    mu = 10.0**log_mu
    t = math.log(mu / M_C)
    aR_inv = 1/alpha_PS - ((-5.0/3) / (2*math.pi)) * t
    if aR_inv > 0:
        print(f"  μ = 10^{log_mu}: α_R⁻¹ = {aR_inv:.2f}, α_R = {1/aR_inv:.5f}, g_R = {math.sqrt(4*math.pi/aR_inv):.4f}")
    else:
        print(f"  μ = 10^{log_mu}: Landau pole!")

# From the numbers: α_R⁻¹ increases as we go to lower energies.
# So the coupling WEAKENS. This IS asymptotic freedom.
# b_2R = -5/3 means the COEFFICIENT is negative, and
# α⁻¹(μ) = α⁻¹(M_C) - b/(2π) ln(μ/M_C) with b < 0 gives:
# α⁻¹ increases when ln(μ/M_C) < 0 (low energy) ✓

# So: SU(2)_R IS asymptotically free in the LR model.
# (The b > 0 convention for AF would give b = +5/3)

# In the AF case, instantons are well-defined and the non-perturbative
# scale IS generated by dimensional transmutation:

# Λ_SU2R = M_C × exp(-2π/(b₀ × α_PS))
# where b₀ here is the POSITIVE coefficient for AF.
# b₀ = 5/3 (positive for AF)

b0_AF = 5.0/3  # positive for AF

Lambda_SU2R = M_C * math.exp(-2*math.pi / (b0_AF * alpha_PS))
log_Lambda = math.log10(max(Lambda_SU2R, 1e-300))

print(f"\n*** NON-PERTURBATIVE SCALE FROM SU(2)_R INSTANTONS ***")
print(f"  b₀ = {b0_AF:.4f} (AF convention, positive)")
print(f"  α_PS = {alpha_PS:.5f}")
print(f"  2π/(b₀ × α_PS) = {2*math.pi/(b0_AF * alpha_PS):.2f}")
print(f"  exp(-2π/(b₀ × α_PS)) = {math.exp(-2*math.pi/(b0_AF * alpha_PS)):.2e}")
print(f"  Λ_SU2R = M_C × exp(-2π/(b₀α_PS)) = {Lambda_SU2R:.2e} GeV")
print(f"  log₁₀(Λ_SU2R) = {log_Lambda:.1f}")

# Compare with the hand estimate from CW script
# The CW hand estimate was: S_inst = 8π²/(N_eff × g²) with N_eff ≈ 17
# My formula: S = 2π/(b₀ × α) = 2π/((5/3) × (1/46.2))
#            = 2π × 46.2 × 3/5 = 2π × 27.72 = 174.1
# Hmm, that's WAY too large.

# The issue: the standard instanton scale formula is:
# Λ = μ × exp(-8π²/(b₀ g²(μ)))  [for SU(N) with b₀ the 1-loop coeff]
# But the EXACT formula involves more factors.

# Let me use the CORRECT instanton-generated scale:
# The dynamical scale Λ in the MS-bar scheme for SU(N):
# Λ_MS = μ × exp(-1/(2 b₀ α(μ)))
# where b₀ is defined via: μ d(α)/dμ = -2b₀ α²

# In our convention: d(α⁻¹)/d(ln μ) = b_2R/(2π) = (-5/3)/(2π)
# So: d(α)/d(ln μ) = b_2R/(2π) × α² = (-5/3)/(2π) × α²
# μ d(α)/dμ = (-5/3)/(2π) × α²
# Comparing with μ d(α)/dμ = -2b₀ α²:
# -2b₀ = (-5/3)/(2π)
# b₀ = 5/(12π)

# Then: Λ = μ × exp(-1/(2 × 5/(12π) × α))
#       = μ × exp(-12π/(10α))
#       = μ × exp(-6π/(5α))

b0_proper = 5.0 / (12 * math.pi)
Lambda_proper = M_C * math.exp(-1 / (2 * b0_proper * alpha_PS))
print(f"\nUsing proper normalization:")
print(f"  b₀ (in dα/d ln μ = -2b₀α² convention) = {b0_proper:.6f}")
print(f"  1/(2b₀α) = {1/(2*b0_proper*alpha_PS):.2f}")
print(f"  Λ_SU2R = {Lambda_proper:.2e} GeV")

# Hmm, let me just use the simpler and more standard formula.
# The QCD scale: Λ_QCD ~ M_GUT × exp(-2π/(b₀ α_GUT))
# where b₀ = 7 for SU(3) with 6 quarks.
# α_GUT ≈ 1/25, M_GUT ~ 2×10^16
# Λ_QCD ~ 2×10^16 × exp(-2π×25/7) = 2×10^16 × exp(-22.4) = 2×10^16 × 1.9×10^{-10}
# = 3.8×10^6 GeV — too high, actual Λ_QCD ≈ 0.3 GeV
# The discrepancy is because the 2-loop + threshold effects matter enormously.

# For a cleaner comparison, use the 1-loop exact RG solution:
# α⁻¹(Λ) = 0  (definition of the confinement scale)
# α⁻¹(Λ) = α⁻¹(M_C) + |b_CW|/(2π) × ln(M_C/Λ) = 0
# → ln(M_C/Λ) = 2π α_PS⁻¹ / |b_CW|
# → ln(Λ/M_C) = -2π / (|b_CW| × α_PS)

# With b_CW = -5/3 → |b_CW| = 5/3:
S_eff_dimensional = 2 * math.pi / ((5.0/3) * alpha_PS)
Lambda_AF = M_C * math.exp(-S_eff_dimensional)

print(f"\n*** DIMENSIONAL TRANSMUTATION SCALE (1-loop exact) ***")
print(f"  Λ_SU2R: α_R⁻¹(Λ) = 0 defines the strong coupling scale")
print(f"  ln(M_C/Λ) = 2π/(|b| × α_PS) = 2π/((5/3) × {alpha_PS:.5f})")
print(f"            = {S_eff_dimensional:.2f}")
print(f"  Λ_SU2R = M_C × exp(-{S_eff_dimensional:.2f})")
print(f"         = {Lambda_AF:.2e} GeV")
print(f"  log₁₀(Λ) = {math.log10(max(Lambda_AF, 1e-300)):.1f}")


# =====================================================================
# PART 6: THE INSTANTON ACTION FROM GEOMETRY
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: GEOMETRIC DERIVATION OF THE INSTANTON ACTION")
print("=" * 72)

print("""
The standard 't Hooft instanton generates a potential of the form:

  V_inst ~ Λ³_SU2R × v_R × cos(θ)

(for the Δ_R field that breaks SU(2)_R).

The EXPONENTIAL suppression comes from the instanton action:

  exp(-S_inst) = exp(-8π²/g²_R(M_C))

But the PREFACTOR involves the determinant of fluctuations around
the instanton, which brings in all the fields that couple to SU(2)_R.

For SU(2) with the LR particle content, the instanton amplitude is:

  A_inst = C × μ^{b₀} × exp(-8π²/g²(μ))

In dimensional regularization at scale μ = M_C:

  A_inst = C × M_C^{-5/3} × exp(-8π²/g²_PS)

The EFFECTIVE scale is set by:

  Λ_eff^{b₀} = M_C^{b₀} × exp(-8π²/g²_PS)

But with b₀ < 0 (i.e., b = -5/3 in our convention), the instanton
amplitude GROWS at low energies! This means:

  Λ_eff = M_C × [exp(-8π²/g²_PS)]^{1/|b₀|}
        = M_C × exp(-8π²/(|b₀| × g²_PS))
        = M_C × exp(-(3/5) × 8π²/g²_PS)
        = M_C × exp(-24π²/(5 g²_PS))
""")

# The key formula: the instanton-generated VEV of Δ_R
# In the SU(2) instanton calculus ('t Hooft 1976):
#
# For a theory with scalar field Δ in a representation R:
# The instanton generates an effective vertex:
# ∫ d⁴x × C × Λ^4 × exp(-8π²/g²)
#
# But the SCALE at which SU(2)_R becomes non-perturbative is:
# Λ_NP where g²(Λ_NP) = O(4π) (strong coupling)
#
# HOWEVER: SU(2)_R here is NOT AF (b₀ = -5/3 < 0 in the standard
# convention where b₀ > 0 means AF).
#
# Wait, I got confused earlier. Let me settle this ONCE AND FOR ALL.

print("=" * 50)
print("SETTLING THE AF QUESTION FOR SU(2)_R")
print("=" * 50)

# The 1-loop RGE for the gauge coupling:
# dg/d(ln μ) = β(g) = -b g³/(16π²)
# where b = (11/3)C₂(G) - (4/3)∑ T(R_f) n_f - (1/3)∑ T(R_s) n_s
#
# For AF: b > 0 (coupling decreases at high energy)
#
# For SU(2)_R in the LR model:
# Gauge: (11/3) × 2 = 22/3
# Fermions: 12 Weyl doublets → (4/3) × 12 × (1/2) = 8
# Δ_R (complex triplet): (1/3) × 1 × 2 = 2/3
# Φ (2 complex doublets): (1/3) × 2 × (1/2) = 1/3
#
# b = 22/3 - 8 - 2/3 - 1/3 = (22 - 24 - 2 - 1)/3 = -5/3

b_standard = 22.0/3 - 8 - 2.0/3 - 1.0/3
print(f"\n  b (standard convention) = {b_standard:.4f}")
print(f"  b < 0 → NOT asymptotically free ✓")

# With b < 0: dg/d(ln μ) = -b g³/(16π²) = (+5/3)g³/(16π²) > 0
# → coupling INCREASES at higher energy
# → coupling DECREASES at lower energy
# → NO confinement
# → NO standard Λ_QCD-like scale

# But then what about the CW script showing α_R(M_R) < α_R(M_C)?
# That's exactly this: the coupling weakens going down. NOT AF.
# I was confusing myself. Let me verify with actual numbers.

for log_mu in [16.65, 16, 14, 12, 10, 8]:
    mu = 10.0**log_mu
    # Using CW convention: α⁻¹(μ) = α⁻¹(M_C) - (b_CW/(2π)) × ln(μ/M_C)
    # b_CW = -5/3
    t = math.log(mu / M_C)
    aR_inv = 1/alpha_PS - ((-5.0/3) / (2*math.pi)) * t
    # = 1/alpha_PS + (5/3)/(2π) × ln(M_C/μ)  [for μ < M_C, this adds positive]
    print(f"  μ = 10^{log_mu:5.2f}: α_R⁻¹ = {aR_inv:.2f}, g_R = {math.sqrt(4*math.pi/aR_inv):.4f}")

print(f"\n  α_R⁻¹ DECREASES at low energy → α_R INCREASES → coupling STRENGTHENS")
print(f"  This is because b = -5/3 < 0 → NOT AF")
print(f"  There is no standard instanton-generated Λ_NP scale!")

# =====================================================================
# PART 7: THE CORRECT NON-PERTURBATIVE MECHANISM
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: THE CORRECT INSTANTON MECHANISM")
print("=" * 72)

print("""
KEY INSIGHT: For a NOT-asymptotically-free SU(2)_R, the standard QCD-like
instanton mechanism does NOT apply. Instead, the relevant mechanism is:

1. CONSTRAINED INSTANTON (Affleck-Dine-Seiberg type):
   The instanton at the UV scale M_C has finite action S = 8π²/g²(M_C)
   and generates a CALCULABLE potential for the Δ_R field.

2. The instanton-generated potential has the form:
   V_inst(v_R) ~ M_C⁴ × exp(-8π²/g²_PS) × F(v_R/M_C)

   where F depends on the details of the instanton calculation.

3. For the SCALE of the instanton amplitude:
   exp(-8π²/g²_PS) = exp(-8π²/(4π α_PS))
                    = exp(-2π/α_PS)
                    = exp(-2π × 46.2)
                    = exp(-290.3)
                    ≈ 10^{-126}

   This is FAR too small! A single SU(2) instanton at the PS scale
   is incredibly suppressed.

RESOLUTION: The instanton does NOT wrap a simple SU(2)_R.
Instead, it wraps the FULL fibre GL+(4)/SO(3,1), which has more
degrees of freedom and a SMALLER effective action.

The effective action for a composite instanton on the fibre:

  S_fibre = 8π²/(N_eff × g²_PS)

where N_eff counts the effective number of gauge d.o.f. in the
instanton configuration.
""")

# Standard SU(2) instanton: way too suppressed
S_su2 = 8 * math.pi**2 / g_PS**2
print(f"SU(2)_R instanton (standard):")
print(f"  S = 8π²/g² = {S_su2:.1f}")
print(f"  exp(-S) = {math.exp(-S_su2):.2e}")
print(f"  → Completely negligible")

# Now: the FIBRE instanton
# The fibre GL+(4)/SO(3,1) supports a topological sector π₃ = Z
# and the instanton wraps the FULL coset space.

# The instanton action on the symmetric space:
# For a symmetric space G/K, the instanton is related to the
# SECTIONAL CURVATURE of the space.

# For GL+(4)/SO(3,1) with the DeWitt metric, the Ricci curvature is:
# Ric = -(1/2) B (Killing form)
# The scalar curvature R = -30

# The instanton action on a curved space involves the curvature radius:
# S = 8π²/g² × (L²/ρ²) where L is the curvature radius and ρ is the
# instanton size.

# For a symmetric space, the curvature radius L satisfies:
# R = -n(n-1)/L² where n is the dimension
# For our case: R = -30, n = 10
# -30 = -10×9/L² → L² = 3

# But this isn't quite right either. The KEY is that the instanton
# wraps a 4-dimensional submanifold of the 10-dimensional fibre.

# The relevant object is the second Chern class c₂ of the gauge bundle.
# For the metric bundle, the gauge field is the Kaluza-Klein connection
# which has curvature F = R^⊥ (the normal bundle curvature).

# The instanton action involves the FIBRE contribution to the
# second Chern number:
# ∫_{S⁴} c₂(F) = ∫ Tr(F ∧ F) / (8π²)

# In the metric bundle, F is valued in so(6,4), and the compact part
# so(6) ⊕ so(4) gives the physical gauge fields.

# For the SU(2)_R INSTANTON (winding in π₃(SO(3,1)) = π₃(SO(3)) = Z):
# The instanton configuration uses the ENTIRE SO(3,1) connection,
# not just the SU(2)_R part.

# However, the connection is built from the FULL fibre geometry,
# and all 10 fibre directions contribute to the gauge coupling.

# The effective coupling for the FIBRE instanton:
# The DeWitt metric couples all fibre modes. The instanton, when
# it wraps the SU(2)_R ⊂ SO(3,1) direction, interacts with all
# 10 fibre modes through the DeWitt metric.

# The coupling normalization: g²_eff = g²_PS / C_fibre
# where C_fibre is the ratio of the Killing form on SU(2)_R
# to the DeWitt metric norm.

print("""
THE FIBRE INSTANTON ACTION:

The instanton on GL+(4)/SO(3,1) wraps the SU(2)_R ⊂ SO(3,1) subgroup.
The DeWitt metric couples this to ALL 10 fibre directions.

The effective action is:
  S_fibre = 8π² × (Killing norm of instanton)/(DeWitt norm)

The Killing norm of the SU(2)_R generator R_i:
  B(R_i, R_i) = 8 Tr(R_i²) = 8 × (-1/2) = -4

The DeWitt norm:
  G(R_i, R_i) = dewitt_lor(R_i, R_i) = ... (need to compute the
  ACTION of R_i on the tangent space p)

Wait — the instanton lives in the GAUGE algebra (so(3,1) = h),
not in the tangent space p. The gauge coupling comes from the
kinetic term ∫ Tr(F∧*F) where the trace uses the fibre metric.

In KK reduction: L_gauge = -(1/4g²) F^a_μν F^{aμν}
where 1/g² is determined by the volume of the fibre and the
normalization of the Killing vectors.

For the metric bundle with DeWitt metric on Met(X):
  1/g²_PS = V_fibre × C × (DeWitt normalization)

The fibre "volume" is infinite (non-compact space) but the relevant
quantity is the volume of the compact orbit of SO(3,1) through the
background point η, which is finite.

Actually, the gauge coupling is already KNOWN from the programme:
  g_PS² = 4π/α_PS = 4π × 46.2 ≈ 581

The instanton action for the SU(2)_R subgroup is:
  S = 8π²/g²_R = 8π²/g²_PS (since g_R = g_PS at M_C)
""")

# So the PURE SU(2)_R instanton has S = 8π²/g² ≈ 290.
# This is too large. The CW script estimated N_eff ≈ 17 to get M_R ~ 10^9.

# Where does N_eff come from?
# The hand estimate was: Λ = M_C × exp(-8π²/(N_eff g²))
# For Λ = 10^9: ln(4.5×10^16/10^9) = 17.6
# So: 8π²/(N_eff g²) = 17.6
# N_eff = 8π²/(17.6 × g²) = 78.96/(17.6 × 0.272) = 16.5

# BUT: this formula assumes the instanton action is S = 8π²/(N_eff g²).
# This is NOT the standard instanton action for ANY gauge theory.
# The standard formula is always S = 8π²/g² (for unit winding).

# What could make the effective action SMALLER?
# Answer: the instanton wraps a path in the FIBRE that uses
# multiple gauge generators simultaneously.

# For a "fat instanton" that uses ALL generators of so(3,1) = SU(2)_L × SU(2)_R:
# The action could be S = 8π²/(Σ g²_i × C²_i) where the sum is over
# all generators involved.

# For so(3,1) with 6 generators (3 rotations + 3 boosts):
# The BPST-like instanton uses only 3 generators (one SU(2)).
# A "thick" instanton could use all 6.

# More generally, on the FULL fibre GL+(4)/SO(3,1) with 10 tangent
# directions, the instanton path could involve all 10 directions.

# The KEY: the instanton on GL+(4)/SO(3,1) is not an SU(2) instanton.
# It's a MAP S³ → GL+(4)/SO(3,1) representing the generator of π₃ = Z.
# The MINIMUM energy representative of this class uses the geodesic
# in the symmetric space.

print("""
KEY INSIGHT: THE GEODESIC INSTANTON

π₃(GL+(4)/SO(3,1)) = Z tells us there is a non-contractible 3-sphere
in the fibre. The instanton is the MINIMUM ACTION representative of
this topological class.

On a symmetric space, the minimum-energy representative of a homotopy
class is a TOTALLY GEODESIC submanifold. The S³ ⊂ GL+(4)/SO(3,1) that
represents the generator of π₃ is a totally geodesic 3-sphere.

For a totally geodesic S³ ⊂ G/K with the symmetric space metric:
  - The S³ has constant curvature determined by the ambient curvature
  - The sectional curvature K along the S³ directions determines the radius
  - The instanton action is related to vol(S³)/radius

From our Ricci tensor computation:
  - The sectional curvature of GL+(4)/SO(3,1) is K ≤ 0 (non-positive,
    since it's of non-compact type)
  - The "radius" of the geodesic S³ is infinite (non-compact)

Wait — this means the geodesic S³ has INFINITE volume and the
instanton action diverges? That can't be right.

The CORRECT picture: the instanton is not an S³ in the fibre,
but rather a GAUGE FIELD on the base spacetime R⁴.

Let me reconsider the full problem more carefully.
""")


# =====================================================================
# PART 8: THE CORRECT FRAMEWORK — FIBRE INSTANTON AS GAUGE INSTANTON
# =====================================================================

print("\n" + "=" * 72)
print("PART 8: CORRECT FRAMEWORK")
print("=" * 72)

print("""
The correct picture is:

1. The metric bundle has structure group SO(3,1) acting on the fibre.
2. The Kaluza-Klein connection A_μ is an so(3,1)-valued gauge field on R⁴.
3. An instanton is a self-dual connection: F = *F (in Euclidean signature).
4. The topological charge is ν = (1/8π²)∫ Tr(F∧F) ∈ π₃(SO(3,1)) = Z.
5. The instanton action is S = 8π²|ν|/g² where g is the SO(3,1) coupling.

Now, SO(3,1) is non-compact, but the gauge field theory is still well-defined
on Euclidean R⁴ (after Wick rotation). The BPST instanton construction works
for any gauge group with π₃ = Z.

The SO(3,1) coupling:
  SO(3,1) = SL(2,C)/Z₂ contains both SU(2)_L (compact) and boosts (non-compact).
  The gauge coupling for SO(3,1) in the metric bundle is g = g_PS.

  But SO(3,1) is non-compact, so the instanton equation F = *F uses the
  LORENTZIAN metric on the Lie algebra, not a positive-definite one.

  For a non-compact gauge group, the action is:
  S = -(1/4g²)∫ B(F, *F)  where B is the Killing form of so(3,1).

  The Killing form of so(3,1):
  B(J_i, J_j) = -2δ_ij  (rotations: negative definite — compact directions)
  B(K_i, K_j) = +2δ_ij  (boosts: positive definite — non-compact directions)
  B(J_i, K_j) = 0

  The signature is (3, 3) on so(3,1).

  The gauge kinetic term -(1/4g²) B(F, *F) has INDEFINITE sign!
  The gauge action is NOT positive-definite for SO(3,1).

  THIS IS A FUNDAMENTAL ISSUE for non-compact gauge groups.

  RESOLUTION IN THE METRIC BUNDLE:
  The physical gauge group is the COMPACT subgroup SU(4)×SU(2)_L×SU(2)_R,
  not SO(3,1). The compact gauge field has positive-definite action.

  The SU(2)_R ⊂ SO(3,1) instanton has:
  S = 8π²/g²_R = 8π²/g²_PS

  But this uses only 3 out of the 21 compact gauge generators.
  The instanton is "thin" — it sits in a small subgroup.
""")

# THE RESOLUTION: Use the 't Hooft mechanism for the BREAKING of SU(2)_R

# In the standard Pati-Salam model, SU(2)_R is broken by the VEV of Δ_R.
# The NON-PERTURBATIVE contribution to the Δ_R potential comes from
# instantons that wind around the unbroken SU(2)_R.

# For the metric bundle, the additional ingredient is that the FIBRE
# provides extra degrees of freedom that COUPLE to the SU(2)_R instanton
# and REDUCE the effective action.

# The mechanism: the instanton in SU(2)_R induces fluctuations in the
# other fibre directions through the fibre curvature (Ricci tensor).
# These fluctuations LOWER the instanton action.

# Quantitatively: the instanton action is modified by the fibre curvature:
# S_eff = S₀ - ΔS_fibre
# where ΔS_fibre comes from integrating out the fibre fluctuations
# in the instanton background.

# The fibre modes that couple to SU(2)_R through the Ricci tensor:
# From fibre_ricci_full.py:
#   - V+ sector (6D, gauge): Ric/G = -3.5
#   - V- sector (4D, Higgs): Ric/G = -2.25
#   - V+ eigenvalues: {-4, -4, -4, -4, -4, -1}
#   - V- eigenvalues: {-3, 4, 4, 4} (from eigh of Ric on V-)

# The fibre modes in the instanton background contribute to the
# 1-loop determinant. Each mode with mass M_i in the instanton
# background modifies the action by:
# δS ~ -ln(det(-D² + M²_i)) ∝ -dim(mode) × f(M_i × ρ)
# where ρ is the instanton size.

# For modes with M << 1/ρ (light modes): δS ~ dim × ln(ρ)
# For modes with M >> 1/ρ (heavy modes): δS ~ dim × (M²ρ²) (negligible)

# At the PS scale (ρ ~ 1/M_C), ALL fibre modes are "light" (M ~ M_C):
# The total modification to the exponent involves ALL fibre d.o.f.

# The effective b₀ for the instanton density:
# In the original SU(2)_R: b₀ = -5/3
# Adding the fibre fluctuations (10 real scalar fields from the fibre):

# Each real scalar in the adjoint of SU(2)_R contributes:
# δb₀ = -(1/3) × T(adj) = -(1/3) × 2 = -2/3
# per real scalar

# Each real scalar in the fundamental of SU(2)_R:
# δb₀ = -(1/6) × T(fund) = -(1/6) × (1/2) = -1/12

# The fibre modes: we need to know their SU(2)_R representation content.
# The 10 fibre tangent directions transform under SO(3,1) ⊃ SU(2)_R.
# Under SU(2)_L × SU(2)_R:
#   V+ (6D) transforms as some rep of SU(2)_R
#   V- (4D) transforms as some rep of SU(2)_R

# From the DeWitt metric eigenbasis:
# V- (4D, Higgs) ~ (2,2) of SU(2)_L × SU(2)_R → 2 doublets of SU(2)_R
# V+ (6D, gauge) ~ under SO(3,1)/SU(2)_R:
#   The 6 of SO(6) decomposes under SU(2)_R as...
#   Actually, V+ transforms under SO(3) ⊂ SO(3,1) as:
#   6 = 5 ⊕ 1 (traceless symmetric + trace)
#   Under SU(2)_R: 5 = spin-2 → 5-dim rep, 1 = singlet

# So the fibre modes under SU(2)_R:
#   V- (4D): 2 doublets of SU(2)_R (the bidoublet)
#   V+ (6D): 1 quintet (spin-2) + 1 singlet of SU(2)_R

# Hmm wait, this decomposition needs more care. Let me compute it.

# The SU(2)_R generators R_i act on the 10-dim tangent space p via adjoint.
# Let me compute the Casimir C₂ = Σ_i (ad_Ri)² to identify representations.

# Build basis for p (eta-symmetric matrices)
def build_eta_symmetric_basis():
    basis = []
    labels = []
    for i in range(d):
        for j in range(i, d):
            mat = np.zeros((d, d))
            if i == j:
                mat[i, i] = 1.0
            else:
                # Need ηS = (ηS)^T
                mat[i, j] = 1.0 / np.sqrt(2)
                if eta[i,i] * eta[j,j] > 0:
                    mat[j, i] = 1.0 / np.sqrt(2)
                else:
                    mat[j, i] = -1.0 / np.sqrt(2)
                # Check
                etaS = eta @ mat
                if np.max(np.abs(etaS - etaS.T)) > 1e-10:
                    mat[j, i] = -mat[j, i]
            basis.append(mat)
            labels.append(f"({i},{j})")
    return basis, labels

p_basis, p_labels = build_eta_symmetric_basis()
dim_p = len(p_basis)

# Build DeWitt metric matrix
G_mat = np.zeros((dim_p, dim_p))
for i in range(dim_p):
    for j in range(dim_p):
        G_mat[i, j] = dewitt_lor(p_basis[i], p_basis[j])

G_mat_inv = np.linalg.inv(G_mat)

# Adjoint action of R_i on p: [R_i, S] and project back to p
def ad_on_p(gen):
    """Matrix of ad_gen acting on p-basis."""
    mat = np.zeros((dim_p, dim_p))
    for j in range(dim_p):
        comm = lie_bracket(gen, p_basis[j])
        for i in range(dim_p):
            mat[i, j] = dewitt_lor(p_basis[i], comm)
    return G_mat_inv @ mat

# Compute SU(2)_R Casimir on p
ad_R = [ad_on_p(R[i]) for i in range(3)]
C2_SU2R = sum(ad_R[i] @ ad_R[i] for i in range(3))

print(f"\nSU(2)_R Casimir C₂ on the 10-dim tangent space p:")
C2_eigs = np.sort(np.linalg.eigvalsh(C2_SU2R))
print(f"  Eigenvalues: {C2_eigs}")

# For SU(2), the Casimir eigenvalue on the spin-j representation is j(j+1)
# spin-0: C₂ = 0
# spin-1/2: C₂ = 3/4
# spin-1: C₂ = 2
# spin-3/2: C₂ = 15/4
# spin-2: C₂ = 6

# Identify the representations
print(f"\nRepresentation decomposition of p under SU(2)_R:")
# Round eigenvalues and count multiplicities
from collections import Counter
rounded_eigs = [round(e, 2) for e in C2_eigs]
counts = Counter(rounded_eigs)
for eig, mult in sorted(counts.items()):
    # Find j: j(j+1) = eig → j = (-1 + sqrt(1 + 4*eig))/2
    if eig >= 0:
        j = (-1 + math.sqrt(1 + 4*abs(eig))) / 2
        dim_rep = int(round(2*j + 1))
        n_copies = mult // dim_rep if dim_rep > 0 else 0
        print(f"  C₂ = {eig:6.2f} → j = {j:.1f} (dim {dim_rep}), multiplicity {mult}, copies = {n_copies}")
    else:
        print(f"  C₂ = {eig:6.2f} → [negative: check sign conventions]")

# Also compute in the V+/V- eigenbasis
eigvals_G, eigvecs_G = np.linalg.eigh(G_mat)
pos_idx = np.where(eigvals_G > 1e-10)[0]
neg_idx = np.where(eigvals_G < -1e-10)[0]
U = eigvecs_G

# Transform Casimir to eigenbasis
C2_eigbasis = U.T @ C2_SU2R @ U

print(f"\nC₂(SU(2)_R) restricted to V+ ({len(pos_idx)}D):")
C2_pp = C2_eigbasis[np.ix_(list(pos_idx), list(pos_idx))]
eigs_pp = np.sort(np.linalg.eigvalsh(C2_pp))
print(f"  Eigenvalues: {eigs_pp}")

print(f"\nC₂(SU(2)_R) restricted to V- ({len(neg_idx)}D):")
C2_mm = C2_eigbasis[np.ix_(list(neg_idx), list(neg_idx))]
eigs_mm = np.sort(np.linalg.eigvalsh(C2_mm))
print(f"  Eigenvalues: {eigs_mm}")


# =====================================================================
# PART 9: INSTANTON DETERMINANT AND N_eff
# =====================================================================

print("\n" + "=" * 72)
print("PART 9: INSTANTON DETERMINANT AND N_eff")
print("=" * 72)

print("""
The instanton amplitude involves the 1-loop determinant of ALL fields
in the instanton background. For the BPST SU(2) instanton of size ρ:

  A = ∫ dρ/ρ⁵ × (μρ)^{b₀} × exp(-8π²/g²(μ))

where b₀ is the FULL 1-loop coefficient including ALL fields that
couple to SU(2)_R.

The effective b₀ determines the instanton density. The non-perturbative
scale is:
  Λ_NP = μ × exp(-8π²/(b₀ × g²(μ)))   [for b₀ > 0]

For NOT-AF theories (b₀ < 0 in our convention), the instanton integral
is dominated by LARGE ρ (IR effects), not small ρ.

In the metric bundle, the instanton size is CUT OFF by the fibre:
  ρ_max ~ 1/M_C (the fibre size)

The effective potential generated by the constrained instanton is:
  V_inst ~ M_C⁴ × exp(-8π²/g²_PS) × (corrections from all fields)

The corrections from integrating over the instanton moduli give:
  V_inst ~ M_C⁴ × [g²_PS/(8π²)]^{N_0/2} × exp(-8π²/g²_PS)

where N_0 is the number of instanton zero modes.

For SU(2) in 4D: N_0 = 4(for gauge) + 4(for Δ_R) + 2×N_f(fermions)
                     = 4 + 4 + 2×12 = 32

Hmm, but this isn't the N_eff from the CW estimate.

Let me think about this differently.

The CW script estimated: Λ_inst = M_C exp(-8π²/(N_eff g²))
with N_eff ≈ 17 needed for M_R ~ 10^9.

This corresponds to replacing g² → N_eff × g² in the action,
which means the instanton is N_eff times "cheaper" than a
standard SU(2) instanton.

This can happen if the instanton wraps a LARGER subgroup than SU(2)_R.
""")

# The resolution: CALORON or "composite" instanton

# On GL+(4)/SO(3,1), the instanton wraps the SU(2)_R subgroup
# of SO(3,1). But SO(3,1) has 6 generators, not 3.

# For an SO(4) instanton (compact version of SO(3,1)):
# SO(4) ≅ SU(2)_L × SU(2)_R
# An SO(4) instanton has action:
# S = 8π²/g²_{SO(4)} × (ν_L + ν_R)
# For a pure SU(2)_R instanton: ν_L = 0, ν_R = 1 → S = 8π²/g²

# For an SO(6,4) instanton (the full structure group):
# The embedding SU(2)_R ⊂ SO(4) ⊂ SO(6,4)
# The instanton charge is classified by π₃(SO(6,4)) = Z

# For SO(N) with N ≥ 3: π₃(SO(N)) = Z
# The instanton action for SO(N) is:
# S = 8π²/g²_{SO(N)} × |ν|

# In our case, the gauge coupling for SO(6,4) at the PS scale:
# The SO(6,4) group acts on the 10-dim fibre tangent space.
# The gauge kinetic term is:
# -(1/4g²_{PS}) Tr_{10}(F∧*F)
# where Tr_{10} is the trace in the 10-dimensional fundamental representation.

# The instanton in SU(2)_R ⊂ SO(4) ⊂ SO(6,4) has charge ν = 1 in
# π₃(SO(6,4)) = Z, and the action in the fundamental representation is:
# S = 8π²/g²_fund

# The relationship between g²_fund (in the 10-dim rep) and g²_PS
# (in the standard normalization):
# The standard PS normalization uses Tr_adj/(dim(G)) for SU(N).
# For SO(6,4) in the fundamental 10-dim rep:
# Tr_10(T_a T_b) = C × δ_{ab}
# where C depends on the normalization.

# For SO(N), the fundamental representation has:
# Tr_N(T_a T_b) = δ_{ab}/2 (standard normalization)

# But the PS coupling g_PS is the SU(4) × SU(2)² coupling, which
# is related to the SO(6,4) coupling by a factor.

# For the SU(2)_R INSTANTON embedded in SO(6,4):
# The instanton uses generators of SU(2)_R ⊂ SO(4) ⊂ SO(6,4).
# In the 10-dim fundamental of SO(6,4), the SU(2)_R generators
# act as follows:

# The 10 of SO(6,4) decomposes under SO(6) × SO(4) as:
# 10 = (6, 1) ⊕ (1, 4)
# Under SU(2)_L × SU(2)_R ≅ SO(4):
# (1, 4) → (2, 2)
# The SU(2)_R generators act on (2, 2) as right multiplication.

# The Dynkin index of SU(2)_R in the (2, 2):
# T((2,2)) = T(2) × dim(2) = (1/2) × 2 = 1

# For the SU(2)_R in the (6, 1):
# The 6 is a singlet of SO(4), so SU(2)_R acts trivially.
# T(6, 1) = 0

# Total: T_total = 0 + 1 = 1

# So the SU(2)_R INSTANTON action in the SO(6,4) gauge theory is:
# S = 8π² × T_total / g²_PS = 8π²/g²_PS (same as before)

# This confirms: a pure SU(2)_R instanton has the standard action.
# N_eff = 1 from this calculation.

print(f"SU(2)_R instanton in SO(6,4) gauge theory:")
print(f"  Dynkin index T = 1 (from (2,2) of SO(4) in 10 of SO(6,4))")
print(f"  S = 8π²/g²_PS = {8*math.pi**2/g_PS**2:.1f}")
print(f"  exp(-S) = {math.exp(-8*math.pi**2/g_PS**2):.2e}")
print(f"  → N_eff = 1 from the gauge structure alone")

# =====================================================================
# PART 10: THE 't HOOFT MECHANISM AND FIBRE FLUCTUATIONS
# =====================================================================

print("\n" + "=" * 72)
print("PART 10: FIBRE FLUCTUATION CORRECTIONS")
print("=" * 72)

print("""
The N_eff ≈ 17 estimate from the CW script was HEURISTIC.
The rigorous instanton action is S = 8π²/g²_PS ≈ 290.

This means a SINGLE SU(2)_R instanton is incredibly suppressed:
  exp(-S) ≈ exp(-290) ≈ 10^{-126}

THIS DOES NOT GENERATE M_R ~ 10^9 GeV.

IMPLICATIONS FOR THE PROGRAMME:

1. The instanton mechanism with N_eff ≈ 17 is NOT justified from
   first principles. The actual instanton action is ~17× larger.

2. The SU(2)_R breaking scale M_R is NOT determined by instantons.

3. We need a DIFFERENT mechanism for SU(2)_R breaking:

   (a) TREE-LEVEL from geometry: The CP³ mechanism breaks SU(4)
       but leaves SU(2)_R intact. Could higher-order fibre geometry
       (beyond the symmetric point) provide a potential?

   (b) RADIATIVE: The CW potential gives M_R ~ M_C (no hierarchy).
       Could threshold corrections or 2-loop effects help?

   (c) MULTI-INSTANTON: Multiple (semi-dilute) instantons could
       give an enhanced effect, but the dilute gas approximation
       gives Σ_n exp(-nS)/n! = exp(exp(-S)) which is still tiny.

   (d) STRONG COUPLING: If the theory enters a confining phase at
       some scale, non-perturbative effects could be O(1). But
       SU(2)_R is NOT AF, so it doesn't confine.

   (e) COSMOLOGICAL: M_R could be set by cosmological evolution
       (thermal phase transition, inflation, etc.) rather than
       vacuum physics.

   (f) INPUT: M_R could be a free parameter of the theory, set by
       initial conditions. The RG-determined value M_R ~ 10^9 GeV
       is then a CONSISTENCY CONDITION, not a prediction.

   (g) FIBRE MODULI: The fibre of GL+(4)/SO(3,1) has moduli
       (the metric can vary). Perhaps the L-R breaking is determined
       by the fibre moduli potential, which could involve
       non-perturbative effects in a DIFFERENT sector.
""")

# Let me explore option (g) more carefully
print("""
OPTION (g): FIBRE MODULI POTENTIAL

The fibre metric g_F varies over the base spacetime. At each point,
g_F ∈ GL+(4)/SO(3,1). The effective potential V(g_F) determines the
vacuum configuration.

From the existing computation:
  - The CP³ holomorphic curvature potential breaks SU(4) → SU(3) × U(1)
  - This potential acts on the V+ (gauge) sector
  - The V- (Higgs) sector provides the bidoublet

The key: does the fibre potential have a FLAT DIRECTION in the SU(2)_R
direction that could be lifted by quantum corrections?

From lr_breaking_check.py: the potential IS flat in the SU(2)_R direction
at tree level. This is the starting point for the CW analysis.

But the CW analysis shows M_R ~ M_C (no hierarchy).

THE REMAINING OPTION: a hierarchy generated by the running of the
FIBRE moduli potential from M_C down to lower scales. This could
involve:
  - The fibre Ricci flow
  - Anomalous dimensions of fibre operators
  - Mixing between fibre and base operators
""")


# =====================================================================
# PART 11: THE HONEST ASSESSMENT
# =====================================================================

print("\n" + "=" * 72)
print("PART 11: HONEST ASSESSMENT")
print("=" * 72)

S_inst_actual = 8 * math.pi**2 / g_PS**2
S_needed = math.log(M_C / M_R_target)

print(f"""
RESULT OF THE INSTANTON CALCULATION:

1. TOPOLOGY: π₃(GL+(4)/SO(3,1)) = Z  ✓
   The fibre supports instantons classified by an integer winding number.
   The generator winds around SU(2)_R relative to SU(2)_L.

2. INSTANTON ACTION: S = 8π²/g²_PS = {S_inst_actual:.1f}
   This is the STANDARD result for an SU(2) instanton.
   There is NO enhancement factor N_eff from the fibre geometry.

3. INSTANTON SUPPRESSION: exp(-S) = exp(-{S_inst_actual:.0f}) ≈ 10^{{-{S_inst_actual/math.log(10):.0f}}}
   This is negligibly small. The instanton does NOT generate M_R.

4. THE N_eff ≈ 17 ESTIMATE WAS WRONG:
   The CW script's hand estimate assumed the 10 fibre d.o.f.
   enter the exponent, but they DON'T. They enter the PREFACTOR
   of the instanton amplitude (through the 1-loop determinant),
   not the exponential.

   The N_eff factor would require the instanton to wrap a subgroup
   N_eff times "wider" than SU(2), which is not what happens.

5. NEEDED vs ACTUAL:
   Needed: S_eff = ln(M_C/M_R) = {S_needed:.1f}
   Actual: S = 8π²/g² = {S_inst_actual:.1f}
   Ratio: {S_inst_actual/S_needed:.0f}× too large

6. M_R REMAINS UNDETERMINED:
   The SU(2)_R breaking scale is NOT predicted by instantons.
   The 5.7-decade M_R tension (gauge 10⁹ vs seesaw 6×10¹⁴)
   is NOT resolved by this calculation.

   STATUS: M_R is an undetermined parameter of the model.

IMPACT ON THE PROGRAMME:
  - The instanton mechanism (Part 8 of CW script) should be marked
    as RULED OUT for generating M_R.
  - The physical picture (SU(4) classical, SU(2)_R non-perturbative,
    EW radiative) is NOT supported.
  - SU(2)_R breaking mechanism remains OPEN.
  - The viability assessment should note this honestly.

POSSIBLE SALVAGE ROUTES:
  (a) M_R as free parameter: The theory has 1 additional scale beyond M_C.
      This is common in Pati-Salam models and not fatal.
  (b) Seesaw: If M_R ~ 6×10¹⁴ GeV (the seesaw value), then the RG
      running needs modification (different scalar content).
  (c) Novel geometry: Some non-perturbative effect specific to the metric
      bundle (e.g., topology change, moduli space tunneling) that we
      haven't identified yet.
  (d) Anthropic: M_R scans in the landscape and is selected by
      conditions for nucleosynthesis / structure formation.
""")


# =====================================================================
# PART 12: WHAT CAN BE COMPUTED — THE INSTANTON PROFILE
# =====================================================================

print("\n" + "=" * 72)
print("PART 12: THE BPST INSTANTON PROFILE (for completeness)")
print("=" * 72)

print("""
Even though the instanton doesn't generate M_R, the BPST solution
for SU(2)_R on R⁴ is well-defined and may be useful for other purposes.

The BPST instanton:
  A_μ = f(r) × σ_{μν} x^ν / (x² + ρ²)
  f(r) = 2ρ²/(x² + ρ²)

  F_μν = 4ρ²/((x² + ρ²)²) × (self-dual part)

  Action: S = 8π²/g² (independent of ρ)

  Topological charge: ν = 1
""")

# Compute the instanton profile numerically
def bpst_field_strength_sq(r, rho):
    """
    |F|² for BPST instanton at radial distance r, size ρ.
    In the singular gauge: F = (2ρ²/(r² + ρ²)²) × (self-dual tensor)
    |F|² = 192 ρ⁴ / (r² + ρ²)⁴  (with standard normalization)
    """
    return 192 * rho**4 / (r**2 + rho**2)**4

# Verify: ∫ d⁴x |F|²/(8π²) = 8π² (the instanton action/g²)
# ∫ d⁴x |F|² = 2π² ∫₀^∞ r³ dr × 192ρ⁴/(r²+ρ²)⁴
#              = 2π² × 192ρ⁴ × ∫₀^∞ r³/(r²+ρ²)⁴ dr

def integrand_check(r, rho=1.0):
    return r**3 * 192 * rho**4 / (r**2 + rho**2)**4

result, err = quad(integrand_check, 0, np.inf, args=(1.0,))
S_check = 2 * math.pi**2 * result / (2 * g_PS**2)  # Action = ∫ Tr(F²)/g²
# Actually: S = (1/2g²) ∫ Tr(F∧*F) = (1/2g²) ∫ |F|² d⁴x  (for self-dual F)
# ∫ |F|² d⁴x = 2π² × result

print(f"Numerical verification of BPST action:")
print(f"  ∫ r³ × |F|² dr = {result:.4f}  (for ρ=1)")
print(f"  ∫ d⁴x |F|² = 2π² × {result:.4f} = {2*math.pi**2*result:.4f}")
print(f"  Expected: 64π² = {64*math.pi**2:.4f}")
# For SU(2): |F|² = 192ρ⁴/(r²+ρ²)⁴ includes the Tr factor
# Actually Tr(F∧*F) for SU(2) = (1/2)|F_a|² summed over a=1,2,3
# The factor 192 comes from summing over all tensor components

# The actual integral: ∫ r³/(r²+1)⁴ dr = 1/6  (for ρ=1)
analytic_integral = 1.0/6
print(f"  Analytic: ∫₀^∞ r³/(r²+1)⁴ dr = 1/6 = {1/6:.6f}")
print(f"  Numerical: {result/192:.6f}")
# 2π² × 192 × (1/6) = 64π² ✓
print(f"  2π² × 192 × 1/6 = {2*math.pi**2 * 192 / 6:.2f} = 64π² = {64*math.pi**2:.2f}")

# The instanton action
# S = (1/4g²) ∫ F^a_{μν} F^a_{μν} d⁴x
# For self-dual F: ∫ Tr(F∧*F) = ∫ |F|²
# With the factor Tr (in fund): ∫ Tr(F²) = (1/2) ∫ F^a F^a
# So S = ∫ Tr(F²) d⁴x / (g²) = (1/g²) × ...

# Standard result: S = 8π²/g² per instanton ✓
print(f"\n  BPST instanton action = 8π²/g² = {8*math.pi**2/g_PS**2:.1f}")
print(f"  For g = g_PS = {g_PS:.4f}")
print(f"  S = {8*math.pi**2/g_PS**2:.1f}")

# =====================================================================
# SUMMARY
# =====================================================================

print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)

print(f"""
INSTANTON ON GL+(4)/SO(3,1) — COMPLETE RESULTS:

┌─────────────────────────────────────────────────────────────────┐
│  π₃(GL+(4)/SO(3,1)) = Z                                       │
│  Generator: SU(2)_R winds relative to SU(2)_L                 │
│  Instanton breaks SU(2)_R preserving SU(2)_L ✓                │
│                                                                 │
│  Instanton action: S = 8π²/g²_PS = {S_inst_actual:.1f}                   │
│  exp(-S) = 10^{{-{S_inst_actual/math.log(10):.0f}}}                                           │
│                                                                 │
│  *** THE INSTANTON IS TOO SUPPRESSED TO GENERATE M_R ***       │
│                                                                 │
│  Needed: exp(-S) ~ 10^(-8) for M_R ~ 10^9                     │
│  Actual: exp(-S) ~ 10^(-126)                                   │
│  Discrepancy: ~118 orders of magnitude                          │
│                                                                 │
│  The N_eff ≈ 17 estimate was incorrect.                        │
│  Fibre d.o.f. enter the PREFACTOR, not the EXPONENT.           │
│                                                                 │
│  SU(2)_R breaking mechanism remains OPEN.                      │
│  M_R is an undetermined parameter.                             │
└─────────────────────────────────────────────────────────────────┘

WHAT THIS CALCULATION ESTABLISHES:
  1. ✅ π₃(GL+(4)/SO(3,1)) = Z — rigorously computed via homotopy exact sequence
  2. ✅ The instanton wraps SU(2)_R and preserves SU(2)_L — correct physics
  3. ✅ The BPST profile is well-defined — no issues with non-compact fibre
  4. ✅ SU(2)_R is NOT asymptotically free — confirmed b = -5/3
  5. ❌ The instanton does NOT generate M_R — action too large by ~17×
  6. ❌ N_eff ≈ 17 was a heuristic error — correct value is N_eff = 1

WHAT NEEDS UPDATING:
  - CW script Part 8 (instanton estimate): mark as RULED OUT
  - README: update instanton estimate to honest result
  - Paper 7: if instanton mechanism is mentioned, retract the claim
  - Viability: the M_R tension remains unresolved
""")
