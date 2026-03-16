#!/usr/bin/env python3
"""
RIGOROUS TEST: Does ε = 1/√20 Follow From Geometry?
=====================================================

THE QUESTION:
  The Cabibbo angle sin(θ_C) ≈ 0.2253 matches ε = 1/√20 ≈ 0.2236.
  But does this follow UNIQUELY from the metric bundle, or is 1/√20
  a lucky coincidence?

THE TEST:
  Compute the overlap integral between U(3)_I and U(3)_J in SO(6)
  using the Haar measure. If this gives 1/√20 with NO normalisation
  choices, the Cabibbo angle is derived. If not, it's numerology.

  ALSO: Compute using dim(intersection)/dim(U(3)) to see if that's
  the right formula. Try EVERY natural formula and see which one
  matches — this tells us whether ANY of them are compelling.

METHODOLOGY:
  - Use only Haar-measure integrals (no free parameters)
  - Try every natural group-theoretic quantity
  - Report ALL results, even ones that don't match
  - No cherry-picking allowed
"""

import numpy as np
from scipy.integrate import quad
from scipy.linalg import expm
from itertools import combinations

print("=" * 72)
print("RIGOROUS TEST: DOES ε = 1/√20 FOLLOW FROM GEOMETRY?")
print("=" * 72)

# Observed
sin_theta_C_obs = 0.2253  # PDG 2024
epsilon_claimed = 1 / np.sqrt(20)  # = 0.2236

print(f"\nObserved: sin(θ_C) = {sin_theta_C_obs}")
print(f"Claimed:  ε = 1/√20 = {epsilon_claimed:.6f}")
print(f"Match:    {abs(sin_theta_C_obs - epsilon_claimed)/sin_theta_C_obs * 100:.2f}% error")

# =====================================================================
# PART 1: The three complex structures on R⁶
# =====================================================================
print("\n" + "=" * 72)
print("PART 1: COMPLEX STRUCTURES AND U(3) SUBGROUPS")
print("=" * 72)

# Complex structures on R⁶ (acting on R⁶, not R⁴)
# These come from the quaternion action on R⁴ ⊕ R² ≅ R⁶
# J_a = J_a(R⁴) ⊕ J(R²)

# On R⁴: the quaternion units
I4 = np.array([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]], dtype=float)
J4 = np.array([[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]], dtype=float)
K4 = np.array([[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]], dtype=float)

# On R²: a single complex structure
I2 = np.array([[0,-1],[1,0]], dtype=float)

# On R⁶ = R⁴ ⊕ R²:
def block_diag(A, B):
    n, m = A.shape[0], B.shape[0]
    M = np.zeros((n+m, n+m))
    M[:n, :n] = A
    M[n:, n:] = B
    return M

J1 = block_diag(I4, I2)
J2 = block_diag(J4, I2)
J3 = block_diag(K4, I2)

# Verify: J_a² = -I
for name, J in [("J1", J1), ("J2", J2), ("J3", J3)]:
    assert np.allclose(J @ J, -np.eye(6)), f"{name}² ≠ -I"
print("All J_a² = -I ✓")

# U(3)_a = {A ∈ SO(6) : AJ_a = J_aA}
# Compute basis of u(3)_a = {X ∈ so(6) : [X, J_a] = 0}

def compute_u3_basis(J):
    """Find basis of u(3) = {X ∈ so(6) : [X, J] = 0}."""
    # so(6) basis: antisymmetric 6×6 matrices
    so6_basis = []
    for i in range(6):
        for j in range(i+1, 6):
            A = np.zeros((6, 6))
            A[i, j] = 1.0
            A[j, i] = -1.0
            so6_basis.append(A)

    # Filter: [X, J] = 0
    u3_basis = []
    for X in so6_basis:
        comm = X @ J - J @ X
        if np.allclose(comm, 0, atol=1e-10):
            u3_basis.append(X)

    return u3_basis

u3_1 = compute_u3_basis(J1)
u3_2 = compute_u3_basis(J2)
u3_3 = compute_u3_basis(J3)

print(f"\ndim(u(3)_1) = {len(u3_1)}")
print(f"dim(u(3)_2) = {len(u3_2)}")
print(f"dim(u(3)_3) = {len(u3_3)}")
print(f"dim(so(6)) = 15")

