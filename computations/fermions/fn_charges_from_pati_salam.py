#!/usr/bin/env python3
"""
FN Charges from Pati-Salam: Can We Derive Them?
================================================

RESULT: NO. The Froggatt-Nielsen charges for different fermion sectors
CANNOT be derived purely from Pati-Salam + Sp(1) breaking.

This script demonstrates five independent reasons why.
"""

import numpy as np

print("=" * 70)
print("CAN FN CHARGES BE DERIVED FROM PATI-SALAM + Sp(1)?")
print("=" * 70)

# =====================================================================
# REASON 1: Sp(1) → U(1) gives UNIQUE charges
# =====================================================================
print("\n--- Reason 1: Sp(1) charges are generation-only ---")

# The adjoint of Sp(1) on Im(H) = {I, J, K}
# ad_K acts on {I, J, K} basis
# [K, I] = 2J, [K, J] = -2I, [K, K] = 0
ad_K = np.array([
    [0, -2, 0],
    [2,  0, 0],
    [0,  0, 0]
], dtype=float)

eigenvalues = np.linalg.eigvals(ad_K)
print(f"ad_K eigenvalues: {np.sort_complex(eigenvalues)}")
print("Charges: q = (+1, -1, 0) after normalization")
print("These are the SAME for ALL fermion types within a generation.")

# =====================================================================
# REASON 2: u_L and d_L in same PS multiplet
# =====================================================================
print("\n--- Reason 2: u_L, d_L in same (4,2,1) ---")
print("F_L = (4,2,1) contains BOTH u_L and d_L")
print("F_R = (4bar,1,2) contains BOTH u_R and d_R")
print("Therefore: FN matrix Y_{ab} ~ eps^{|q_a|+|q_b|} is IDENTICAL")
print("for up-type and down-type at tree level.")

# =====================================================================
# REASON 3: Phi and Phi-tilde are Sp(1) singlets
# =====================================================================
print("\n--- Reason 3: Phi, Phi-tilde are Sp(1) singlets ---")
print("Bidoublet Phi = (1,2,2) lives in V^- (negative-norm sector)")
print("Sp(1) acts on V^+ (positive-norm sector)")
print("[Sp(1), Phi] = 0 and [Sp(1), Phi-tilde] = 0")
print("Therefore: Y_1 (from Phi) and Y_2 (from Phi-tilde)")
print("have the SAME Sp(1) transformation properties.")
print("They CANNOT carry different FN charges.")

# =====================================================================
# REASON 4: VEV ratio gives only universal factor
# =====================================================================
print("\n--- Reason 4: v_1/v_2 gives only universal ratio ---")

# M_up = Y_1 * v_1 + Y_2 * v_2
# M_down = Y_1 * v_2 + Y_2 * v_1
# If Y_1 and Y_2 have same generation structure (from Reason 3),
# then M_up/M_down is generation-independent

eps = 1 / np.sqrt(20)
# Universal FN matrix (same for up and down)
Y_FN = np.array([
    [eps**4, eps**3, eps**2],
    [eps**3, eps**2, eps**1],
    [eps**2, eps**1, 1.0  ]
])

# Two independent coefficients
c1, c2 = 0.8, 0.3  # arbitrary O(1) coefficients

# Try different VEV ratios
for tan_beta in [1.0, 5.0, 40.0]:
    v1 = 246 / np.sqrt(1 + tan_beta**2)
    v2 = v1 * tan_beta

    M_up = (c1 * v1 + c2 * v2) * Y_FN
    M_down = (c1 * v2 + c2 * v1) * Y_FN

    ratios = np.diag(M_up) / np.diag(M_down)
    print(f"  tan(β) = {tan_beta:.1f}: m_up/m_down ratios = "
          f"{ratios[0]:.2f}, {ratios[1]:.2f}, {ratios[2]:.2f}")
    print(f"  → All ratios IDENTICAL = {ratios[0]:.4f}")

print("\nObserved ratios: m_t/m_b = 41, m_c/m_s = 14, m_u/m_d = 0.46")
print("These are WILDLY different → cannot come from universal VEV ratio")

# =====================================================================
# REASON 5: SU(4) Clebschs don't help
# =====================================================================
print("\n--- Reason 5: (15,2,2) gives generation-independent factor ---")
print("Adding a (15,2,2) Higgs gives:")
print("  Y_quark = (a + b/3) * Y_FN")
print("  Y_lepton = (a - b) * Y_FN")
print("The FN matrix Y_FN is the SAME → hierarchy is identical")
print("Only the OVERALL scale differs (quark vs lepton)")

# =====================================================================
# WHAT CAN BE DERIVED
# =====================================================================
print("\n" + "=" * 70)
print("WHAT CAN BE DERIVED FROM PS + Sp(1)")
print("=" * 70)

print("""
✓ Three generations with identical gauge quantum numbers
✓ A universal hierarchy 1 : ε² : ε⁴ with ε = 1/√20
✓ Bottom-tau unification at M_PS (from SU(4))
✓ CKM = identity at tree level
✓ The Cabibbo angle sin(θ_C) = ε = 0.224 (from generation overlap)
""")

# =====================================================================
# WHAT CANNOT BE DERIVED
# =====================================================================
print("=" * 70)
print("WHAT CANNOT BE DERIVED (needs additional input)")
print("=" * 70)

print("""
✗ Different ε-powers for leptons (~ε²) vs down quarks (~ε^2.5) vs up quarks (~ε³)
✗ The claim q_up = 2×q_down has NO group-theoretic basis in Pati-Salam
✗ It REQUIRES SU(5) or SO(10) where up/down sit in different reps (10 vs 5̄)

To get sector-dependent hierarchies, you need AT LEAST ONE of:
  1. A second Sp(1)-breaking scale coupling differently to Φ vs Φ̃
  2. A (15,2,2) Higgs with generation-dependent VEV (requires a second flavon)
  3. Higher-dimensional operators with different SU(4) tensor structure
  4. Embedding in SU(5) or SO(10) where 10 and 5̄ have different quantum numbers
""")

# =====================================================================
# THE HONEST CONCLUSION
# =====================================================================
print("=" * 70)
print("CONCLUSION")
print("=" * 70)

print("""
The Metric Bundle gives:
  - ε = 1/√20 (derived from fiber dimension)      ← GENUINE
  - Universal hierarchy m₃ : m₂ : m₁ ~ 1 : ε² : ε⁴  ← DERIVED from Sp(1)
  - Bottom-tau unification                           ← FROM SU(4)
  - Cabibbo angle = ε                                ← DERIVED

The Metric Bundle does NOT give:
  - Why up-type has ε³ while down-type has ε²        ← FITTED
  - Why leptons differ from quarks in hierarchy       ← NEEDS (15,2,2)
  - The O(1) Yukawa coefficients                     ← NEEDS Dirac operator

STATUS: The mass hierarchy is a CONSISTENCY CHECK (order of magnitude correct
with one parameter ε), not a PREDICTION (specific powers are fitted).
""")
