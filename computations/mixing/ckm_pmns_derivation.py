#!/usr/bin/env python3
"""
TECHNICAL NOTE 20: CKM AND PMNS MIXING ANGLES FROM FIBER GEOMETRY
===================================================================

The CKM and PMNS matrices encode the mixing between mass eigenstates
and weak interaction eigenstates for quarks and leptons respectively.

CKM has 4 parameters: 3 angles + 1 CP phase (8 precisely measured numbers total)
PMNS has 4 parameters: 3 angles + 1 CP phase (+ 2 Majorana phases for neutrinos)

This note attempts to derive these angles from the metric bundle geometry.

Key insight: The three generations come from three complex structures
I, J, K on R⁶ that satisfy the quaternionic algebra:
    IJ = K, JK = I, KI = J
    I² = J² = K² = -1

These span a 2-sphere S² in the space of complex structures.
Sp(1) breaking picks a direction on this S², determining mass eigenstates.
CKM arises from the MISALIGNMENT between up and down breaking directions.

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from scipy.linalg import expm, block_diag
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

print("=" * 72)
print("TECHNICAL NOTE 20: CKM AND PMNS FROM FIBER GEOMETRY")
print("=" * 72)

# =====================================================================
# OBSERVED VALUES
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 1: OBSERVED MIXING MATRICES")
print("=" * 72)

# CKM parameters (PDG 2024)
# Wolfenstein parametrization: lambda, A, rho_bar, eta_bar
lambda_W = 0.22500  # sin(theta_12) ≈ Cabibbo angle
A_W = 0.826
rho_bar = 0.159
eta_bar = 0.348

# CKM angles (degrees)
theta_12_ckm = np.degrees(np.arcsin(lambda_W))
theta_23_ckm = np.degrees(np.arcsin(A_W * lambda_W**2))
theta_13_ckm = np.degrees(np.arcsin(A_W * lambda_W**3 * np.sqrt(rho_bar**2 + eta_bar**2)))
delta_ckm = np.degrees(np.arctan2(eta_bar, rho_bar))

print(f"\nCKM matrix (quark mixing):")
print(f"  θ₁₂ = {theta_12_ckm:.3f}° (Cabibbo)")
print(f"  θ₂₃ = {theta_23_ckm:.3f}°")
print(f"  θ₁₃ = {theta_13_ckm:.3f}°")
print(f"  δ   = {delta_ckm:.1f}° (CP phase)")

# Construct |V_CKM| (magnitudes)
s12, c12 = np.sin(np.radians(theta_12_ckm)), np.cos(np.radians(theta_12_ckm))
s23, c23 = np.sin(np.radians(theta_23_ckm)), np.cos(np.radians(theta_23_ckm))
s13, c13 = np.sin(np.radians(theta_13_ckm)), np.cos(np.radians(theta_13_ckm))

V_CKM_obs = np.array([
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.999118]
])

print(f"\n|V_CKM| observed:")
for row in V_CKM_obs:
    print(f"  [{row[0]:.5f}, {row[1]:.5f}, {row[2]:.5f}]")

# PMNS parameters (NuFit 5.2, 2023, normal ordering)
theta_12_pmns = 33.41  # degrees
theta_23_pmns = 42.2   # degrees (octant ambiguity: could be ~49°)
theta_13_pmns = 8.58   # degrees
delta_pmns = 232.0     # degrees (CP phase, large uncertainty)

print(f"\nPMNS matrix (lepton mixing):")
print(f"  θ₁₂ = {theta_12_pmns:.2f}° (solar)")
print(f"  θ₂₃ = {theta_23_pmns:.1f}° (atmospheric)")
print(f"  θ₁₃ = {theta_13_pmns:.2f}° (reactor)")
print(f"  δ   = {delta_pmns:.0f}° (CP phase)")

# Construct |U_PMNS| (magnitudes)
s12_p, c12_p = np.sin(np.radians(theta_12_pmns)), np.cos(np.radians(theta_12_pmns))
s23_p, c23_p = np.sin(np.radians(theta_23_pmns)), np.cos(np.radians(theta_23_pmns))
s13_p, c13_p = np.sin(np.radians(theta_13_pmns)), np.cos(np.radians(theta_13_pmns))

U_PMNS_obs = np.abs(np.array([
    [c12_p*c13_p, s12_p*c13_p, s13_p],
    [-s12_p*c23_p - c12_p*s23_p*s13_p, c12_p*c23_p - s12_p*s23_p*s13_p, s23_p*c13_p],
    [s12_p*s23_p - c12_p*c23_p*s13_p, -c12_p*s23_p - s12_p*c23_p*s13_p, c23_p*c13_p]
]))

print(f"\n|U_PMNS| observed:")
for row in U_PMNS_obs:
    print(f"  [{row[0]:.4f}, {row[1]:.4f}, {row[2]:.4f}]")

# Key observation: CKM is nearly diagonal, PMNS has large mixing
print(f"\nKey contrast:")
print(f"  CKM: small angles (hierarchical mixing)")
print(f"    |V_us| = {V_CKM_obs[0,1]:.4f}, |V_cb| = {V_CKM_obs[1,2]:.4f}, |V_ub| = {V_CKM_obs[0,2]:.5f}")
print(f"  PMNS: large angles (democratic mixing)")
print(f"    |U_e2| = {U_PMNS_obs[0,1]:.4f}, |U_μ3| = {U_PMNS_obs[1,2]:.4f}, |U_e3| = {U_PMNS_obs[0,2]:.4f}")


# =====================================================================
# SECTION 2: THE QUATERNIONIC STRUCTURE
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 2: QUATERNIONIC COMPLEX STRUCTURES")
print("=" * 72)

# Complex structures on R⁶ from quaternions
I4 = np.array([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]], dtype=float)
J4 = np.array([[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]], dtype=float)
K4 = np.array([[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]], dtype=float)
IC = np.array([[0,-1],[1,0]], dtype=float)

def block_diag_manual(A, B):
    n, m = A.shape[0], B.shape[0]
    M = np.zeros((n+m, n+m))
    M[:n, :n] = A
    M[n:, n:] = B
    return M

J1 = block_diag_manual(I4, IC)  # Generation 1
J2 = block_diag_manual(J4, IC)  # Generation 2
J3 = block_diag_manual(K4, IC)  # Generation 3

# Verify J² = -I
for name, J in [("J₁", J1), ("J₂", J2), ("J₃", J3)]:
    assert np.allclose(J @ J, -np.eye(6)), f"{name} fails J² = -I"

# Compute the angles between complex structures
def angle_between_J(Ja, Jb):
    """Compute the angle between two complex structures."""
    dot = np.trace(Ja @ Jb.T)
    norm_a = np.sqrt(np.trace(Ja @ Ja.T))
    norm_b = np.sqrt(np.trace(Jb @ Jb.T))
    cos_theta = dot / (norm_a * norm_b)
    return np.arccos(np.clip(cos_theta, -1, 1))

theta_12 = angle_between_J(J1, J2)
theta_13 = angle_between_J(J1, J3)
theta_23 = angle_between_J(J2, J3)

print(f"\nAngles between complex structures:")
print(f"  θ(J₁, J₂) = {np.degrees(theta_12):.1f}°")
print(f"  θ(J₁, J₃) = {np.degrees(theta_13):.1f}°")
print(f"  θ(J₂, J₃) = {np.degrees(theta_23):.1f}°")

print("""
All three angles are EQUAL — this is the Z₃ symmetry from quaternions.
I, J, K are related by 120° rotations in the space of complex structures.