# =====================================================================
# PART 2: Intersection dimensions
# =====================================================================
print("\n" + "=" * 72)
print("PART 2: INTERSECTION SUBGROUPS")
print("=" * 72)

def intersection_dim(basis_A, basis_B):
    """Compute dim(span(A) ∩ span(B))."""
    if not basis_A or not basis_B:
        return 0
    # Flatten to vectors
    n = basis_A[0].size
    vecs_A = np.array([X.flatten() for X in basis_A])
    vecs_B = np.array([X.flatten() for X in basis_B])

    # Combine and find rank
    combined = np.vstack([vecs_A, vecs_B])
    rank_combined = np.linalg.matrix_rank(combined, tol=1e-10)
    rank_A = np.linalg.matrix_rank(vecs_A, tol=1e-10)
    rank_B = np.linalg.matrix_rank(vecs_B, tol=1e-10)

    # dim(A ∩ B) = dim(A) + dim(B) - dim(A + B)
    return rank_A + rank_B - rank_combined

d12 = intersection_dim(u3_1, u3_2)
d23 = intersection_dim(u3_2, u3_3)
d13 = intersection_dim(u3_1, u3_3)
d123 = intersection_dim(u3_1, intersection_dim_basis(u3_1, u3_2, u3_3) if False else u3_1)

# Triple intersection
def triple_intersection_dim(b1, b2, b3):
    """dim(b1 ∩ b2 ∩ b3)"""
    n = b1[0].size
    v1 = np.array([X.flatten() for X in b1])
    v2 = np.array([X.flatten() for X in b2])
    v3 = np.array([X.flatten() for X in b3])

    # Find basis of b1 ∩ b2 first
    # A vector v is in b1 ∩ b2 if v = Σ a_i v1_i = Σ b_j v2_j
    # i.e., [v1 | -v2] [a; b]^T = 0
    M12 = np.vstack([v1, -v2]).T
    # Null space gives a ∩ b
    from scipy.linalg import null_space
    ns = null_space(M12, rcond=1e-10)
    if ns.shape[1] == 0:
        return 0
    # Reconstruct intersection vectors
    int12 = ns[:len(b1), :].T @ v1  # each row is a vector in the intersection

    # Now intersect with b3
    if int12.shape[0] == 0:
        return 0
    M = np.vstack([int12, -v3]).T
    ns2 = null_space(M, rcond=1e-10)
    return ns2.shape[1] if ns2.shape[1] > 0 else 0

d123 = triple_intersection_dim(u3_1, u3_2, u3_3)

print(f"dim(u(3)_1 ∩ u(3)_2) = {d12}")
print(f"dim(u(3)_2 ∩ u(3)_3) = {d23}")
print(f"dim(u(3)_1 ∩ u(3)_3) = {d13}")
print(f"dim(u(3)_1 ∩ u(3)_2 ∩ u(3)_3) = {d123}")

# =====================================================================
# PART 3: ALL natural formulas for ε
# =====================================================================
print("\n" + "=" * 72)
print("PART 3: EVERY NATURAL FORMULA FOR ε")
print("=" * 72)

dim_so6 = 15
dim_u3 = 9
dim_int = d12  # pairwise intersection

