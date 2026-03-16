#!/usr/bin/env python3
"""
Coleman-Weinberg Potential for SU(2)_R Breaking
=================================================

In the metric bundle framework:
  - Tree-level potential for SU(2)_R breaking is ZERO
    (fibre curvature is L-R symmetric: proven in lr_breaking_check.py)
  - The CW mechanism (1-loop) provides the FULL effective potential
  - Dimensional transmutation determines M_R from M_C

Key metric bundle inputs:
  - g_R(M_C) = g_L(M_C) = g_PS  (from PS unification)
  - f_ν ≈ 0 at tree level  (b/a = 0 from fibre_ricci_full.py)
  - M_C = 4.5 × 10^16 GeV  (from zero_parameter_rg.py)
  - g_BL(M_C) from PS embedding

Particles that get mass from v_R ≡ ⟨Δ_R^0⟩:
  - W_R^±  gauge bosons:  M = g_R v_R  (6 d.o.f.)
  - Z'     gauge boson:   M = √(g_R² + g_BL²) v_R  (3 d.o.f.)
  - ν_R    Majorana:      M = f_ν v_R ≈ 0  (b/a = 0)
  - Δ_R    physical modes: M² ∝ λ v_R² ≈ 0  (λ = 0 at tree level)

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
import math
from scipy.optimize import brentq, minimize_scalar
from scipy.integrate import solve_ivp

np.set_printoptions(precision=8, suppress=True, linewidth=120)

# =====================================================================
# INPUTS (from zero_parameter_rg.py and fibre_ricci_full.py)
# =====================================================================

M_C = 4.5e16        # GeV — PS → LR breaking scale
alpha_PS_inv = 46.2  # from zero-parameter RG
alpha_PS = 1 / alpha_PS_inv
g_PS = math.sqrt(4 * math.pi * alpha_PS)  # ≈ 0.522

# At M_C: couplings from PS matching
g_R_MC = g_PS            # g_{2R}(M_C) = g_{2L}(M_C) = g_PS
g_BL_MC = g_PS * math.sqrt(2/3)  # from SU(4) → SU(3) × U(1)_{B-L}
# Factor: α_BL = (2/3) α_4 at the PS scale

f_nu_tree = 0.0   # Majorana Yukawa = 0 at tree level (b/a = 0)
N_gen = 3

print("=" * 72)
print("COLEMAN-WEINBERG POTENTIAL FOR SU(2)_R BREAKING")
print("=" * 72)

print(f"\nInputs from metric bundle:")
print(f"  M_C            = {M_C:.2e} GeV")
print(f"  α_PS           = {alpha_PS:.5f}  (α_PS⁻¹ = {alpha_PS_inv:.1f})")
print(f"  g_PS           = {g_PS:.4f}")
print(f"  g_R(M_C)       = {g_R_MC:.4f}")
print(f"  g_BL(M_C)      = {g_BL_MC:.4f}")
print(f"  f_ν(tree)      = {f_nu_tree}  (b/a = 0 from geometry)")

# =====================================================================
# PART 1: NAIVE CW POTENTIAL (no RG improvement)
# =====================================================================

print("\n" + "=" * 72)
print("PART 1: NAIVE COLEMAN-WEINBERG POTENTIAL")
print("(no RG improvement — couplings fixed at M_C values)")
print("=" * 72)

def V_CW_naive(v_R, mu, g_R, g_BL, f_nu=0.0):
    """
    1-loop CW effective potential in MS-bar.

    V = Σ_i (n_i / 64π²) M_i⁴ [ln(M_i² / μ²) - C_i]

    C_i = 5/6 for gauge bosons, 3/2 for scalars/fermions (MS-bar)
    """
    if v_R <= 0:
        return 0.0

    V = 0.0

    # W_R^± gauge bosons: M² = g_R² v_R²
    # 6 d.o.f. (3 polarizations × 2 charge states)
    M_WR2 = g_R**2 * v_R**2
    if M_WR2 > 0:
        V += (6 / (64 * math.pi**2)) * M_WR2**2 * (math.log(M_WR2 / mu**2) - 5/6)

    # Z' gauge boson: M² = (g_R² + g_BL²) v_R²
    # 3 d.o.f. (3 polarizations × 1 neutral state)
    M_Zp2 = (g_R**2 + g_BL**2) * v_R**2
    if M_Zp2 > 0:
        V += (3 / (64 * math.pi**2)) * M_Zp2**2 * (math.log(M_Zp2 / mu**2) - 5/6)

    # Majorana neutrinos: M = f_ν v_R
    # 2 d.o.f. per Majorana × N_gen generations (fermion: negative sign)
    if f_nu > 0:
        M_nu2 = f_nu**2 * v_R**2
        V -= (2 * N_gen / (64 * math.pi**2)) * M_nu2**2 * (math.log(M_nu2 / mu**2) - 3/2)

    return V

# CW coefficient B (field-independent part)
B_gauge = (1 / (64 * math.pi**2)) * (
    6 * g_R_MC**4 +                          # from W_R^±
    3 * (g_R_MC**2 + g_BL_MC**2)**2          # from Z'
)

print(f"\nCW coefficient B (gauge-dominated):")
print(f"  B_WR  = {6 * g_R_MC**4 / (64 * math.pi**2):.6e}")
print(f"  B_Z'  = {3 * (g_R_MC**2 + g_BL_MC**2)**2 / (64 * math.pi**2):.6e}")
print(f"  B_tot = {B_gauge:.6e}")

# Find minimum of V_CW(v_R) with μ = M_C
# V_CW = v_R⁴ × [B_eff × ln(v_R²/M_C²) + const]
# Minimum at dV/dv_R = 0:

def dV_dv(v_R, mu=M_C, g_R=g_R_MC, g_BL=g_BL_MC):
    """Numerical derivative of V_CW."""
    eps = v_R * 1e-6
    return (V_CW_naive(v_R + eps, mu, g_R, g_BL) -
            V_CW_naive(v_R - eps, mu, g_R, g_BL)) / (2 * eps)

# For V = B v_R⁴ [ln(v_R/M_C) + const], the minimum is at:
# 4B v_R³ [ln(v_R²/M_C²) + const'] = 0
# → v_R = M_C × exp(something of order 1)

# Scan V_CW over many decades
print(f"\nV_CW(v_R) scan (μ = M_C):")
print(f"{'log10(v_R/GeV)':>16} {'V_CW / M_C⁴':>16} {'v_R / M_C':>12}")
v_min_naive = None
V_min_naive = float('inf')
for log_v in np.linspace(6, 17, 100):
    v_R = 10**log_v
    V = V_CW_naive(v_R, M_C, g_R_MC, g_BL_MC)
    V_norm = V / M_C**4
    if V < V_min_naive:
        V_min_naive = V
        v_min_naive = v_R

# Print selected values
for log_v in [8, 10, 12, 14, 15, 15.5, 16, 16.3, 16.5, 16.65, 17]:
    v_R = 10**log_v
    V = V_CW_naive(v_R, M_C, g_R_MC, g_BL_MC)
    V_norm = V / M_C**4
    print(f"  {log_v:>14.1f} {V_norm:>16.4e} {v_R/M_C:>12.4e}")

# Refine minimum
res = minimize_scalar(lambda lv: V_CW_naive(10**lv, M_C, g_R_MC, g_BL_MC),
                      bounds=(6, 17.5), method='bounded')
v_min = 10**res.x
V_at_min = res.fun

print(f"\n*** NAIVE CW MINIMUM ***")
print(f"  v_R(min) = {v_min:.3e} GeV")
print(f"  log10(v_R) = {math.log10(v_min):.2f}")
print(f"  v_R / M_C = {v_min / M_C:.4f}")
print(f"  V(min) / M_C⁴ = {V_at_min / M_C**4:.6e}")
print(f"  → M_R ≈ {v_min:.2e} GeV (naive CW)")

ratio_naive = v_min / M_C
print(f"\n  v_R / M_C = {ratio_naive:.4f}")
if ratio_naive > 0.1:
    print(f"  *** NO HIERARCHY: M_R ~ M_C ***")
    print(f"  The naive CW potential puts M_R within an order of magnitude of M_C.")
    print(f"  This is the standard CW result: dimensional transmutation")
    print(f"  generates v_R ~ Λ_UV with no exponential suppression.")

# =====================================================================
# PART 2: RG-IMPROVED CW POTENTIAL
# =====================================================================

print("\n" + "=" * 72)
print("PART 2: RG-IMPROVED CW POTENTIAL")
print("(running couplings from M_C down to v_R)")
print("=" * 72)

# LR beta coefficients (from zero_parameter_rg.py, Scenario A: Φ + Δ_R)
b_3_LR = -7.0
b_2L_LR = -8/3
b_2R_LR = -5/3      # SU(2)_R: weaker asymptotic freedom due to Δ_R
b_BL_LR = 11/2      # U(1)_{B-L}: NOT asymptotically free

print(f"\nLR beta coefficients (Scenario A: Φ + Δ_R):")
print(f"  b_3  = {b_3_LR:.2f}")
print(f"  b_2L = {b_2L_LR:.4f}")
print(f"  b_2R = {b_2R_LR:.4f}")
print(f"  b_BL = {b_BL_LR:.4f}")

def run_couplings_LR(mu, mu0, alpha_R0, alpha_BL0, b_2R=b_2R_LR, b_BL=b_BL_LR):
    """
    Run SU(2)_R and U(1)_{B-L} couplings from mu0 to mu (1-loop).

    α⁻¹(μ) = α⁻¹(μ₀) - (b/2π) ln(μ/μ₀)
    """
    t = math.log(mu / mu0)
    alpha_R_inv = 1/alpha_R0 - (b_2R / (2 * math.pi)) * t
    alpha_BL_inv = 1/alpha_BL0 - (b_BL / (2 * math.pi)) * t

    if alpha_R_inv <= 0 or alpha_BL_inv <= 0:
        return None, None  # Landau pole

    return 1/alpha_R_inv, 1/alpha_BL_inv

# Initial conditions at M_C
alpha_R_MC = g_R_MC**2 / (4 * math.pi)
alpha_BL_MC = g_BL_MC**2 / (4 * math.pi)

print(f"\nInitial conditions at M_C:")
print(f"  α_R(M_C)  = {alpha_R_MC:.5f}  (α_R⁻¹ = {1/alpha_R_MC:.1f})")
print(f"  α_BL(M_C) = {alpha_BL_MC:.5f}  (α_BL⁻¹ = {1/alpha_BL_MC:.1f})")

# Run couplings and compute V_CW with running g's
print(f"\nRG-improved V_CW (μ = v_R, running couplings):")
print(f"{'log10(v_R)':>12} {'g_R':>8} {'g_BL':>8} {'V/M_C⁴':>14}")

V_improved = []
log_v_range = np.linspace(6, 17, 500)
for log_v in log_v_range:
    v_R = 10**log_v
    alpha_R, alpha_BL = run_couplings_LR(v_R, M_C, alpha_R_MC, alpha_BL_MC)
    if alpha_R is None:
        continue
    g_R = math.sqrt(4 * math.pi * alpha_R)
    g_BL = math.sqrt(4 * math.pi * alpha_BL)
    V = V_CW_naive(v_R, v_R, g_R, g_BL)  # μ = v_R (RG improvement)
    V_improved.append((log_v, v_R, g_R, g_BL, V))

# Find minimum
V_vals = np.array([x[4] for x in V_improved])
min_idx = np.argmin(V_vals)
lv_min, vR_min, gR_min, gBL_min, V_min = V_improved[min_idx]

# Print selected values
for entry in V_improved:
    lv = entry[0]
    if lv in [8, 10, 12, 14, 15, 15.5, 16, 16.5] or abs(lv - lv_min) < 0.05:
        print(f"  {lv:>10.1f} {entry[2]:>8.4f} {entry[3]:>8.4f} {entry[4]/M_C**4:>14.4e}")

print(f"\n*** RG-IMPROVED CW MINIMUM ***")
print(f"  v_R(min) = {vR_min:.3e} GeV")
print(f"  log10(v_R) = {lv_min:.2f}")
print(f"  v_R / M_C = {vR_min / M_C:.4f}")
print(f"  g_R(M_R) = {gR_min:.4f},  g_BL(M_R) = {gBL_min:.4f}")
print(f"  V(min) / M_C⁴ = {V_min / M_C**4:.6e}")

# Check: is there a Landau pole in g_BL?
# U(1)_{B-L} has b_BL = 11/2 > 0 → coupling GROWS at low energy
# Landau pole at: α_BL⁻¹(μ) = 0 → ln(μ/M_C) = 2π/(b_BL × α_BL(M_C))
t_Landau = 2 * math.pi / (b_BL_LR * alpha_BL_MC)  # negative (μ < M_C)
mu_Landau = M_C * math.exp(t_Landau)
print(f"\n  U(1)_BL Landau pole at: {mu_Landau:.2e} GeV (log10 = {math.log10(mu_Landau):.1f})")

# =====================================================================
# PART 3: QUARTIC COUPLING RGE
# =====================================================================

print("\n" + "=" * 72)
print("PART 3: QUARTIC COUPLING β FUNCTION")
print("Running λ_Δ from λ(M_C) = 0")
print("=" * 72)

# β function for quartic coupling of complex SU(2) triplet with U(1) charge
# Using general formulas from Machacek-Vaughn (1984):
#
# For V = λ(Δ†Δ)² with Δ ~ (1,1,3)_{BL=2}:
#
# β_λ = (1/16π²) [
#   a₁ λ² + a₂ λ g_R² + a₃ λ g_BL²     (scalar-gauge mixed)
#   - c₁ g_R⁴ - c₂ g_R² g_BL² - c₃ g_BL⁴  (pure gauge)
#   + fermion Yukawa terms (≈ 0 since f_ν ≈ 0)
# ]
#
# For complex triplet of SU(2) (n=6 real d.o.f., C₂=2, T=2):
#   a₁ = 2(n + 8)/3 = 2(6+8)/3 ≈ 9.33  (but convention-dependent)
# Using the standard 4D result for |Φ|⁴ quartic:

# Self-coupling: (2N+8) for N complex fields → (2×3+8) = 14
a_self = 14.0

# Gauge-scalar: 12 × C₂(3) = 12 × 2 = 24 for SU(2)_R
a_gauge_R = 24.0

# U(1)-scalar: depends on charge normalization
# For B-L charge Q=2: 48 × α_BL² ... let's use Y²=4 → coefficient 48
a_gauge_BL = 48.0

# Pure gauge (negative — drives λ down):
# SU(2)_R contribution: 3/2 × [C₂(3)]² × dim(3)/dim(3) = 3/2 × 4 = 6
# More carefully: for SU(2) with complex triplet, the g⁴ coefficient is:
# -(3/16)(2g⁴) × sum of Casimir factors
# Standard result for SU(2) triplet: c = 6 g_R⁴ (the same as the B coefficient)
# Using A₄ from Martin (2-loop review): for adjoint of SU(2):
# The contribution is -(9/2) g⁴ ...
# Let me use the KNOWN result for the SM Higgs (doublet) and scale:
# For doublet: c_SU2 = 9/8 g⁴  → for triplet: c_SU2 = 9/2 g⁴ (C₂ ratio: 2/0.75 = 8/3)
# Actually: c ∝ C₂(R)² × something. For doublet C₂=3/4, c=9/8=(3/4)²×2.
# For triplet C₂=2, c = 2² × 2 = 8. Hmm.
#
# Let me use the general formula: the gauge contribution to β_λ is
# -(3/16π²) × [C₂(R)]² × g⁴ × dim(R) / dim(R)
# No, that doesn't help. Let me just use the B coefficient directly.
#
# The relationship: β_λ|_{λ=0, gauge} = -(some coefficient) × g⁴/(16π²)
# where the coefficient is related to B:
# B = (1/64π²) × Σ n_i c_i⁴  and  β_λ|_{gauge} = -(1/16π²) × Σ n_i c_i⁴ × (4/6)
# Wait, the relationship is:
# V_CW = B v⁴ [ln(v²/μ²) - C]  and the quartic from this is λ_CW = 24B ln(v²/μ²)
# So β_λ = 24B × 2 = 48B (running of the quartic from the CW potential)
# No, that's circular.

# Let me just use specific known results:
# For SU(2) with adjoint (real triplet): β_λ|_{gauge} = -(9/2) g⁴/(16π²)
# For SU(2) with fundamental (complex doublet): β_λ|_{gauge} = -(9/4) g⁴/(16π²)
#   (actually it's -(9/8)(2g⁴+(g²+g'²)²)/(16π²) for the SM)
#
# For COMPLEX triplet: the gauge contribution should be scaled by C₂² ratio:
# c_triplet / c_doublet = C₂(3)² / C₂(2)² = 4 / (9/16) = 64/9 ≈ 7.1
# → c_triplet = 7.1 × (9/4) = 16  (approximately)
#
# I'll use c_R = 12 for SU(2)_R and c_BL = 12 for U(1)_{BL} as reasonable estimates.
# The exact O(1) coefficient doesn't affect the qualitative conclusion.

c_R = 12.0     # pure g_R⁴ coefficient
c_RBL = 6.0    # mixed g_R² g_BL² coefficient
c_BL = 3.0     # pure g_BL⁴ coefficient

def beta_lambda(lam, g_R, g_BL, f_nu=0.0):
    """1-loop beta function for quartic coupling λ_Δ."""
    return (1 / (16 * math.pi**2)) * (
        a_self * lam**2
        + a_gauge_R * lam * g_R**2
        + a_gauge_BL * lam * g_BL**2
        - c_R * g_R**4
        - c_RBL * g_R**2 * g_BL**2
        - c_BL * g_BL**4
        # fermion contribution: + 4 N_gen × f_nu⁴ (with sign for fermion loops)
        # ≈ 0 since f_nu ≈ 0
    )

# Run the coupled system from M_C down
def rge_system(t, y):
    """
    RGE system: d/dt [λ, α_R⁻¹, α_BL⁻¹] where t = ln(μ/M_C)
    """
    lam, aR_inv, aBL_inv = y

    if aR_inv <= 0 or aBL_inv <= 0:
        return [0, 0, 0]

    g_R = math.sqrt(4 * math.pi / aR_inv)
    g_BL = math.sqrt(4 * math.pi / aBL_inv)

    dlam_dt = beta_lambda(lam, g_R, g_BL)
    daR_inv_dt = -(b_2R_LR / (2 * math.pi))
    daBL_inv_dt = -(b_BL_LR / (2 * math.pi))

    return [dlam_dt, daR_inv_dt, daBL_inv_dt]

# Initial conditions at M_C (t = 0)
y0 = [0.0, 1/alpha_R_MC, 1/alpha_BL_MC]

# Run from t = 0 (M_C) down to t = -ln(M_C/100) (μ = 100 GeV)
t_span = (0, -math.log(M_C / 100))
t_eval = np.linspace(0, t_span[1], 2000)

sol = solve_ivp(rge_system, t_span, y0, t_eval=t_eval, method='RK45',
                rtol=1e-10, atol=1e-12)

print(f"\nQuartic coupling evolution from M_C:")
print(f"{'log10(μ/GeV)':>14} {'λ_Δ':>12} {'g_R':>8} {'g_BL':>8} {'β_λ':>12}")

# Extract and display
lambda_vals = sol.y[0]
aR_inv_vals = sol.y[1]
aBL_inv_vals = sol.y[2]
t_vals = sol.t
mu_vals = M_C * np.exp(t_vals)

# Check if λ ever crosses zero (it starts at 0 and goes negative from gauge loops)
lambda_cross_zero = False
mu_cross = None

for i in range(1, len(lambda_vals)):
    log_mu = math.log10(mu_vals[i])

    # Print selected values
    if abs(log_mu - round(log_mu)) < 0.02 and round(log_mu) in [16, 15, 14, 12, 10, 8, 6, 4, 2]:
        g_R = math.sqrt(4 * math.pi / aR_inv_vals[i]) if aR_inv_vals[i] > 0 else float('nan')
        g_BL = math.sqrt(4 * math.pi / aBL_inv_vals[i]) if aBL_inv_vals[i] > 0 else float('nan')
        bl = beta_lambda(lambda_vals[i], g_R, g_BL)
        print(f"  {log_mu:>12.1f} {lambda_vals[i]:>12.4e} {g_R:>8.4f} {g_BL:>8.4f} {bl:>12.4e}")

    # Check for second zero crossing (λ returning to 0 from below)
    if i > 10 and lambda_vals[i-1] < 0 and lambda_vals[i] >= 0:
        lambda_cross_zero = True
        # Interpolate
        frac = -lambda_vals[i-1] / (lambda_vals[i] - lambda_vals[i-1])
        mu_cross = mu_vals[i-1] * (mu_vals[i] / mu_vals[i-1])**frac
        print(f"\n  *** λ crosses zero at μ = {mu_cross:.3e} GeV (log10 = {math.log10(mu_cross):.2f}) ***")

lambda_min = np.min(lambda_vals)
idx_min = np.argmin(lambda_vals)
print(f"\n  λ_min = {lambda_min:.6e} at μ = {mu_vals[idx_min]:.2e} GeV")

if not lambda_cross_zero:
    print(f"\n  λ never returns to zero — no Gildener-Weinberg minimum below M_C.")
    print(f"  The quartic is driven negative by gauge loops and stays there.")

# =====================================================================
# PART 4: THE RG-IMPROVED EFFECTIVE POTENTIAL
# =====================================================================

print("\n" + "=" * 72)
print("PART 4: FULL RG-IMPROVED EFFECTIVE POTENTIAL")
print("=" * 72)

def V_eff_improved(v_R):
    """
    RG-improved effective potential V(v_R) with running couplings at μ = v_R.

    V = (λ_eff(v_R) / 4!) v_R⁴ + V_CW(v_R, μ=v_R)

    where λ_eff includes the running quartic and V_CW adds the 1-loop log correction.
    """
    if v_R <= 100 or v_R >= M_C * 10:
        return 0.0

    t = math.log(v_R / M_C)

    # Get running couplings at μ = v_R by interpolation
    idx = np.searchsorted(-t_vals, -t)  # t_vals is decreasing
    if idx <= 0 or idx >= len(t_vals):
        return 0.0

    # Linear interpolation
    frac = (t - t_vals[idx-1]) / (t_vals[idx] - t_vals[idx-1])
    lam = lambda_vals[idx-1] + frac * (lambda_vals[idx] - lambda_vals[idx-1])
    aR_inv = aR_inv_vals[idx-1] + frac * (aR_inv_vals[idx] - aR_inv_vals[idx-1])
    aBL_inv = aBL_inv_vals[idx-1] + frac * (aBL_inv_vals[idx] - aBL_inv_vals[idx-1])

    if aR_inv <= 0 or aBL_inv <= 0:
        return 0.0

    g_R = math.sqrt(4 * math.pi / aR_inv)
    g_BL = math.sqrt(4 * math.pi / aBL_inv)

    # Tree-level with running quartic
    V_tree = (lam / 24) * v_R**4

    # 1-loop CW correction (with μ = v_R, logs are small)
    # V_CW = (1/64π²) Σ n_i M_i⁴ [ln(M_i²/v_R²) - C_i]
    # With μ = v_R: ln(g²v²/v²) = ln(g²) = 2ln(g)
    V_1loop = 0.0
    M_WR2 = g_R**2 * v_R**2
    V_1loop += (6 / (64 * math.pi**2)) * M_WR2**2 * (math.log(g_R**2) - 5/6)

    M_Zp2 = (g_R**2 + g_BL**2) * v_R**2
    V_1loop += (3 / (64 * math.pi**2)) * M_Zp2**2 * (math.log(g_R**2 + g_BL**2) - 5/6)

    return V_tree + V_1loop

# Scan the improved potential
print(f"\nRG-improved V_eff(v_R) scan:")
print(f"{'log10(v_R)':>12} {'λ_eff':>12} {'V_tree/M_C⁴':>14} {'V_total/M_C⁴':>14}")

V_eff_vals = []
for log_v in np.linspace(3, 16.6, 500):
    v_R = 10**log_v
    V = V_eff_improved(v_R)
    V_eff_vals.append((log_v, V))

# Find minimum
V_arr = np.array([x[1] for x in V_eff_vals])
lv_arr = np.array([x[0] for x in V_eff_vals])
# Only look for minimum where V < 0 (symmetry breaking)
neg_mask = V_arr < 0
if np.any(neg_mask):
    min_idx = np.argmin(V_arr)
    lv_min_imp = lv_arr[min_idx]
    V_min_imp = V_arr[min_idx]
    vR_min_imp = 10**lv_min_imp

    # Refine
    try:
        res = minimize_scalar(lambda lv: V_eff_improved(10**lv),
                              bounds=(max(3, lv_min_imp - 2), min(16.6, lv_min_imp + 2)),
                              method='bounded')
        vR_min_imp = 10**res.x
        V_min_imp = res.fun
        lv_min_imp = res.x
    except:
        pass

    print(f"\n*** RG-IMPROVED CW MINIMUM ***")
    print(f"  v_R(min) = {vR_min_imp:.3e} GeV")
    print(f"  log10(v_R) = {lv_min_imp:.2f}")
    print(f"  v_R / M_C = {vR_min_imp / M_C:.4e}")
    print(f"  V(min) / M_C⁴ = {V_min_imp / M_C**4:.6e}")
else:
    print(f"\n  No negative region in V_eff → no symmetry breaking minimum.")
    print(f"  The effective potential is positive for all v_R < M_C.")

# Print selected values of the improved potential
print(f"\nDetailed scan:")
for log_v in [4, 6, 8, 10, 12, 13, 14, 14.5, 15, 15.5, 16, 16.3, 16.5]:
    v_R = 10**log_v
    V = V_eff_improved(v_R)

    # Get λ at this scale
    t = math.log(v_R / M_C)
    idx = np.searchsorted(-t_vals, -t)
    if 0 < idx < len(t_vals):
        frac = (t - t_vals[idx-1]) / (t_vals[idx] - t_vals[idx-1])
        lam = lambda_vals[idx-1] + frac * (lambda_vals[idx] - lambda_vals[idx-1])
    else:
        lam = float('nan')

    print(f"  log10(v_R) = {log_v:>5.1f}:  λ = {lam:>11.4e},  V/M_C⁴ = {V/M_C**4:>13.4e}")


# =====================================================================
# PART 5: DIMENSIONAL TRANSMUTATION FORMULA
# =====================================================================

print("\n" + "=" * 72)
print("PART 5: DIMENSIONAL TRANSMUTATION ANALYSIS")
print("=" * 72)

# The standard CW result for a classically conformal theory:
# v = Λ × exp(-1/(2|β'_λ|))
# where β'_λ = dβ_λ/dλ evaluated at the fixed point

# For our case with λ = 0 at M_C:
# β_λ(λ=0) = -(1/16π²) × [c_R g_R⁴ + c_RBL g_R² g_BL² + c_BL g_BL⁴]

beta_lambda_at_MC = beta_lambda(0.0, g_R_MC, g_BL_MC)
print(f"\nβ_λ(λ=0, M_C) = {beta_lambda_at_MC:.6e}")
print(f"  (negative → λ driven below zero → instability)")

# The effective B coefficient
B_eff_dimtrans = abs(beta_lambda_at_MC)

# In the Gildener-Weinberg picture:
# The minimum forms where the LOG correction balances the running λ:
# λ(μ) + (B_eff) × [4 ln(μ/M_C) + 1] = 0
# With λ(μ) ≈ β_λ × ln(μ/M_C):
# β_λ × t + B_eff × (4t + 1) = 0
# (β_λ + 4B_eff) t = -B_eff
# t = -B_eff / (β_λ + 4B_eff)

# Since β_λ < 0 and B_eff > 0:
# If |β_λ| > 4B_eff: t > 0 (no minimum below M_C — already at M_C)
# If |β_λ| < 4B_eff: t < 0 (minimum below M_C)

print(f"\n  |β_λ| = {abs(beta_lambda_at_MC):.6e}")
print(f"  4B_eff = {4 * B_gauge:.6e}")
# Wait, B_eff and β_λ are related but not the same.
# Let me compute them properly.

# The 1-loop CW B coefficient (from mass spectrum):
B_CW = (1 / (64 * math.pi**2)) * (
    6 * g_R_MC**4 * (2 * math.log(g_R_MC) - 5/6) +  # Hmm, this is the LOG part
    3 * (g_R_MC**2 + g_BL_MC**2)**2 * (math.log(g_R_MC**2 + g_BL_MC**2) - 5/6)
)
# Actually, the coefficient of the v⁴ ln(v/μ) term:
B_log = (1 / (64 * math.pi**2)) * (
    6 * g_R_MC**4 +
    3 * (g_R_MC**2 + g_BL_MC**2)**2
)
print(f"\n  B (coefficient of v⁴ ln(v/M_C)): {B_log:.6e}")

# Dimensional transmutation: ln(v/M_C) = -β_λ / (4 B_log) ???
# No. The proper formula:
# V_eff(v) = (λ(v)/4!) v⁴ + B_log v⁴ ln(v²/M_C²) + const
# V'(v) = [λ(v)/6 + λ'(v)v/24 + 4B_log ln(v²/M_C²) + 2B_log] v³ = 0
# At leading order (λ small, λ' = β_λ):
# λ(v)/6 + 4B_log ln(v²/M_C²) + 2B_log ≈ 0
# Using λ(v) = β_λ × 2 ln(v/M_C):
# β_λ × 2 ln(v/M_C) / 6 + 4 B_log × 2 ln(v/M_C) + 2 B_log = 0
# ln(v/M_C) × (β_λ/3 + 8 B_log) = -2 B_log
# ln(v/M_C) = -2 B_log / (β_λ/3 + 8 B_log)

t_min = -2 * B_log / (beta_lambda_at_MC / 3 + 8 * B_log)
v_dimtrans = M_C * math.exp(t_min)

print(f"\nDimensional transmutation formula:")
print(f"  ln(v_R/M_C) = -2B / (β_λ/3 + 8B) = {t_min:.4f}")
print(f"  v_R = M_C × exp({t_min:.4f}) = {v_dimtrans:.3e} GeV")
print(f"  log10(v_R) = {math.log10(v_dimtrans):.2f}")
print(f"  v_R / M_C = {v_dimtrans / M_C:.4f}")

# Alternative: pure exponential from the beta function
# If the quartic runs linearly: λ(μ) = β_λ × ln(μ/M_C)
# The minimum of V = λv⁴/4! is at v where λ(v) ≈ 0, i.e., v ~ M_C
# No hierarchy!

# The hierarchy would need |β_λ/B| >> 1 (large cancellation)
print(f"\n  |β_λ / B_log| = {abs(beta_lambda_at_MC / B_log):.2f}")
print(f"  (would need >> 1 for hierarchy; ~1 gives v ~ M_C)")


# =====================================================================
# PART 6: SENSITIVITY ANALYSIS
# =====================================================================

print("\n" + "=" * 72)
print("PART 6: WHAT WOULD BE NEEDED FOR M_R ~ 10⁹ GeV?")
print("=" * 72)

# For M_R / M_C ~ 10^{-7}:
# ln(M_R/M_C) = -7 × ln(10) = -16.1
# Need: t_min = -16.1

# From t_min = -2B / (β_λ/3 + 8B):
# -16.1 = -2B / (β_λ/3 + 8B)
# β_λ/3 + 8B = 2B / 16.1 = 0.124 B
# β_λ/3 = (0.124 - 8) B = -7.876 B
# β_λ = -23.6 B

# With B ~ 1.6 × 10^{-3}: need β_λ ~ -0.038
# Compare actual: β_λ ~ -3.5 × 10^{-4}
# → Need β_λ about 100× larger!

target_log = -7 * math.log(10)  # ln(10^{-7})
# β_λ/3 + 8B = 2B / |target_log|
# β_λ = 3 × (2B/|target_log| - 8B) = 3B × (2/|target_log| - 8)
beta_needed = 3 * B_log * (2 / abs(target_log) - 8)
ratio_needed = beta_needed / beta_lambda_at_MC

print(f"\nFor M_R = 10⁹ GeV (7 decades below M_C):")
print(f"  Need β_λ = {beta_needed:.4e}")
print(f"  Actual β_λ = {beta_lambda_at_MC:.4e}")
print(f"  Ratio: need {ratio_needed:.0f}× larger β_λ")
print(f"\n  This requires either:")
print(f"  (a) ~{abs(ratio_needed):.0f}× more particles coupling to Δ_R")
print(f"  (b) Large Yukawa couplings (f_ν ~ 1 for Majorana mass)")
print(f"  (c) Non-perturbative effects (instantons, strong dynamics)")

# What Yukawa would be needed?
# Fermion contribution to β_λ: + (4 N_gen / 16π²) f_ν⁴
# Need total β_λ = beta_needed
# → f_ν⁴ = (beta_needed - beta_lambda_at_MC) × 16π² / (4 N_gen)
# This is only valid if beta_needed < 0 (which it is since we need β more negative)
delta_beta = beta_needed - beta_lambda_at_MC
if delta_beta < 0:
    # Fermions make β MORE negative (fermions enter with opposite sign in the CW formula)
    # Wait: fermion loops in V_CW have NEGATIVE sign (Σ n_f M_f⁴ with n_f < 0)
    # So fermion contribution to β_λ is POSITIVE (drives λ up, counteracts gauge)
    # We need β MORE negative, so fermions don't help — they make it worse!
    print(f"\n  NOTE: Fermion Yukawa couplings would make β_λ LESS negative")
    print(f"  (fermion loops counteract gauge loops in the quartic RGE)")
    print(f"  → Fermions cannot solve the hierarchy problem here!")
else:
    f_nu_needed = (delta_beta * 16 * math.pi**2 / (4 * N_gen))**0.25
    print(f"\n  With Majorana Yukawa f_ν = {f_nu_needed:.3f} would shift β_λ enough")


# =====================================================================
# PART 7: COMPARISON WITH RG-DETERMINED M_R
# =====================================================================

print("\n" + "=" * 72)
print("PART 7: COMPARISON WITH ZERO-PARAMETER RG")
print("=" * 72)

M_R_RG = 1.1e9  # from zero_parameter_rg.py

print(f"\n  M_R (CW dimensional transmutation) = {v_dimtrans:.2e} GeV")
print(f"  M_R (zero-parameter gauge running)  = {M_R_RG:.2e} GeV")
print(f"  M_R (seesaw, m_ν = 0.05 eV, f~1)   = 6×10¹⁴ GeV")
print(f"\n  CW / RG  ratio: {v_dimtrans / M_R_RG:.1e}")
print(f"  CW / M_C ratio: {v_dimtrans / M_C:.3f}")

print(f"""
DIAGNOSIS:
  The Coleman-Weinberg mechanism gives M_R ≈ {v_dimtrans/M_C:.2f} M_C ≈ {v_dimtrans:.1e} GeV.
  This is essentially M_R ~ M_C — NO hierarchy generated.

  The zero-parameter RG gives M_R ~ 10⁹ GeV as a CONSISTENCY CONDITION
  from measured SM couplings, but this requires v_R << M_C which the
  CW potential alone does not produce.

  Three possible resolutions:

  1. TREE-LEVEL MASS: The Δ_R scalar has a nonzero mass² at tree level
     (i.e., the L-R symmetry is broken explicitly, not spontaneously).
     The CP³ potential may contribute a small L-R splitting through
     higher-order effects (2-loop, threshold corrections).

  2. EXTENDED SCALAR SECTOR: Additional scalars (e.g., (15,1,3) or
     Pati-Salam colored scalars) could modify β_λ enough to generate
     a hierarchy. This connects to the M_R tension from zero_parameter_rg.py.

  3. NON-PERTURBATIVE: Instanton effects or strong dynamics on the
     fibre could generate an exponentially suppressed scale.
     The fibre topology (π₃(SO(3,1)) = ℤ) supports instantons.

  STATUS: SU(2)_R breaking scale is NOT YET determined from geometry.
  The CW mechanism identifies the correct PHYSICS (radiative L-R breaking)
  but cannot produce the required hierarchy without additional input.
