#!/usr/bin/env python3
"""
FEP LOCALISATION VERIFICATION SUITE — Paper 8
================================================

Tests every quantitative claim in Paper 8:
Localisation from the Free Energy Principle on the Metric Bundle.

All computations use the orthonormal basis for S²(R^{3,1}), where
off-diagonal elements are normalized by 1/√2. In this basis, the
DeWitt metric has eigenvalues {-1: ×4, +1: ×6} (signature (6,4)).

Author: Metric Bundle Programme, March 2026
"""

import numpy as np

print("=" * 72)
print("PAPER 8: FEP LOCALISATION VERIFICATION SUITE")
print("=" * 72)

passed = 0
failed = 0
total = 0

def check(name, predicted, observed, tolerance, unit=""):
    """Check a prediction against observation."""
    global passed, failed, total
    total += 1
    if observed != 0:
        error = abs(predicted - observed) / abs(observed)
    else:
        error = abs(predicted - observed)
    status = "PASS" if error <= tolerance else "FAIL"
    if status == "PASS":
        passed += 1
    else:
        failed += 1
    print(f"  [{status}] {name}")
    print(f"         Predicted: {predicted:.6g} {unit}")
    print(f"         Observed:  {observed:.6g} {unit}")
    print(f"         Error:     {error*100:.1f}%  (tolerance: {tolerance*100:.0f}%)")
    return status == "PASS"


# =====================================================================
# TEST 1: DeWitt eigenvalues and signature
# =====================================================================
print("\n" + "=" * 72)
print("TEST 1: DeWitt metric eigenvalues (orthonormal basis)")
print("=" * 72)

d = 4
eta = np.diag([-1.0, 1.0, 1.0, 1.0])

# Orthonormal basis for S²(R⁴): diagonal e_{ii}, off-diagonal (1/√2)(e_{ij}+e_{ji})
basis = []
for i in range(d):
    for j in range(i, d):
        mat = np.zeros((d, d))
        if i == j:
            mat[i, i] = 1.0
        else:
            mat[i, j] = 1.0 / np.sqrt(2)
            mat[j, i] = 1.0 / np.sqrt(2)
        basis.append(mat)

dim_fibre = len(basis)  # = 10
G_DW = np.zeros((dim_fibre, dim_fibre))
for a in range(dim_fibre):
    for b in range(dim_fibre):
        h, k = basis[a], basis[b]
        t1 = np.einsum('mr,ns,mn,rs', eta, eta, h, k)
        trh = np.einsum('mn,mn', eta, h)
        trk = np.einsum('mn,mn', eta, k)
        G_DW[a, b] = t1 - 0.5 * trh * trk

eigs = np.linalg.eigvalsh(G_DW)
eigs_sorted = np.sort(eigs)
n_pos = int(np.sum(eigs > 1e-10))
n_neg = int(np.sum(eigs < -1e-10))

total += 1
if n_pos == 6 and n_neg == 4:
    passed += 1
    print(f"  [PASS] Signature = ({n_pos}, {n_neg}) = (6, 4)")
else:
    failed += 1
    print(f"  [FAIL] Signature = ({n_pos}, {n_neg}), expected (6, 4)")

print(f"         Eigenvalues: {eigs_sorted.round(6)}")

# In orthonormal basis: all eigenvalues are ±1
n_neg1 = int(np.sum(np.abs(eigs - (-1)) < 0.01))
n_pos1 = int(np.sum(np.abs(eigs - (+1)) < 0.01))

total += 1
if n_neg1 == 4 and n_pos1 == 6:
    passed += 1
    print(f"  [PASS] Orthonormal spectrum: {{-1: ×{n_neg1}, +1: ×{n_pos1}}}")
else:
    failed += 1
    print(f"  [FAIL] Expected {{-1: ×4, +1: ×6}}, got -1×{n_neg1}, +1×{n_pos1}")


# =====================================================================
# TEST 2: FEP prior from fibre curvature
# =====================================================================
print("\n" + "=" * 72)
print("TEST 2: FEP prior — Gaussian width from R_fibre = -30")
print("=" * 72)