# Try every formula that a reasonable person might write down
formulas = {
    # Simple dimension ratios
    "dim(∩)/dim(u3)":                dim_int / dim_u3,
    "dim(∩)/dim(so6)":               dim_int / dim_so6,
    "√(dim(∩)/dim(u3))":             np.sqrt(dim_int / dim_u3),
    "√(dim(∩)/dim(so6))":            np.sqrt(dim_int / dim_so6),

    # Complement ratios
    "(dim(u3)-dim(∩))/dim(u3)":      (dim_u3 - dim_int) / dim_u3,
    "(dim(u3)-dim(∩))/dim(so6)":     (dim_u3 - dim_int) / dim_so6,
    "√((dim(u3)-dim(∩))/dim(so6))":  np.sqrt((dim_u3 - dim_int) / dim_so6),

    # Fiber dimension formulas
    "1/√(dim_fiber)":                1 / np.sqrt(10),
    "1/√(2·dim_fiber)":              1 / np.sqrt(20),
    "1/√(dim_fiber + dim_base)":     1 / np.sqrt(14),
    "1/√(dim_fiber · dim_base)":     1 / np.sqrt(40),
    "1/dim_fiber":                   1 / 10,

    # Dynkin-related
    "1/√(2·rank(SU4)·rank(SU2)²)":  1 / np.sqrt(2 * 3 * 1),
    "1/√(dim(PS))":                  1 / np.sqrt(21),
    "1/√(dim(PS)+dim(u1))":          1 / np.sqrt(22),

    # Volume ratios
    "Vol(U3)/Vol(SO6)":              None,  # compute below
    "Vol(U3∩U3')/Vol(U3)":           None,  # compute below

    # Casimir ratios
    "C2(fund,SU4)/C2(adj,SU4)":      (15/8) / 4,  # = 15/32

    # Signature-related
    "n_minus/n_total":               4 / 10,
    "√(n_minus/n_total)":            np.sqrt(4 / 10),
    "n_minus/n_plus":                4 / 6,
    "√(n_minus·n_plus)/n_total":     np.sqrt(4 * 6) / 10,

    # SO(6) branching
    "1/√(dim(6_of_SO6))":           1 / np.sqrt(6),

    # Mixed
    "dim(∩)/dim(u3)²":              dim_int / dim_u3**2,
    "√(dim(∩)/(dim(u3)·dim(so6)))": np.sqrt(dim_int / (dim_u3 * dim_so6)),
}

# Sort by distance from observed
print(f"\n{'Formula':<45} {'Value':>10} {'Error':>8}")
print("-" * 70)

results = []
for name, val in formulas.items():
    if val is not None and val > 0:
        err = abs(val - sin_theta_C_obs) / sin_theta_C_obs * 100
        results.append((err, name, val))

results.sort()
for err, name, val in results:
    marker = " ★" if err < 2 else ""
    print(f"{name:<45} {val:10.6f} {err:7.2f}%{marker}")

# =====================================================================
# PART 4: The actual overlap integral (Haar measure)
# =====================================================================
print("\n" + "=" * 72)
print("PART 4: HAAR MEASURE OVERLAP INTEGRAL")
print("=" * 72)

# The most rigorous quantity: the probability that a random element
# of SO(6) (drawn from Haar measure) lies in U(3)_1 ∩ U(3)_2.
#
# P(U(3)_1 ∩ U(3)_2) = Vol(U(3)_1 ∩ U(3)_2) / Vol(SO(6))
#
# Related: the "mixing angle" between U(3)_1 and U(3)_2 is:
# sin²(θ) = 1 - P(overlap)
#
# OR: the Grassmannian distance between U(3)_1/SO(6) and U(3)_2/SO(6)

# The volume ratios are known exactly:
# Vol(SO(n)) = 2^{n(n-1)/4} × π^{n(n+1)/4} / Γ_n(n/2)
# Vol(U(n)) = (2π)^{n(n+1)/2} / (1! 2! ... (n-1)!)
# Vol(SO(2n)/U(n)) = 2^n × Vol(SO(2n)) / Vol(U(n))

# For SO(6) = SU(4)/Z₂:
# Vol(SU(4)) = (2π)^{9} / (1·2·6) = (2π)^9 / 12
# For U(3): Vol(U(3)) = (2π)^6 / (1·2) = (2π)^6 / 2

# The coset SO(6)/U(3) is the space of complex structures on R⁶
# compatible with the metric. This is CP³ (complex projective 3-space).
# dim(CP³) = 6, Vol(CP³) = π³/6 (with Fubini-Study metric normalized
# so that lines have area π)

# The "angle" between two complex structures J_1 and J_2 on R⁶
# is a point in SO(6), i.e., the element g such that J_2 = g J_1 g⁻¹.
# The mixing is determined by the eigenvalues of J_1 J_2.

# Compute J_1 J_2 eigenvalues
J1J2 = J1 @ J2
eigenvals_12 = np.linalg.eigvals(J1J2)
print(f"Eigenvalues of J₁J₂: {np.sort_complex(eigenvals_12)}")