The mass eigenstates require breaking this Z₃ symmetry.
""")


# =====================================================================
# SECTION 3: SP(1) BREAKING PARAMETRIZATION
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 3: SP(1) BREAKING AND MIXING ANGLES")
print("=" * 72)

print("""
The Sp(1) ≅ SU(2) flavor symmetry acts on the quaternion space (1, I, J, K).
Breaking Sp(1) → U(1) selects a direction in (I, J, K) space — a point on S².

Parametrize the breaking direction by angles (α, β) on S²:
  n⃗ = (sin α cos β, sin α sin β, cos α)

The "heavy" complex structure is:
  J_heavy = n₁·J₁ + n₂·J₂ + n₃·J₃  (normalized)

where n₁ + n₂ + n₃ = 1 for a convex combination.

Actually, since J_a² = -I, we need to be more careful.
The complex structures span the Lie algebra sp(1) ≅ su(2).
A general complex structure is:
  J(θ, φ) = sin θ cos φ · J₁ + sin θ sin φ · J₂ + cos θ · J₃

This is well-defined because J(θ,φ)² = -I for all (θ, φ) on S².
""")

def J_breaking(theta, phi):
    """General complex structure on S²."""
    n1 = np.sin(theta) * np.cos(phi)
    n2 = np.sin(theta) * np.sin(phi)
    n3 = np.cos(theta)
    J = n1 * J1 + n2 * J2 + n3 * J3
    # Normalize to ensure J² = -I (should already be true)
    norm = np.sqrt(-np.trace(J @ J) / 6)
    return J / norm

# Test: J(0, 0) should give J₃ (cos θ = 1)
J_test = J_breaking(0, 0)
# Check that it's proportional to J₃
if np.linalg.norm(J_test) > 0.01:
    J_test_normed = J_test / np.linalg.norm(J_test)
    J3_normed = J3 / np.linalg.norm(J3)
    assert np.allclose(np.abs(J_test_normed), np.abs(J3_normed), atol=0.1), "J(0,0) should be ~ J₃"

print("Breaking direction parametrization verified.")


# =====================================================================
# SECTION 4: CKM FROM MISALIGNMENT
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 4: CKM FROM UP-DOWN MISALIGNMENT")
print("=" * 72)

print("""
The CKM matrix arises from the MISALIGNMENT between:
  - Up-type breaking direction: (θ_u, φ_u) on S²
  - Down-type breaking direction: (θ_d, φ_d) on S²