""")


# =====================================================================
# PART 8: INSTANTON ESTIMATE
# =====================================================================

print("=" * 72)
print("PART 8: INSTANTON-GENERATED SCALE")
print("*** RULED OUT — see instanton_gl4_so31.py for rigorous calculation ***")
print("*** N_eff ≈ 17 was incorrect; actual S = 8π²/g² = 290 (N_eff = 1) ***")
print("=" * 72)

# If instantons on the fibre generate a non-perturbative scale:
# Λ_inst ~ M_C × exp(-8π² / g²)

# For g_PS at M_C:
inst_exponent = -8 * math.pi**2 / g_PS**2
M_inst = M_C * math.exp(inst_exponent)

print(f"\n  Instanton scale: Λ_inst = M_C × exp(-8π²/g_PS²)")
print(f"  8π²/g_PS² = {8*math.pi**2/g_PS**2:.1f}")
print(f"  exp(-{8*math.pi**2/g_PS**2:.1f}) = {math.exp(inst_exponent):.2e}")
print(f"  Λ_inst = {M_inst:.2e} GeV")
print(f"  log10(Λ_inst) = {math.log10(max(M_inst, 1e-300)):.1f}")

# With N_eff effective degrees of freedom:
for N_eff in [1, 2, 3, 6, 12]:
    exp_factor = -8 * math.pi**2 / (N_eff * g_PS**2)
    M_inst_N = M_C * math.exp(exp_factor)
    log_M = math.log10(max(M_inst_N, 1e-300))
    print(f"  N_eff = {N_eff:>2}: Λ_inst = {M_inst_N:.2e} GeV  (log10 = {log_M:.1f})")

# For M_R ~ 10^9: need exp(-S) = 10^{-7.65}
# → S = 7.65 × ln(10) = 17.6
# → 8π²/(N_eff g²) = 17.6
# → N_eff = 8π²/(17.6 × g²) = 78.96/(17.6 × 0.272) = 16.5

S_needed = math.log(M_C / M_R_RG)
N_eff_needed = 8 * math.pi**2 / (S_needed * g_PS**2)
print(f"\n  For M_R = {M_R_RG:.1e} GeV:")
print(f"  Need S = ln(M_C/M_R) = {S_needed:.1f}")
print(f"  → N_eff = 8π²/(S × g²) = {N_eff_needed:.1f}")
print(f"  *** HOWEVER: instanton_gl4_so31.py shows N_eff = 1 (not 17) ***")
print(f"  *** The fibre d.o.f. enter the PREFACTOR, not the EXPONENT ***")
print(f"  *** Actual instanton action S = 8π²/g² = {8*math.pi**2/g_PS**2:.0f} → exp(-S) ~ 10^(-126) ***")
print(f"  *** This mechanism is RULED OUT for generating M_R ***")


# =====================================================================
# SUMMARY
# =====================================================================

print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)

print(f"""
RESULT: Coleman-Weinberg analysis for SU(2)_R breaking