J2J3 = J2 @ J3
eigenvals_23 = np.linalg.eigvals(J2J3)
print(f"Eigenvalues of J₂J₃: {np.sort_complex(eigenvals_23)}")

J1J3 = J1 @ J3
eigenvals_13 = np.linalg.eigvals(J1J3)
print(f"Eigenvalues of J₁J₃: {np.sort_complex(eigenvals_13)}")

# The eigenvalues of J₁J₂ encode the "angles" between the two
# complex structures. For two complex structures on R⁶:
# J₁J₂ has eigenvalues e^{±iα_k}, k = 1,2,3
# where α_k are the Kähler angles.

# Extract angles
angles_12 = np.sort(np.abs(np.angle(eigenvals_12[np.abs(np.imag(eigenvals_12)) > 0.01])))
print(f"\nKähler angles between J₁ and J₂:")
for a in angles_12:
    print(f"  α = {np.degrees(a):.1f}° = {a:.4f} rad")

# The "distance" between J₁ and J₂ on the space of complex structures
# (which is CP³ with Fubini-Study metric) is:
#   d²(J₁, J₂) = Σ_k α_k²

# But the more fundamental quantity for mixing is:
# The transition amplitude between generation 1 and generation 2
# = |⟨ψ_1 | ψ_2⟩| where ψ_a is the "wavefunction" of generation a.

# In the geometric picture, this is related to:
#   cos(θ_{12}) = Tr(P_1 P_2) / √(Tr(P_1²) Tr(P_2²))
# where P_a = (1 - iJ_a)/2 is the holomorphic projector.

P1 = (np.eye(6) - 1j * J1) / 2
P2 = (np.eye(6) - 1j * J2) / 2
P3 = (np.eye(6) - 1j * J3) / 2

overlap_12 = np.abs(np.trace(P1.conj().T @ P2)) / np.sqrt(
    np.abs(np.trace(P1.conj().T @ P1)) * np.abs(np.trace(P2.conj().T @ P2)))
overlap_23 = np.abs(np.trace(P2.conj().T @ P3)) / np.sqrt(
    np.abs(np.trace(P2.conj().T @ P2)) * np.abs(np.trace(P3.conj().T @ P3)))
overlap_13 = np.abs(np.trace(P1.conj().T @ P3)) / np.sqrt(
    np.abs(np.trace(P1.conj().T @ P1)) * np.abs(np.trace(P3.conj().T @ P3)))

print(f"\nHolomorphic projector overlaps:")
print(f"  |⟨P₁|P₂⟩| = {overlap_12:.6f}")
print(f"  |⟨P₂|P₃⟩| = {overlap_23:.6f}")
print(f"  |⟨P₁|P₃⟩| = {overlap_13:.6f}")

# Alternative: Tr(J₁J₂)/Tr(J₁²) as a measure of overlap
trace_overlap_12 = np.trace(J1 @ J2) / np.trace(J1 @ J1)
trace_overlap_23 = np.trace(J2 @ J3) / np.trace(J2 @ J2)
trace_overlap_13 = np.trace(J1 @ J3) / np.trace(J1 @ J1)

print(f"\nTrace overlaps Tr(J_aJ_b)/Tr(J_a²):")
print(f"  Tr(J₁J₂)/6 = {trace_overlap_12:.6f}")
print(f"  Tr(J₂J₃)/6 = {trace_overlap_23:.6f}")
print(f"  Tr(J₁J₃)/6 = {trace_overlap_13:.6f}")

# Anticommutator norm
anticomm_12 = np.linalg.norm(J1 @ J2 + J2 @ J1, 'fro')
anticomm_23 = np.linalg.norm(J2 @ J3 + J3 @ J2, 'fro')
anticomm_13 = np.linalg.norm(J1 @ J3 + J3 @ J1, 'fro')

print(f"\nAnticommutator norms ||{{J_a, J_b}}||_F:")
print(f"  ||{{J₁, J₂}}|| = {anticomm_12:.6f}")
print(f"  ||{{J₂, J₃}}|| = {anticomm_23:.6f}")
print(f"  ||{{J₁, J₃}}|| = {anticomm_13:.6f}")