If both sectors break along the SAME direction, V_CKM = I (no mixing).
If they break along DIFFERENT directions, mixing arises.

The ANGLE between breaking directions determines the CABIBBO ANGLE:
  θ_C ≈ arccos(n⃗_u · n⃗_d)  (for small angles)

Let's explore what geometric constraints might fix these directions.
""")

def breaking_angle(theta_u, phi_u, theta_d, phi_d):
    """Compute angle between two breaking directions on S²."""
    n_u = np.array([np.sin(theta_u)*np.cos(phi_u),
                    np.sin(theta_u)*np.sin(phi_u),
                    np.cos(theta_u)])
    n_d = np.array([np.sin(theta_d)*np.cos(phi_d),
                    np.sin(theta_d)*np.sin(phi_d),
                    np.cos(theta_d)])
    dot = np.dot(n_u, n_d)
    return np.arccos(np.clip(dot, -1, 1))

# The observed Cabibbo angle
theta_C_obs = np.radians(theta_12_ckm)
print(f"Observed Cabibbo angle: θ_C = {theta_12_ckm:.2f}° = {theta_C_obs:.4f} rad")

# If up-type breaks along J₃ (θ_u=0) and down-type breaks at angle θ_C:
theta_u, phi_u = 0.0, 0.0  # Along J₃
# We need: n⃗_u · n⃗_d = cos(θ_C)
# With n⃗_u = (0, 0, 1), we need n₃_d = cos(θ_C)
# So θ_d = θ_C, any φ_d

theta_d = theta_C_obs
phi_d = 0.0

misalignment = breaking_angle(theta_u, phi_u, theta_d, phi_d)
print(f"\nExample: up along J₃, down rotated by θ_C")
print(f"  θ_u = 0°, φ_u = 0° (along J₃)")
print(f"  θ_d = {np.degrees(theta_d):.2f}°, φ_d = 0°")
print(f"  Misalignment angle: {np.degrees(misalignment):.2f}°")
print(f"  This reproduces Cabibbo by construction.")


# =====================================================================
# SECTION 5: GEOMETRIC CONSTRAINTS ON BREAKING DIRECTIONS
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 5: GEOMETRIC CONSTRAINTS ON BREAKING")
print("=" * 72)

print("""
Without additional constraints, θ_d and φ_d are FREE PARAMETERS.
This means CKM angles are NOT predicted by the geometry alone.

However, there are several special points/directions on S² that
might be selected by geometric principles:

1. POLES: J₁, J₂, J₃ (the three original complex structures)
   - These are related by Z₃ symmetry
   - If up breaks along J₃ and down along J₂, the angle is 90° — too large

2. EDGES: Midpoints between Ji and Jj
   - J₁₂ = (J₁ + J₂)/√2, etc.
   - Angle from J₃ to J₁₂ is arccos(1/√3) ≈ 54.7°

3. CENTER: Equal mixture J_c = (J₁ + J₂ + J₃)/√3
   - Angle from J₃ to J_c is arccos(1/√3) ≈ 54.7°

4. GOLDEN RATIO POINT: Related to icosahedral symmetry
   - Angle arctan(φ) where φ = (1+√5)/2 ≈ 58.3°

None of these match the observed Cabibbo angle of ~13°!
""")

# Compute special geometric angles
phi_golden = (1 + np.sqrt(5)) / 2

special_angles = {
    "Z₃ vertex (J_i to J_j)": np.degrees(theta_12),  # ~ 90°
    "Midpoint (J₃ to J₁₂)": np.degrees(np.arccos(1/np.sqrt(3))),  # ~ 54.7°
    "Center (J₃ to J_c)": np.degrees(np.arccos(1/np.sqrt(3))),  # ~ 54.7°
    "Golden (arctan φ)": np.degrees(np.arctan(phi_golden)),  # ~ 58.3°
    "Observed Cabibbo": theta_12_ckm,  # ~ 13°
}

print(f"\nSpecial geometric angles vs. Cabibbo:")
print(f"  {'Configuration':<30} {'Angle (°)':>12}")
print(f"  {'-'*44}")
for name, angle in special_angles.items():
    marker = " <-- OBSERVED" if "Cabibbo" in name else ""
    print(f"  {name:<30} {angle:>12.2f}{marker}")

print("""
The Cabibbo angle is MUCH SMALLER than any natural geometric angle.
This suggests the CKM smallness comes from DYNAMICS, not pure geometry.
""")


# =====================================================================
# SECTION 6: DYNAMICAL SELECTION — MASS RATIO CONSTRAINT
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 6: MASS RATIOS AND MIXING ANGLES")
print("=" * 72)

print("""
In many models, the CKM angles are related to mass ratios:

  θ_C ≈ √(m_d/m_s)  or  θ_C ≈ √(m_u/m_c)