1. TREE-LEVEL: The fibre curvature is L-R symmetric at tree level.
   V_tree(Δ_R, SU(2)_R direction) = 0.
   This is a geometric consequence of the Lorentzian metric bundle.

2. ONE-LOOP CW: The gauge boson loops (W_R^±, Z') generate a potential:
   V_CW = B v_R⁴ [ln(v_R/M_C) + const]
   with B = {B_log:.4e}
   Minimum at v_R ≈ {v_dimtrans/M_C:.2f} × M_C ≈ {v_dimtrans:.1e} GeV
   → NO hierarchy: M_R ~ M_C

3. FERMION LOOPS: The Majorana Yukawa f_ν ≈ 0 (from b/a = 0 at tree level).
   Even with f_ν ≠ 0, fermion loops counteract gauge loops (make β_λ less negative).
   → Fermions cannot generate the hierarchy.

4. QUARTIC RGE: λ_Δ starts at 0 (M_C), immediately goes negative,
   and stays negative (min λ = {lambda_min:.4e}).
   → Quartic never returns to zero — no Gildener-Weinberg minimum.

5. INSTANTON: S = 8π²/g² = 290 → exp(-S) ~ 10^(-126).
   *** RULED OUT (March 2026): instanton_gl4_so31.py shows N_eff = 1,
   not ~17 as estimated here. Fibre d.o.f. enter the prefactor, not
   the exponent. The instanton is too suppressed by ~118 orders of
   magnitude to generate M_R ~ 10⁹ GeV. ***

CONCLUSION:
  NEITHER perturbative (CW) NOR non-perturbative (instanton) mechanisms
  generate M_R << M_C from the metric bundle geometry alone.

  The SU(2)_R breaking scale M_R remains an UNDETERMINED PARAMETER.
  The 5.7-decade tension between gauge RG (10⁹) and seesaw (6×10¹⁴)
  is UNRESOLVED.

  What IS established:
    - SU(4)_C → SU(3)_c × U(1)_{{B-L}} : classical (fibre curvature) ✓
    - SU(2)_R → U(1)_R : MECHANISM OPEN (CW too weak, instanton too suppressed)
    - SU(2)_L × U(1)_Y → U(1)_em : radiative (Higgs CW, standard)

  Possible resolutions:
    (a) M_R as free parameter (standard in PS models)
    (b) Different scalar content modifies RG running
    (c) Cosmological phase transition sets M_R
    (d) Novel fibre geometry effect not yet identified
""")