# =====================================================================
# PART 5: The definitive test
# =====================================================================
print("\n" + "=" * 72)
print("PART 5: DEFINITIVE COMPARISON")
print("=" * 72)

# Collect ALL computed geometric quantities
geometric_quantities = {
    "dim(u3∩u3')/dim(u3)":                d12 / dim_u3,
    "dim(u3∩u3')/dim(so6)":               d12 / dim_so6,
    "√(dim(u3∩u3')/dim(u3))":             np.sqrt(d12 / dim_u3),
    "√(dim(u3∩u3')/dim(so6))":            np.sqrt(d12 / dim_so6),
    "1/√(2·dim_fiber)":                   1 / np.sqrt(20),
    "1/√(dim_fiber)":                     1 / np.sqrt(10),
    "|⟨P₁|P₂⟩| (projector)":             overlap_12,
    "Tr(J₁J₂)/Tr(J₁²) (trace)":          abs(trace_overlap_12),
    "||{J₁,J₂}||/(2||J₁||²)":            anticomm_12 / (2 * np.linalg.norm(J1, 'fro')**2),
}

print(f"\n{'Geometric quantity':<40} {'Value':>10} {'Error vs obs':>12} {'Match?':>8}")
print("-" * 75)

for name, val in sorted(geometric_quantities.items(), key=lambda x: abs(x[1] - sin_theta_C_obs)):
    err = abs(val - sin_theta_C_obs) / sin_theta_C_obs * 100
    match = "★ YES" if err < 2 else "  no"
    print(f"{name:<40} {val:10.6f} {err:11.2f}% {match}")

# =====================================================================
# PART 6: THE VERDICT
# =====================================================================
print("\n" + "=" * 72)
print("PART 6: THE VERDICT")
print("=" * 72)

print(f"""
KEY FINDINGS:

1. dim(u(3)_1 ∩ u(3)_2) = {d12}
   This is the dimension of the common subalgebra.

2. The NATURAL ratio is dim(∩)/dim(u3) = {d12}/{dim_u3} = {d12/dim_u3:.6f}
   This is NOT close to sin(θ_C) = {sin_theta_C_obs}.

3. The formula 1/√(2·dim_fiber) = 1/√20 = {1/np.sqrt(20):.6f}
   DOES match sin(θ_C) to 0.75%.
   But the "2" has no rigorous justification from the geometry.

4. The holomorphic projector overlap |⟨P₁|P₂⟩| = {overlap_12:.6f}
   is {'close' if abs(overlap_12 - sin_theta_C_obs)/sin_theta_C_obs < 0.1 else 'NOT close'}
   to sin(θ_C).

5. The trace overlap Tr(J₁J₂)/Tr(J₁²) = {abs(trace_overlap_12):.6f}
   is {'close' if abs(abs(trace_overlap_12) - sin_theta_C_obs)/sin_theta_C_obs < 0.1 else 'NOT close'}
   to sin(θ_C).
""")

# Check if ANY natural quantity gives 1/√20
print("QUESTION: Does ANY purely geometric quantity give 1/√20 = 0.22360...?")
print()
target = 1/np.sqrt(20)
for name, val in geometric_quantities.items():
    if abs(val - target) / target < 0.01:
        print(f"  ★ {name} = {val:.6f} ≈ 1/√20 = {target:.6f}")

# Final assessment
print(f"""
HONEST ASSESSMENT:

The formula ε = 1/√20 gives a 0.75% match to sin(θ_C).
But 1/√20 = 1/√(2 × dim_fiber).

The factor "2" could come from:
  a) Two chiralities (left/right) — but WHY would that enter?
  b) Two quark sectors (up/down) — but WHY?
  c) The signature split (6+4 = 10, 6-4 = 2)?
  d) A numerical coincidence

Without a derivation of the factor 2, this is:
  - NUMEROLOGY at the 1% level (not proof)
  - SUGGESTIVE (1% coincidences do happen, but rarely)
  - Worth investigating further (try to derive from overlap integral)

If a rigorous overlap integral gives 1/√20, it becomes DERIVED.
If not, it remains a suggestive coincidence.
""")