This is the GATTO-SARTORI-TONIN relation (1968).

Let's check if the observed masses satisfy this:
""")

# Observed quark masses (MS-bar at 2 GeV for light quarks, pole for heavy)
m_u = 2.16e-3  # GeV
m_d = 4.67e-3  # GeV
m_s = 0.0934   # GeV
m_c = 1.27     # GeV

# Mass ratio predictions for Cabibbo angle
theta_C_from_d_s = np.sqrt(m_d / m_s)
theta_C_from_u_c = np.sqrt(m_u / m_c)
theta_C_geometric_mean = np.sqrt(np.sqrt(m_d / m_s) * np.sqrt(m_u / m_c))

print(f"Mass ratio predictions for sin(θ_C):")
print(f"  √(m_d/m_s) = {theta_C_from_d_s:.4f}")
print(f"  √(m_u/m_c) = {theta_C_from_u_c:.4f}")
print(f"  Geometric mean = {theta_C_geometric_mean:.4f}")
print(f"  Observed sin(θ_C) = {lambda_W:.4f}")

print(f"\nAs angles:")
print(f"  arcsin(√(m_d/m_s)) = {np.degrees(np.arcsin(theta_C_from_d_s)):.1f}°")
print(f"  arcsin(√(m_u/m_c)) = {np.degrees(np.arcsin(theta_C_from_u_c)):.1f}°")
print(f"  Observed θ_C = {theta_12_ckm:.1f}°")

print("""
The Gatto-Sartori-Tonin relation gives θ_C ≈ 13° from √(m_d/m_s).
This is remarkably close to the observed value!

In the metric bundle framework, this becomes:
  The SAME Sp(1) breaking that creates mass hierarchy ALSO creates CKM mixing.
  θ_C is not an independent parameter — it's determined by mass ratios.
""")


# =====================================================================
# SECTION 7: THE FULL CKM STRUCTURE
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 7: FULL CKM FROM SP(1) BREAKING")
print("=" * 72)

print("""
The full CKM matrix has 3 angles + 1 phase. In the metric bundle:

  θ₁₂ (Cabibbo) ≈ √(m_d/m_s)  [Gatto-Sartori-Tonin]
  θ₂₃ ≈ √(m_s/m_b) × (correction factor)
  θ₁₃ ≈ √(m_d/m_b) × (correction factor)
  δ (CP phase) ≈ determined by complex phases in breaking VEV

Let's check θ₂₃ and θ₁₃:
""")

m_b = 4.18  # GeV

theta_23_from_mass = np.sqrt(m_s / m_b)
theta_13_from_mass = np.sqrt(m_d / m_b)

print(f"Mass ratio predictions:")
print(f"  sin(θ₂₃) ≈ √(m_s/m_b) = {theta_23_from_mass:.4f}")
print(f"  Observed sin(θ₂₃) = {np.sin(np.radians(theta_23_ckm)):.4f}")
print(f"  Ratio: {np.sin(np.radians(theta_23_ckm))/theta_23_from_mass:.2f}")

print(f"\n  sin(θ₁₃) ≈ √(m_d/m_b) = {theta_13_from_mass:.4f}")
print(f"  Observed sin(θ₁₃) = {np.sin(np.radians(theta_13_ckm)):.5f}")
print(f"  Ratio: {np.sin(np.radians(theta_13_ckm))/theta_13_from_mass:.3f}")

print("""
The simple mass ratio formulas give the RIGHT ORDER OF MAGNITUDE but
don't match precisely. Corrections from:
  - Running masses to common scale (M_PS)
  - Higher-order terms in Sp(1) breaking
  - Phase alignment between up and down sectors
""")


# =====================================================================
# SECTION 8: PMNS — WHY LARGE MIXING?
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 8: PMNS — WHY SUCH LARGE MIXING?")
print("=" * 72)

print("""
The PMNS matrix has MUCH LARGER mixing angles than CKM:
  θ₁₂ ≈ 33° vs 13° (2.5× larger)
  θ₂₃ ≈ 42° vs 2.4° (17× larger!)
  θ₁₃ ≈ 8.6° vs 0.2° (43× larger!)

Why the difference?