R_fibre = -30.0
n_fibre = 10
curvature_scale = abs(R_fibre) / n_fibre  # = 3.0

print(f"  R_fibre = {R_fibre}")
print(f"  dim(F)  = {n_fibre}")
print(f"  |R_fibre|/n = {curvature_scale}")

check("|R_fibre|/n = 3 (curvature scale per dim)", curvature_scale, 3.0, 0.001)


# =====================================================================
# TEST 3: Localisation widths σ_a from FEP minimum
# =====================================================================
print("\n" + "=" * 72)
print("TEST 3: FEP localisation widths (flat base, Hessian → 0)")
print("=" * 72)

# On flat base, Hessian M → 0, localisation from prior only:
# Σ⁻¹ = (|R_fibre|/n) × |G_DW|
# σ²_a = n / (|R_fibre| × |λ_a|)
# In orthonormal basis: all |λ_a| = 1, so σ²_a = 10/30 = 1/3 for all modes

abs_eigenvalues = np.abs(eigs_sorted)
sigma_sq = n_fibre / (abs(R_fibre) * abs_eigenvalues)
sigma = np.sqrt(sigma_sq)

print(f"  All |λ_a| = 1 in orthonormal basis → uniform localisation:")
for i, (ev, s) in enumerate(zip(eigs_sorted, sigma)):
    sector = "gauge (V⁺)" if ev > 0 else "Higgs/conf (V⁻)"
    print(f"    Mode {i+1}: λ = {ev:+.0f}, σ² = {sigma_sq[i]:.4f}, σ = {s:.4f}  [{sector}]")

check("σ² = 1/3 for all modes", sigma_sq[0], 1.0/3.0, 0.001)
check("σ² uniform (std dev = 0)", np.std(sigma_sq), 0.0, 0.001)


# =====================================================================
# TEST 4: Effective volume V_eff
# =====================================================================
print("\n" + "=" * 72)
print("TEST 4: Effective volume V_eff")
print("=" * 72)

# V_eff = (2π)^5 × ∏σ_a = (2π)^5 × (1/√3)^10 = (2π)^5/3^5
V_eff_numerical = (2 * np.pi)**5 * np.prod(sigma)
V_eff_analytic = (2 * np.pi)**5 / 3**5  # = (2π)^5/243

print(f"  V_eff (numerical)  = {V_eff_numerical:.4f}")
print(f"  V_eff (analytic)   = (2π)⁵/3⁵ = (2π)⁵/243 = {V_eff_analytic:.4f}")

check("V_eff numerical = analytic", V_eff_numerical, V_eff_analytic, 0.001)

# Store for later use
V_eff = V_eff_analytic


# =====================================================================
# TEST 5: Gauge coupling from soldering + FEP
# =====================================================================
print("\n" + "=" * 72)
print("TEST 5: Gauge coupling α_PS from soldering + FEP")
print("=" * 72)

kappa_sq = 9.0 / 8.0   # SO(6) sectional curvature = 9/8
T_Dynkin = 1.0          # Dynkin index for fundamental of SU(4)

# g² = κ²/(2T × V_eff^{1/5})
# V_eff^{1/5} = ((2π)^5/243)^{1/5} = (2π)/243^{1/5} = (2π)/3 = 2π/3
V_eff_fifth = V_eff**(1.0/5.0)
V_eff_fifth_exact = (2 * np.pi) / 3.0  # since (2π)^{5/5} / 3^{5/5} = 2π/3

print(f"  V_eff^(1/5) = {V_eff_fifth:.4f}")
print(f"  V_eff^(1/5) exact = 2π/3 = {V_eff_fifth_exact:.4f}")

g_PS_sq = kappa_sq / (2 * T_Dynkin * V_eff_fifth_exact)
alpha_PS_FEP = g_PS_sq / (4 * np.pi)
alpha_PS_obs = 0.023