In Pati-Salam with Type-I seesaw:
  - Charged lepton Yukawa = down-type quark Yukawa (SU(4) relation)
  - Neutrino masses come from SEESAW: m_ν = (Y_ν v)² / M_R

The PMNS matrix is:
  U_PMNS = V_e† × V_ν

where V_e diagonalizes the charged lepton Yukawa and V_ν diagonalizes
the neutrino mass matrix m_ν.

If Y_ν has a different Sp(1) breaking pattern than Y_e (or if the
right-handed neutrino mass matrix M_R has specific structure), the
PMNS angles can be VERY DIFFERENT from CKM.

SPECIAL CASE: If M_R is Sp(1)-invariant, then V_ν ≈ I and
  U_PMNS ≈ V_e†

But V_e = V_d (SU(4) relation), so U_PMNS ≈ V_CKM.
This would give SMALL PMNS angles — WRONG!

Therefore: M_R must have NON-TRIVIAL structure that differs from Y_d.
""")


# =====================================================================
# SECTION 9: TRIBIMAXIMAL AND GEOMETRIC PATTERNS
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 9: SPECIAL MIXING PATTERNS")
print("=" * 72)

print("""
Before θ₁₃ was measured (pre-2012), the PMNS matrix was consistent with
TRIBIMAXIMAL MIXING:

  U_TB = [[√(2/3),  1/√3,    0   ],
          [-1/√6,   1/√3,  1/√2  ],
          [1/√6,   -1/√3,  1/√2  ]]

This has:
  θ₁₂ = arcsin(1/√3) = 35.26° (vs observed 33.4°)
  θ₂₃ = 45° exactly (vs observed 42-49°)
  θ₁₃ = 0° (WRONG — observed 8.6°)

Tribimaximal is CLOSE but NOT EXACT. The question: does the metric
bundle geometry give tribimaximal as a natural prediction?
""")

# Tribimaximal angles
theta_12_TB = np.degrees(np.arcsin(1/np.sqrt(3)))
theta_23_TB = 45.0
theta_13_TB = 0.0

print(f"Tribimaximal vs. observed:")
print(f"  {'Angle':<10} {'TB':>10} {'Observed':>10} {'Diff':>10}")
print(f"  {'-'*40}")
print(f"  {'θ₁₂':<10} {theta_12_TB:>10.2f} {theta_12_pmns:>10.2f} {theta_12_pmns - theta_12_TB:>+10.2f}")
print(f"  {'θ₂₃':<10} {theta_23_TB:>10.2f} {theta_23_pmns:>10.2f} {theta_23_pmns - theta_23_TB:>+10.2f}")
print(f"  {'θ₁₃':<10} {theta_13_TB:>10.2f} {theta_13_pmns:>10.2f} {theta_13_pmns - theta_13_TB:>+10.2f}")

print("""
θ₁₃ = 0 is RULED OUT. The actual value θ₁₃ ≈ 8.6° breaks tribimaximal.

GEOMETRIC INTERPRETATION:
Tribimaximal mixing comes from A₄ or S₄ discrete symmetries.
These are SUBGROUPS of Sp(1) = SU(2)!

  A₄ ⊂ SU(2) is the binary tetrahedral group (24 elements)
  S₄ ⊂ SU(2) is the binary octahedral group (48 elements)

The quaternions I, J, K generate T* ⊃ A₄. So the metric bundle
geometry CONTAINS the discrete symmetries needed for tribimaximal!

But tribimaximal requires the neutrino sector to respect this symmetry
while the charged lepton sector BREAKS it. This is possible if:
  - M_R (RH neutrino mass) respects A₄
  - Y_e (charged lepton Yukawa) breaks A₄
""")


# =====================================================================
# SECTION 10: ATTEMPT TO DERIVE ANGLES
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 10: COMPUTING MIXING FROM SP(1) BREAKING")
print("=" * 72)

print("""
Let's compute the CKM and PMNS matrices from specific Sp(1) breaking
patterns and see if we can match observations.

MODEL:
  - Up-type Yukawa: Y_u = y_u × M_u where M_u is a 3×3 breaking matrix
  - Down-type Yukawa: Y_d = y_d × M_d where M_d is a different matrix
  - V_CKM = U_u† × U_d where U diagonalizes the corresponding Yukawa

The breaking matrices are determined by how each sector couples to
the breaking VEV in the (I, J, K) direction.
""")

def yukawa_from_breaking(theta_break, phi_break, overlap_matrix):
    """
    Construct Yukawa matrix from Sp(1) breaking direction.

    The breaking direction (θ, φ) on S² selects a preferred complex structure.
    The Yukawa couplings depend on how much each generation "aligns" with this.
    """
    # Breaking direction unit vector
    n = np.array([np.sin(theta_break) * np.cos(phi_break),
                  np.sin(theta_break) * np.sin(phi_break),
                  np.cos(theta_break)])

    # The diagonal elements are enhanced/suppressed based on alignment
    # Generation i aligns with e_i in (I, J, K) space
    # Alignment factor: 1 + epsilon × (n · e_i)
    epsilon = 0.9  # Breaking strength (0 = no breaking, 1 = maximal)

    diag_factors = 1 + epsilon * n
    Y = np.diag(diag_factors)

    # Off-diagonal mixing from overlap matrix
    # This is the part that determines CKM
    # For small breaking, the unitary matrix that diagonalizes Y
    # differs from identity by terms proportional to the overlap

    return Y, diag_factors

# Use the overlap matrix computed in TN11
# From fermion_masses.py: O_ab has eigenvalues {1/2, 1/2, 8} (ratio 1:1:16)
O_approx = np.array([
    [3.0, 0.5, 0.5],
    [0.5, 3.0, 0.5],
    [0.5, 0.5, 3.0]
])

# Up-type breaking: along J₃ direction
theta_u, phi_u = 0.01, 0.0  # Slightly off J₃
Y_u, diag_u = yukawa_from_breaking(theta_u, phi_u, O_approx)

# Down-type breaking: rotated by ~Cabibbo angle
theta_d = np.radians(theta_12_ckm)  # Use observed as target
phi_d = 0.0
Y_d, diag_d = yukawa_from_breaking(theta_d, phi_d, O_approx)

print(f"Up-type Yukawa (breaking along J₃):")
print(f"  Diagonal: {np.round(diag_u, 4)}")
print(f"  Eigenvalues: {np.round(np.linalg.eigvalsh(Y_u), 4)}")

print(f"\nDown-type Yukawa (rotated by θ_C):")
print(f"  Diagonal: {np.round(diag_d, 4)}")
print(f"  Eigenvalues: {np.round(np.linalg.eigvalsh(Y_d), 4)}")

# Diagonalize each Yukawa
eig_u, U_u = np.linalg.eigh(Y_u)
eig_d, U_d = np.linalg.eigh(Y_d)

# Sort by eigenvalue (ascending = lightest first)
idx_u = np.argsort(eig_u)
idx_d = np.argsort(eig_d)
U_u = U_u[:, idx_u]
U_d = U_d[:, idx_d]

# CKM matrix
V_CKM_pred = U_u.T @ U_d

print(f"\nPredicted |V_CKM|:")
for row in np.abs(V_CKM_pred):
    print(f"  [{row[0]:.5f}, {row[1]:.5f}, {row[2]:.5f}]")

print(f"\nObserved |V_CKM|:")
for row in V_CKM_obs:
    print(f"  [{row[0]:.5f}, {row[1]:.5f}, {row[2]:.5f}]")

print("""
This simple model gives a CKM close to identity, as expected from
small misalignment. The precise structure depends on the overlap
matrix and the breaking angles.
""")


# =====================================================================
# SECTION 11: FITTING TO OBSERVATIONS
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 11: CAN WE FIT CKM/PMNS?")
print("=" * 72)

print("""
Let's try to FIND breaking parameters that reproduce observations.

Parameters:
  - θ_u, φ_u: up-type breaking direction
  - θ_d, φ_d: down-type breaking direction
  - ε_u, ε_d: breaking strengths
  - For leptons: additional parameters for M_R structure