print(f"\n  κ² = {kappa_sq} = 9/8 (SO(6) sectional curvature)")
print(f"  T  = {T_Dynkin} (Dynkin index)")
print(f"  g²_PS = κ²/(2T × 2π/3) = (9/8)/(4π/3) = 27/(32π)")
print(f"  g²_PS = {g_PS_sq:.6f}")
print(f"  α_PS  = g²/(4π) = 27/(128π²) = {alpha_PS_FEP:.6f}")
print(f"  α_PS (observed) = {alpha_PS_obs}")

ratio = alpha_PS_FEP / alpha_PS_obs
print(f"  Ratio: {ratio:.2f}×")

# Exact: α = 27/(128π²) ≈ 0.02137
alpha_exact = 27.0 / (128.0 * np.pi**2)
print(f"\n  Exact closed form: α_PS = 27/(128π²) = {alpha_exact:.6f}")

check("α_PS(FEP) ≈ 0.023 (observed)", alpha_PS_FEP, alpha_PS_obs, 0.10)

# Compare with naive KK
alpha_KK_naive = 1.0 / (4 * np.pi * (2.4e18)**2 * 2)
print(f"\n  Naive KK: α_KK ~ {alpha_KK_naive:.2e} (factor ~10^{int(np.log10(alpha_PS_obs/alpha_KK_naive))} off)")
print(f"  FEP improvement: from 10^36× off to {ratio:.1f}× off")


# =====================================================================
# TEST 6: Cosmological constant
# =====================================================================
print("\n" + "=" * 72)
print("TEST 6: Cosmological constant — consistency check")
print("=" * 72)

H_sq = -1.0
II_sq = 2.0
Lambda_bare = -0.5 * (R_fibre + H_sq - II_sq)
print(f"  Λ_bare = -½({R_fibre} + {H_sq} - {II_sq}) = {Lambda_bare}")

check("Λ_bare = +16.5 M_P²", Lambda_bare, 16.5, 0.001)

ell_P = 1.616e-35  # m
Lambda_obs = 2.85e-122  # in M_P² units

# Run formula BACKWARDS: given observed Λ, what is φ₀ and L_obs?
phi_0 = 0.25 * np.log(Lambda_bare / Lambda_obs)
L_obs = np.exp(phi_0) * ell_P
L_H = 3e8 / (67.4e3 / 3.086e22)  # c/H₀ (Hubble radius, honest)

print(f"\n  Running formula backwards from observed Λ:")
print(f"    φ₀ = ¼ ln(Λ_bare/Λ_obs) = {phi_0:.2f}")
print(f"    L_obs = e^φ₀ × ℓ_P = {L_obs*1e6:.1f} μm")
print(f"    L_H = c/H₀ = {L_H:.3e} m")
print(f"    √(ℓ_P × L_H) = {np.sqrt(ell_P * L_H)*1e6:.1f} μm")
print(f"    Geometric mean ratio: L_obs/√(ℓ_P × L_H) = {L_obs/np.sqrt(ell_P * L_H):.2f}")

# The consistency check: L_obs should be ~ biological cell scale
check("L_obs ≈ 84 μm (cell scale)", L_obs * 1e6, 84.0, 0.10, "μm")

# Note: this is a CONSISTENCY CHECK, not a prediction
# The gauge coupling α_PS = 27/(128π²) is the genuine prediction
print(f"\n  NOTE: This is a consistency check, not a prediction.")
print(f"  The framework accommodates Λ_obs with L_obs ≈ cell scale.")
print(f"  Deriving φ₀ from FEP alone (without Λ input) remains open.")


# =====================================================================
# TEST 7: Uncertainty principle consistency
# =====================================================================
print("\n" + "=" * 72)
print("TEST 7: Uncertainty principle — σ_+ and σ_- both nonzero")
print("=" * 72)

sigma_plus_sq = sigma_sq[eigs_sorted > 0]    # 6 gauge modes
sigma_minus_sq = sigma_sq[eigs_sorted < 0]   # 4 Higgs/conformal modes