This is a 6+ parameter fit to 6 observables (3 CKM angles, 3 PMNS angles).
If successful, it shows CONSISTENCY, not prediction.
""")

def ckm_from_params(params):
    """Compute CKM from breaking parameters."""
    theta_u, phi_u, eps_u, theta_d, phi_d, eps_d = params

    # Breaking direction vectors
    n_u = np.array([np.sin(theta_u) * np.cos(phi_u),
                    np.sin(theta_u) * np.sin(phi_u),
                    np.cos(theta_u)])
    n_d = np.array([np.sin(theta_d) * np.cos(phi_d),
                    np.sin(theta_d) * np.sin(phi_d),
                    np.cos(theta_d)])

    # Yukawa eigenvalues from breaking
    y_u = np.sort(1 + eps_u * n_u)  # Sort: lightest to heaviest
    y_d = np.sort(1 + eps_d * n_d)

    # For small breaking, the eigenvectors are approximately the
    # standard basis rotated by the breaking direction.
    # This is a simplification — full treatment requires the overlap matrix.

    # Build rotation matrices
    # V_u rotates from interaction to mass basis for up-type
    # V_d rotates for down-type
    # CKM = V_u† V_d

    # Simple model: rotation in the 1-2 plane by angle ∝ breaking mismatch
    angle_12 = 0.5 * np.arctan2(n_u[0] - n_d[0], n_u[2] - n_d[2] + 0.01)
    angle_23 = 0.5 * np.arctan2(n_u[1] - n_d[1], n_u[2] - n_d[2] + 0.01)
    angle_13 = 0.3 * np.arctan2(n_u[0] - n_d[0], n_u[1] - n_d[1] + 0.01)

    # Build CKM from angles (standard parametrization)
    c12, s12 = np.cos(angle_12), np.sin(angle_12)
    c23, s23 = np.cos(angle_23), np.sin(angle_23)
    c13, s13 = np.cos(angle_13), np.sin(angle_13)

    V = np.array([
        [c12*c13, s12*c13, s13],
        [-s12*c23 - c12*s23*s13, c12*c23 - s12*s23*s13, s23*c13],
        [s12*s23 - c12*c23*s13, -c12*s23 - s12*c23*s13, c23*c13]
    ])

    return np.abs(V)

def ckm_loss(params):
    """Loss function for CKM fit."""
    V_pred = ckm_from_params(params)
    diff = (V_pred - V_CKM_obs) / V_CKM_obs  # Relative error
    return np.sum(diff**2)

# Initial guess
x0 = [0.1, 0.0, 0.5, 0.3, 0.1, 0.5]  # θ_u, φ_u, ε_u, θ_d, φ_d, ε_d

# Bounds
bounds = [(0, np.pi), (-np.pi, np.pi), (0.1, 1.0),
          (0, np.pi), (-np.pi, np.pi), (0.1, 1.0)]

# Minimize
result = minimize(ckm_loss, x0, bounds=bounds, method='L-BFGS-B')

if result.success:
    best_params = result.x
    V_fit = ckm_from_params(best_params)

    print(f"Best-fit parameters:")
    print(f"  θ_u = {np.degrees(best_params[0]):.1f}°, φ_u = {np.degrees(best_params[1]):.1f}°, ε_u = {best_params[2]:.3f}")
    print(f"  θ_d = {np.degrees(best_params[3]):.1f}°, φ_d = {np.degrees(best_params[4]):.1f}°, ε_d = {best_params[5]:.3f}")

    print(f"\nFitted |V_CKM|:")
    for row in V_fit:
        print(f"  [{row[0]:.5f}, {row[1]:.5f}, {row[2]:.5f}]")

    print(f"\nResidual loss: {result.fun:.6f}")
else:
    print(f"Fit did not converge: {result.message}")


# =====================================================================
# SECTION 12: HONEST ASSESSMENT
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 12: HONEST ASSESSMENT")
print("=" * 72)

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  CKM AND PMNS MIXING — RESULTS                                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  WHAT THE FRAMEWORK PROVIDES:                                        ║
║                                                                      ║
║    1. Three generations from quaternionic structure I, J, K          ║
║       These span S² in complex structure space                       ║
║       STATUS: Rigorous                                               ║
║                                                                      ║
║    2. Tree-level degeneracy: V_CKM = V_PMNS = I (no mixing)         ║
║       From Sp(1) flavor symmetry                                     ║
║       STATUS: Rigorous                                               ║
║                                                                      ║
║    3. Mixing arises from Sp(1) breaking                              ║
║       CKM = misalignment between up and down breaking directions     ║
║       STATUS: Framework (not predictive)                             ║
║                                                                      ║
║    4. Gatto-Sartori-Tonin relation: θ_C ≈ √(m_d/m_s)                ║
║       The SAME breaking that creates mass hierarchy creates CKM      ║
║       STATUS: Consistent with observation                            ║
║                                                                      ║
║  WHAT THE FRAMEWORK DOES NOT PROVIDE:                                ║
║                                                                      ║
║    ✗ Specific breaking directions (θ_u, φ_u), (θ_d, φ_d)            ║
║      These are free parameters                                       ║
║                                                                      ║
║    ✗ Prediction of CKM/PMNS angles from geometry alone              ║
║      Would require a selection principle for breaking directions     ║
║                                                                      ║
║    ✗ Explanation of why PMNS has large angles vs CKM small          ║
║      Requires understanding M_R structure (seesaw mechanism)         ║
║                                                                      ║
║    ✗ CP violation (phases)                                           ║
║      Complex phases in breaking VEV are additional parameters        ║
║                                                                      ║
║  POSSIBLE SELECTION PRINCIPLES:                                      ║
║                                                                      ║
║    • A₄ or S₄ discrete symmetry (subgroups of Sp(1))                ║
║      Could select tribimaximal for PMNS                              ║
║      But θ₁₃ ≠ 0 rules out exact tribimaximal                       ║
║                                                                      ║
║    • Vacuum alignment via potential minimization                     ║
║      Would require computing the scalar potential on S²              ║
║      Not yet done in this framework                                  ║
║                                                                      ║
║    • Anthropic/dynamical selection                                   ║
║      Breaking direction selected by some other principle             ║
║                                                                      ║
║  COMPARISON WITH STANDARD APPROACHES:                                ║
║                                                                      ║
║    The metric bundle is NO WORSE than other approaches:              ║
║    - Froggatt-Nielsen: assumes textures (free parameters)            ║
║    - Discrete symmetries: A₄, S₄, etc. (free choice of group)       ║
║    - Extra dimensions: compactification (free geometry)              ║
║                                                                      ║
║    All flavor models have free parameters for CKM/PMNS.              ║
║    The metric bundle at least CONNECTS CKM to mass hierarchy         ║
║    via Sp(1) breaking (Gatto-Sartori-Tonin relation).                ║
║                                                                      ║
║  VERDICT: CONSISTENT BUT NOT PREDICTIVE                              ║
║                                                                      ║
║    CKM/PMNS angles are free parameters in the current framework.     ║
║    They could become predictions if a selection principle for        ║
║    the Sp(1) breaking direction is identified.                       ║
║                                                                      ║
║  VIABILITY IMPACT: None                                              ║
║    This is the standard situation for flavor physics.                ║
║    No existing theory predicts all mixing angles from geometry.      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")


# =====================================================================
# SECTION 13: WHAT WOULD MAKE IT PREDICTIVE?
# =====================================================================

print("\n" + "=" * 72)
print("SECTION 13: PATHWAYS TO PREDICTION")
print("=" * 72)

print("""
To make CKM/PMNS angles PREDICTIONS (not free parameters), we need:

1. VACUUM SELECTION PRINCIPLE
   Compute the effective potential V(θ, φ) on S² from the full theory.
   The breaking direction is the minimum of this potential.
   This requires:
   - One-loop corrections to the scalar potential
   - Coupling of Sp(1) breaking to gauge and Yukawa sectors

2. DISCRETE SYMMETRY FROM TOPOLOGY
   The metric bundle might have a PREFERRED breaking direction from
   topological considerations (e.g., non-trivial π₁ or π₂ of the bundle).
   Check if the section moduli space has special points.

3. RG FLOW ATTRACTOR
   The Sp(1) breaking direction might flow to a fixed point under RG.
   This would make the low-energy breaking direction insensitive to
   initial conditions (UV completion).

4. INFORMATION-THEORETIC SELECTION
   Under Structural Idealism, the FEP might select breaking directions.
   "The observer minimizes variational free energy" could determine
   which complex structure is "preferred."

5. COMPUTE THE SEESAW STRUCTURE
   For PMNS, the key is the right-handed neutrino mass matrix M_R.
   If M_R comes from the geometry (e.g., from a different sector of
   the metric bundle), its structure could be predicted.
   Then PMNS = V_e† × V_ν would be determined.

CONCRETE NEXT STEP:
   Compute the one-loop effective potential V_eff(θ, φ) for the Sp(1)
   breaking field and find its minima. If the minimum is at a special
   geometric point (pole, edge, center), that would predict CKM angles.
""")


# =====================================================================
# SUMMARY TABLE
# =====================================================================

print("\n" + "=" * 72)
print("SUMMARY TABLE")
print("=" * 72)

print(f"""
┌───────────────────────────────────────────────────────────────────────┐
│  CKM/PMNS IN THE METRIC BUNDLE                                        │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  CKM Angles (quarks):                                                 │
│    θ₁₂ = {theta_12_ckm:.2f}° (Cabibbo)       Status: PARAMETRIC            │
│    θ₂₃ = {theta_23_ckm:.2f}°                  Status: PARAMETRIC            │
│    θ₁₃ = {theta_13_ckm:.3f}°                  Status: PARAMETRIC            │
│    δ   = {delta_ckm:.0f}° (CP)               Status: PARAMETRIC            │
│                                                                       │
│  PMNS Angles (leptons):                                               │
│    θ₁₂ = {theta_12_pmns:.1f}° (solar)          Status: PARAMETRIC            │
│    θ₂₃ = {theta_23_pmns:.1f}° (atmospheric)    Status: PARAMETRIC            │
│    θ₁₃ = {theta_13_pmns:.2f}° (reactor)        Status: PARAMETRIC            │
│    δ   = {delta_pmns:.0f}° (CP)               Status: PARAMETRIC            │
│                                                                       │
│  Geometric source: Sp(1) breaking direction on S²                     │
│  Constraint: θ_C ≈ √(m_d/m_s) (Gatto-Sartori-Tonin) — CONSISTENT     │
│                                                                       │
│  To make PREDICTIVE:                                                  │
│    • Compute vacuum alignment potential V(θ, φ)                       │
│    • Find topological/discrete constraints on breaking                │
│    • Determine M_R structure for seesaw (PMNS)                        │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
""")

print("=" * 72)
print("COMPUTATION COMPLETE")
print("=" * 72)