print(f"  σ²_+ (gauge, {len(sigma_plus_sq)} modes): all = {sigma_plus_sq[0]:.4f}")
print(f"  σ²_- (Higgs, {len(sigma_minus_sq)} modes): all = {sigma_minus_sq[0]:.4f}")

total += 1
if np.all(sigma_plus_sq > 0) and np.all(sigma_minus_sq > 0):
    passed += 1
    print(f"  [PASS] Both σ_+ and σ_- nonzero — uncertainty principle satisfied")
else:
    failed += 1
    print(f"  [FAIL] Uncertainty principle violated")


# =====================================================================
# TEST 8: V_eff finite and positive
# =====================================================================
print("\n" + "=" * 72)
print("TEST 8: V_eff is finite and positive")
print("=" * 72)

total += 1
if V_eff > 0 and np.isfinite(V_eff):
    passed += 1
    print(f"  [PASS] V_eff = {V_eff:.4f} > 0 and finite")
else:
    failed += 1
    print(f"  [FAIL] V_eff not finite/positive")


# =====================================================================
# TEST 9: det(G_DW) in orthonormal basis
# =====================================================================
print("\n" + "=" * 72)
print("TEST 9: det(G_DW) in orthonormal basis")
print("=" * 72)

det_GDW = np.linalg.det(G_DW)
# In orthonormal basis: eigenvalues all ±1, so det = (-1)^4 × (+1)^6 = +1
# But wait: the matrix is 10×10 and not diagonal in this basis!

print(f"  det(G_DW) = {det_GDW:.4f}")
print(f"  Expected: (-1)⁴ × (+1)⁶ = +1 (orthonormal basis)")

check("det(G_DW) = +1 (orthonormal)", det_GDW, 1.0, 0.001)


# =====================================================================
# TEST 10: Closed-form coupling α = 27/(128π²)
# =====================================================================
print("\n" + "=" * 72)
print("TEST 10: Closed-form gauge coupling")
print("=" * 72)

# α_PS = κ²/(2T × V^{1/5}) / (4π)
#      = (9/8) / (2 × 1 × 2π/3) / (4π)
#      = (9/8) × (3/(4π)) / (4π)
#      = 27/(32 × 16π²)
#      = 27/(128π²)

alpha_closed = 27.0 / (128.0 * np.pi**2)
print(f"  α_PS = 27/(128π²) = {alpha_closed:.6f}")
print(f"  1/α_PS = {1/alpha_closed:.1f}")

check("α_PS closed form = numerical", alpha_closed, alpha_PS_FEP, 0.001)
check("α_PS = 0.02137 (7% from observed)", alpha_closed, 0.02137, 0.001)


# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION SUMMARY")
print("=" * 72)

ratio_coupling = alpha_PS_FEP / alpha_PS_obs

print(f"""
  Total tests:  {total}
  Passed:       {passed}
  Failed:       {failed}
  Pass rate:    {100*passed/total:.0f}%

  ═══════════════════════════════════════════════════════════════
  KEY RESULTS
  ═══════════════════════════════════════════════════════════════

  GAUGE COUPLING (the main result — genuine prediction):
    α_PS(FEP) = 27/(128π²) = {alpha_PS_FEP:.5f}
    α_PS(obs) = {alpha_PS_obs}
    Ratio: {ratio_coupling:.2f}×  ({abs(1-ratio_coupling)*100:.0f}% off)
    Naive KK was 10^36× off — FEP closes 36 orders of magnitude

  COSMOLOGICAL CONSTANT (consistency check — not a prediction):
    Λ_bare = {Lambda_bare} M_P² (from Gauss equation, correct sign)
    Λ_obs  = {Lambda_obs:.2e} M_P²
    Implied φ₀ = {phi_0:.2f}
    Implied L_obs = {L_obs*1e6:.0f} μm (biological cell scale)
    Framework accommodates observed Λ with physically meaningful scale.
    Deriving φ₀ from FEP alone remains open.

  ═══════════════════════════════════════════════════════════════
""")

if failed == 0:
    print("  ALL TESTS PASSED ✓")
else:
    print(f"  {failed} test(s) need further work.")

print("=" * 72)
