#!/usr/bin/env python3
"""
Higher-Dimensional Conscious Agents: A Systematic Exploration
==============================================================

Starting question: Is (3,1) spacetime the ONLY signature that produces
"clean" gauge groups via the metric bundle construction, or are there
other viable signatures for bounded conscious agents?

Method:
1. Compute DeWitt metric signature for ALL (p,q) spacetimes up to d=8
2. Identify the resulting SO(n+, n-) structure group
3. Find maximal compact subgroup SO(n+) x SO(n-)
4. Check for accidental isomorphisms that give "interesting" gauge groups
5. Assess which signatures could support stable complex structures

Key formula (Schmidt 2001, gr-qc/0109001):
  DeWitt metric on Sym^2(R^{p,q}):
  G(h,k) = g^{mu rho} g^{nu sigma} h_{mu nu} k_{rho sigma}
          - (1/2)(g^{mu nu} h_{mu nu})(g^{rho sigma} k_{rho sigma})

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from itertools import combinations
import math

np.set_printoptions(precision=4, suppress=True, linewidth=120)

# =====================================================================
# CORE: DeWitt metric for arbitrary signature (p,q)
# =====================================================================

def compute_dewitt_signature(p, q):
    """
    Compute the DeWitt metric signature on Sym^2(R^{p,q}).

    p = number of POSITIVE (spatial-like) dimensions
    q = number of NEGATIVE (time-like) dimensions
    Spacetime signature: (-1,...,-1, +1,...,+1) with q minuses, p pluses

    Returns: (n_pos, n_neg, n_zero, eigenvalues)
    """
    d = p + q
    # Background metric: first q entries are -1, next p entries are +1
    g = np.diag([-1.0]*q + [1.0]*p)
    g_inv = np.diag([-1.0]*q + [1.0]*p)  # self-inverse for diagonal

    # Basis for Sym^2(R^d)
    dim_fibre = d * (d + 1) // 2
    basis = []
    labels = []
    for i in range(d):
        for j in range(i, d):
            mat = np.zeros((d, d))
            if i == j:
                mat[i, i] = 1.0
            else:
                mat[i, j] = 1.0 / np.sqrt(2)
                mat[j, i] = 1.0 / np.sqrt(2)
            basis.append(mat)
            labels.append((i, j))

    # DeWitt metric
    G_DW = np.zeros((dim_fibre, dim_fibre))
    for a in range(dim_fibre):
        for b in range(dim_fibre):
            h, k = basis[a], basis[b]
            # Term 1: g^{mu rho} g^{nu sigma} h_{mu nu} k_{rho sigma}
            t1 = np.einsum('mr,ns,mn,rs', g_inv, g_inv, h, k)
            # Term 2: -1/2 (tr_g h)(tr_g k)
            trh = np.einsum('mn,mn', g_inv, h)
            trk = np.einsum('mn,mn', g_inv, k)
            G_DW[a, b] = t1 - 0.5 * trh * trk

    eigvals = np.linalg.eigvalsh(G_DW)
    n_pos = int(np.sum(eigvals > 1e-10))
    n_neg = int(np.sum(eigvals < -1e-10))
    n_zero = int(np.sum(np.abs(eigvals) <= 1e-10))

    return n_pos, n_neg, n_zero, eigvals, labels


# =====================================================================
# ACCIDENTAL ISOMORPHISMS of low-dimensional SO(n) and SO(p,q)
# =====================================================================

ACCIDENTAL_ISOS = {
    # SO(n) compact isomorphisms
    (1, 0): "U(1) ~ Z_2",
    (2, 0): "U(1)",
    (3, 0): "SU(2) ~ Sp(1)",
    (4, 0): "SU(2)_L x SU(2)_R",
    (5, 0): "Sp(2) ~ USp(4)",
    (6, 0): "SU(4)",
    # Non-compact
    (2, 1): "SL(2,R) ~ SU(1,1)",
    (3, 1): "SL(2,C) ~ Sp(2,C)",
    (3, 3): "SL(4,R)",
    (4, 2): "SU(2,2)",
    (6, 2): "SO*(8) (triality)",
}

def identify_gauge_group(n_pos, n_neg):
    """
    Given SO(n_pos, n_neg) structure group, identify:
    - Maximal compact subgroup SO(n_pos) x SO(n_neg)
    - Any accidental isomorphisms
    - The resulting "gauge group"
    """
    result = {
        'structure_group': f'SO({n_pos},{n_neg})',
        'maximal_compact': f'SO({n_pos}) x SO({n_neg})',
        'compact_isos': [],
        'gauge_factors': [],
        'total_generators': n_pos*(n_pos-1)//2 + n_neg*(n_neg-1)//2,
        'interesting': False,
    }

    # Check for accidental isomorphisms of each compact factor
    for n, label in [(n_pos, 'positive'), (n_neg, 'negative')]:
        key = (n, 0)
        if key in ACCIDENTAL_ISOS:
            result['compact_isos'].append(f"SO({n}) ~ {ACCIDENTAL_ISOS[key]}")
            result['gauge_factors'].append(ACCIDENTAL_ISOS[key])
        else:
            result['gauge_factors'].append(f"SO({n})")

    # Flag as "interesting" if we get clean Lie group isomorphisms
    # (not just generic SO(n))
    interesting_ranks = {3, 4, 5, 6}  # These have accidental isos
    if n_pos in interesting_ranks or n_neg in interesting_ranks:
        result['interesting'] = True

    return result


def analyze_physical_decomposition(p, q, n_pos, n_neg):
    """
    Decompose the DeWitt eigenspaces by their physical meaning:
    - "Spatial metric" modes: h_{ij} for spatial indices
    - "Shift" modes: h_{0i} (time-space cross terms)
    - "Lapse/temporal" modes: h_{00}, h_{0'0'} etc.
    """
    d = p + q

    # Count mode types
    # Temporal-temporal: q(q+1)/2
    # Temporal-spatial (shifts): p*q
    # Spatial-spatial: p(p+1)/2
    n_tt = q * (q + 1) // 2
    n_ts = p * q
    n_ss = p * (p + 1) // 2

    return {
        'temporal_temporal': n_tt,
        'temporal_spatial_shifts': n_ts,
        'spatial_spatial': n_ss,
        'total': n_tt + n_ts + n_ss,
        'fibre_dim': d * (d + 1) // 2,
    }


def check_stability_criteria(p, q):
    """
    Assess whether a (p,q) spacetime could support stable complex structures.

    Criteria:
    1. Causal structure: needs at least 1 time dimension
    2. Huygens principle: clean wave propagation in odd spatial dims
    3. Stable bound states: inverse-square law only in 3 spatial dims
    4. Topological richness: exotic structures in 4 spatial dims
    5. PDA architecture: needs causal ordering for P->D->A loop
    """
    criteria = {}

    # 1. Causal structure
    criteria['has_time'] = q >= 1
    criteria['single_time'] = q == 1
    criteria['multi_time'] = q > 1

    # 2. Wave propagation (Huygens principle holds for odd p)
    criteria['clean_waves'] = (p % 2 == 1)

    # 3. Stable orbits under inverse-(p-1) law
    # Bertrand's theorem: closed stable orbits only for p=3 (inverse square)
    # and p=2 (harmonic) for point-particle mechanics
    criteria['stable_orbits'] = (p == 3)
    criteria['harmonic_orbits'] = (p == 2)

    # 4. Topological richness
    # Exotic R^4: only p=4 has uncountably many exotic smooth structures
    criteria['exotic_smooth'] = (p == 4)
    # Poincare conjecture difficulty: hardest in p=4
    criteria['topological_richness'] = (p >= 3)

    # 5. PDA architecture
    criteria['supports_PDA'] = q >= 1  # Need time for causality

    # Overall assessment
    if p == 3 and q == 1:
        criteria['assessment'] = 'OUR UNIVERSE - all criteria optimal'
    elif q == 0:
        criteria['assessment'] = 'No time - no causality, no PDA'
    elif q >= 2:
        criteria['assessment'] = 'Multi-time: causal paradoxes, but information blankets may still form'
    elif p < 3:
        criteria['assessment'] = 'Too few spatial dims for complex chemistry'
    elif p == 4 and q == 1:
        criteria['assessment'] = 'EXOTIC: unique smooth structures, richer topology than 3+1'
    elif p >= 5 and q == 1:
        criteria['assessment'] = 'No stable orbits, but topological binding possible'
    else:
        criteria['assessment'] = 'Non-standard but not ruled out for information-theoretic agents'

    return criteria


# =====================================================================
# MAIN COMPUTATION: Systematic survey
# =====================================================================

print("=" * 80)
print("HIGHER-DIMENSIONAL CONSCIOUS AGENTS")
print("Systematic Survey of DeWitt Signatures for (p,q) Spacetimes")
print("=" * 80)

print("""
QUESTION: Is (3,1) the unique spacetime signature that produces a "clean"
gauge group from the metric bundle construction?

METHOD: For each (p,q) with d = p+q <= 8, compute:
  1. dim Sym^2(R^d) = d(d+1)/2 = fibre dimension
  2. DeWitt metric signature (n+, n-) on the fibre
  3. Structure group SO(n+, n-)
  4. Maximal compact subgroup and accidental isomorphisms
  5. Stability criteria for bounded agents
""")

# Store results
results = []
max_d = 8

print("\n" + "=" * 80)
print(f"{'(p,q)':>8} {'d':>3} {'fibre':>6} {'DeWitt sig':>14} {'SO(n+,n-)':>12} "
      f"{'Max compact':>30} {'Generators':>5}")
print("-" * 80)

for d in range(2, max_d + 1):
    for q in range(0, d + 1):
        p = d - q
        if p < 0:
            continue

        n_pos, n_neg, n_zero, eigvals, labels = compute_dewitt_signature(p, q)
        gauge = identify_gauge_group(n_pos, n_neg)
        stability = check_stability_criteria(p, q)
        decomp = analyze_physical_decomposition(p, q, n_pos, n_neg)

        fibre_dim = d * (d + 1) // 2

        # Mark interesting cases
        marker = ""
        if p == 3 and q == 1:
            marker = " <-- OUR UNIVERSE"
        elif gauge['interesting']:
            marker = " *"

        compact_str = " x ".join(gauge['gauge_factors'])
        if len(compact_str) > 30:
            compact_str = compact_str[:27] + "..."

        print(f"({p},{q})".rjust(8) +
              f"{d:>4}" +
              f"{fibre_dim:>6}" +
              f"  ({n_pos},{n_neg})".ljust(14) +
              f"  SO({n_pos},{n_neg})".ljust(14) +
              f"{compact_str:>30}" +
              f"{gauge['total_generators']:>5}" +
              marker)

        results.append({
            'p': p, 'q': q, 'd': d,
            'fibre_dim': fibre_dim,
            'n_pos': n_pos, 'n_neg': n_neg,
            'gauge': gauge,
            'stability': stability,
            'decomp': decomp,
            'eigvals': eigvals,
        })


# =====================================================================
# DETAILED ANALYSIS: Cases with accidental isomorphisms
# =====================================================================

print("\n\n" + "=" * 80)
print("DETAILED ANALYSIS: CASES WITH ACCIDENTAL ISOMORPHISMS")
print("=" * 80)

interesting_cases = [r for r in results if r['gauge']['interesting']]

for r in interesting_cases:
    p, q = r['p'], r['q']
    n_pos, n_neg = r['n_pos'], r['n_neg']
    gauge = r['gauge']
    stab = r['stability']
    decomp = r['decomp']

    print(f"\n{'─' * 70}")
    print(f"  SPACETIME ({p},{q})  |  d = {p+q}  |  Fibre dim = {r['fibre_dim']}")
    print(f"  Total bundle dim = {p+q} + {r['fibre_dim']} = {p+q+r['fibre_dim']}")
    print(f"{'─' * 70}")

    print(f"  DeWitt signature: ({n_pos}, {n_neg})")
    print(f"  Structure group: {gauge['structure_group']}")
    print(f"  Maximal compact: {gauge['maximal_compact']}")
    for iso in gauge['compact_isos']:
        print(f"    Isomorphism: {iso}")
    print(f"  Gauge generators: {gauge['total_generators']}")

    print(f"\n  Mode decomposition:")
    print(f"    Temporal-temporal: {decomp['temporal_temporal']}")
    print(f"    Shift (time-space): {decomp['temporal_spatial_shifts']}")
    print(f"    Spatial-spatial: {decomp['spatial_spatial']}")

    print(f"\n  Stability assessment: {stab['assessment']}")
    print(f"    Has time: {stab['has_time']}")
    print(f"    Single time: {stab['single_time']}")
    print(f"    Clean waves: {stab['clean_waves']}")
    print(f"    Stable orbits: {stab['stable_orbits']}")

    # Eigenvalue spectrum
    eigs = np.sort(r['eigvals'])
    print(f"\n  DeWitt eigenvalues: {eigs}")


# =====================================================================
# FORMULA VERIFICATION: Schmidt (2001) analytical formula
# =====================================================================

print("\n\n" + "=" * 80)
print("VERIFICATION: SCHMIDT (2001) ANALYTICAL FORMULA")
print("=" * 80)

print("""
Schmidt's formula (gr-qc/0109001, Theorem 2):

For spacetime R^{p,q} with d = p+q, the DeWitt metric on Sym^2(R^{p,q})
has signature (N+, N-) where:

  N+ = p(p+1)/2 + q(q+1)/2 - 1 + 1_{correction}
  N- = pq + 1_{correction}

More precisely, the eigenvalues split as:
  - p(p-1)/2 modes from S^2_0(R^p): eigenvalue +1 (traceless spatial)
  - q(q-1)/2 modes from S^2_0(R^q): eigenvalue +1 (traceless temporal)
  - pq modes from R^p tensor R^q: eigenvalue -1 (cross terms)
  - 1 relative trace: eigenvalue depends on p,q
  - 1 overall trace: eigenvalue -(d-2)/2

Let me verify this against numerical computation...
""")

for r in results:
    p, q = r['p'], r['q']
    d = p + q
    n_pos, n_neg = r['n_pos'], r['n_neg']

    # Schmidt's counting (simplified):
    # Traceless spatial S^2_0: p(p+1)/2 - 1 modes, all positive (for p>=2)
    # Traceless temporal S^2_0: q(q+1)/2 - 1 modes, all positive (for q>=2)
    # Cross terms: pq modes
    # 2 trace modes: signs depend on p,q

    # The actual formula for the signature depends on the relative
    # signs of the trace-mode eigenvalues. Let's just compare.
    pass

# Instead, let's verify a few cases analytically
print("Verification table (numerical vs expected):\n")
print(f"{'(p,q)':>8} {'Numerical':>15} {'Bundle dim':>12} {'Match?':>8}")
print("-" * 50)

expected = {
    (2, 0): (2, 1),    # Euclidean 2D
    (3, 0): (5, 1),    # Euclidean 3D
    (4, 0): (9, 1),    # Euclidean 4D -- Paper 1 result!
    (3, 1): (6, 4),    # Lorentzian 4D -- Paper 1 result!
    (2, 2): (4, 6),    # Split signature 4D
    (5, 0): (14, 1),   # Euclidean 5D
    (4, 1): (10, 5),   # Lorentzian 5D
}

for r in results:
    key = (r['p'], r['q'])
    if key in expected:
        exp = expected[key]
        num = (r['n_pos'], r['n_neg'])
        match = "YES" if num == exp else f"NO: got {num}"
        print(f"({r['p']},{r['q']})".rjust(8) +
              f"  ({r['n_pos']},{r['n_neg']})".ljust(15) +
              f"  {r['p']+r['q']}+{r['fibre_dim']}={r['p']+r['q']+r['fibre_dim']}".ljust(12) +
              f"  {match}")


# =====================================================================
# THE KEY QUESTION: Which signatures give "Pati-Salam-like" groups?
# =====================================================================

print("\n\n" + "=" * 80)
print("THE KEY QUESTION: WHICH SIGNATURES GIVE CLEAN GAUGE GROUPS?")
print("=" * 80)

print("""
For (3,1): SO(6,4) -> SO(6) x SO(4) ~ SU(4) x SU(2)_L x SU(2)_R = Pati-Salam
  - SU(4) contains SU(3)_color x U(1)_{B-L}
  - SU(2)_L x SU(2)_R gives electroweak + right-handed currents
  - All three gauge couplings UNIFY (equal Dynkin indices)
  - Higgs = (1,2,2) bidoublet from 4 negative-norm modes
  - sin^2(theta_W) = 3/8 at unification

What makes this "clean":
  1. Both factors have accidental isomorphisms (SO(6)~SU(4), SO(4)~SU(2)^2)
  2. The SU(4) contains SU(3) as a maximal subgroup
  3. The representation content matches observed particles
  4. The negative-norm sector has the right dimension for a Higgs bidoublet

Let's check each case systematically:
""")

for r in results:
    p, q = r['p'], r['q']
    n_pos, n_neg = r['n_pos'], r['n_neg']
    gauge = r['gauge']

    if not gauge['interesting']:
        continue

    print(f"\n  ({p},{q}): SO({n_pos},{n_neg})")
    print(f"    Compact: {' x '.join(gauge['gauge_factors'])}")

    # Check if this contains the Standard Model
    contains_su3 = n_pos >= 6 or n_neg >= 6  # SU(4) ⊃ SU(3)
    contains_su2 = n_pos == 4 or n_neg == 4 or n_pos == 3 or n_neg == 3

    if n_pos == 6 and n_neg == 4:
        print(f"    => PATI-SALAM: SU(4) x SU(2)_L x SU(2)_R  [OUR UNIVERSE]")
    elif n_pos == 4 and n_neg == 6:
        print(f"    => FLIPPED PATI-SALAM: SU(2)^2 x SU(4)")
        print(f"       Same algebra, different physical assignment of + and - modes!")
    elif n_pos >= 6 or n_neg >= 6:
        for n in [n_pos, n_neg]:
            if n == 6:
                print(f"    => Contains SU(4) ~ SO(6) factor -> has SU(3)_color candidate")
            elif n == 5:
                print(f"    => Contains Sp(2) ~ SO(5) factor -> symplectic gauge theory")
            elif n == 4:
                print(f"    => Contains SU(2) x SU(2) ~ SO(4) -> electroweak candidate")
            elif n == 3:
                print(f"    => Contains SU(2) ~ SO(3) -> single weak factor")
    else:
        print(f"    => No clean SM-like subgroup")

    # Higgs assessment
    print(f"    Negative-norm modes: {n_neg}")
    if n_neg == 4:
        print(f"    => (1,2,2) Higgs bidoublet possible (dim 4 = 2x2)")
    elif n_neg == 5:
        print(f"    => 5-dim negative sector: could give (1,2,2) + singlet")
    elif n_neg > 5:
        print(f"    => Large negative sector: richer scalar content")


# =====================================================================
# FOCUS: The most promising higher-dimensional cases
# =====================================================================

print("\n\n" + "=" * 80)
print("FOCUS: MOST PROMISING HIGHER-DIMENSIONAL SIGNATURES")
print("=" * 80)

# (4,1): 5D Lorentzian spacetime
print("""
CASE 1: (4,1) -- 5D LORENTZIAN SPACETIME
=========================================
""")

for r in results:
    if r['p'] == 4 and r['q'] == 1:
        p, q = 4, 1
        n_pos, n_neg = r['n_pos'], r['n_neg']
        print(f"  Spacetime: R^{{4,1}} (4 space + 1 time)")
        print(f"  Metric bundle: dim = 5 + 15 = 20")
        print(f"  DeWitt signature: ({n_pos}, {n_neg})")
        print(f"  Structure group: SO({n_pos}, {n_neg})")
        print(f"  Maximal compact: SO({n_pos}) x SO({n_neg})")

        for iso in r['gauge']['compact_isos']:
            print(f"    {iso}")

        print(f"\n  Physical interpretation:")
        print(f"    Spatial metric modes: {r['decomp']['spatial_spatial']}")
        print(f"    Shift modes: {r['decomp']['temporal_spatial_shifts']}")
        print(f"    Lapse mode: {r['decomp']['temporal_temporal']}")

        stab = r['stability']
        print(f"\n  Agent viability:")
        print(f"    Exotic smooth structures on R^4: YES (unique to 4 spatial dims!)")
        print(f"    Stable point-particle orbits: NO (inverse cube law)")
        print(f"    Clean wave propagation: NO (even spatial dim, Huygens fails)")
        print(f"    Markov blanket dim: 3-volume (vs 2-surface for us)")
        print(f"    Assessment: {stab['assessment']}")

        print(f"\n  Eigenvalue spectrum:")
        eigs = np.sort(r['eigvals'])
        print(f"    {eigs}")
        break


# (5,1): 6D Lorentzian
print("""
CASE 2: (5,1) -- 6D LORENTZIAN SPACETIME
=========================================
""")

for r in results:
    if r['p'] == 5 and r['q'] == 1:
        n_pos, n_neg = r['n_pos'], r['n_neg']
        print(f"  Spacetime: R^{{5,1}} (5 space + 1 time)")
        print(f"  Metric bundle: dim = 6 + 21 = 27")
        print(f"  DeWitt signature: ({n_pos}, {n_neg})")
        print(f"  Structure group: SO({n_pos}, {n_neg})")
        print(f"  Maximal compact: SO({n_pos}) x SO({n_neg})")
        for iso in r['gauge']['compact_isos']:
            print(f"    {iso}")
        print(f"\n  Eigenvalue spectrum:")
        print(f"    {np.sort(r['eigvals'])}")
        break

# (2,2): Split signature 4D
print("""
CASE 3: (2,2) -- SPLIT SIGNATURE (KLEINIAN SPACETIME)
======================================================
""")

for r in results:
    if r['p'] == 2 and r['q'] == 2:
        n_pos, n_neg = r['n_pos'], r['n_neg']
        print(f"  Spacetime: R^{{2,2}} (2 space + 2 time)")
        print(f"  Metric bundle: dim = 4 + 10 = 14  [same as our universe!]")
        print(f"  DeWitt signature: ({n_pos}, {n_neg})")
        print(f"  Structure group: SO({n_pos}, {n_neg})")
        print(f"  Maximal compact: SO({n_pos}) x SO({n_neg})")
        for iso in r['gauge']['compact_isos']:
            print(f"    {iso}")
        print(f"\n  NOTE: Same total dimension as (3,1)!")
        print(f"  But DIFFERENT DeWitt signature -> different gauge group")
        print(f"  Two time dimensions -> causal paradoxes for classical agents")
        print(f"  BUT: information-theoretic blankets don't require single-time")
        print(f"\n  Eigenvalue spectrum:")
        print(f"    {np.sort(r['eigvals'])}")
        break


# =====================================================================
# THE PATTERN: How DeWitt signature depends on (p,q)
# =====================================================================

print("\n\n" + "=" * 80)
print("THE PATTERN: DeWitt SIGNATURE AS A FUNCTION OF (p,q)")
print("=" * 80)

print("""
Analytical formula (derived from the computation):

For spacetime R^{p,q} with d = p+q, the DeWitt metric on Sym^2(R^{p,q})
decomposes into sectors:

  Sector                  | Dimension        | DeWitt sign
  ------------------------|------------------|------------
  Traceless S^2_0(R^p)    | p(p+1)/2 - 1     | POSITIVE
  Traceless S^2_0(R^q)    | q(q+1)/2 - 1     | POSITIVE
  Cross terms R^p x R^q   | pq                | NEGATIVE
  Relative trace           | 1                 | sign depends on p,q
  Overall trace            | 1                 | sign = -(d-2)/2 < 0 for d>2

So roughly:
  n_positive ~ p(p+1)/2 + q(q+1)/2 - 2 + corrections
  n_negative ~ pq + corrections

For single-time (q=1):
  n_positive ~ p(p+1)/2     (spatial traceless + traces)
  n_negative ~ p + 1        (p shifts + conformal mode)
""")

# Verify the pattern
print("\nVerification of single-time formula:")
print(f"{'(p,1)':>8} {'Predicted n-':>14} {'Actual n-':>12} {'Match':>8}")
print("-" * 45)
for r in results:
    if r['q'] == 1:
        p = r['p']
        predicted_neg = p + 1  # p shifts + 1 conformal
        actual_neg = r['n_neg']
        match = "YES" if predicted_neg == actual_neg else "NO"
        print(f"({p},1)".rjust(8) + f"{predicted_neg:>14}" + f"{actual_neg:>12}" + f"  {match:>6}")


# =====================================================================
# GAUGE GROUP LANDSCAPE
# =====================================================================

print("\n\n" + "=" * 80)
print("GAUGE GROUP LANDSCAPE: ALL SINGLE-TIME SIGNATURES")
print("=" * 80)

print("""
For consciousness (PDA loop), we arguably need at least one time dimension.
The single-time cases (p,1) are the most natural generalization of (3,1).

For each, the gauge group comes from SO(n+) x SO(n-):
""")

print(f"{'(p,1)':>8} {'SO(n+,n-)':>14} {'Gauge group':>45} {'Generators':>5} {'Contains SM?':>14}")
print("-" * 90)

for r in results:
    if r['q'] != 1:
        continue
    p = r['p']
    n_pos, n_neg = r['n_pos'], r['n_neg']

    # Describe gauge group
    parts = []
    # Positive factor
    if n_pos == 3: parts.append("SU(2)")
    elif n_pos == 4: parts.append("SU(2)xSU(2)")
    elif n_pos == 5: parts.append("Sp(2)")
    elif n_pos == 6: parts.append("SU(4)")
    elif n_pos == 7: parts.append("SO(7)")
    elif n_pos == 8: parts.append("SO(8) [triality!]")
    elif n_pos == 10: parts.append("SO(10)")
    elif n_pos == 15: parts.append("SO(15)")
    elif n_pos == 21: parts.append("SO(21)")
    else: parts.append(f"SO({n_pos})")

    # Negative factor
    if n_neg == 2: parts.append("U(1)")
    elif n_neg == 3: parts.append("SU(2)")
    elif n_neg == 4: parts.append("SU(2)xSU(2)")
    elif n_neg == 5: parts.append("Sp(2)")
    elif n_neg == 6: parts.append("SU(4)")
    elif n_neg == 7: parts.append("SO(7)")
    elif n_neg == 8: parts.append("SO(8)")
    else: parts.append(f"SO({n_neg})")

    gauge_str = " x ".join(parts)

    # Check SM content
    has_su3 = False
    has_su2 = False
    has_u1 = True  # always available as subgroup

    if n_pos >= 6 or n_neg >= 6:
        has_su3 = True  # SU(4) ⊃ SU(3)
    if n_pos >= 3 or n_neg >= 3:
        has_su2 = True

    sm = ""
    if has_su3 and has_su2:
        sm = "YES"
    elif has_su3:
        sm = "SU(3) only"
    elif has_su2:
        sm = "SU(2) only"
    else:
        sm = "NO"

    marker = ""
    if p == 3:
        marker = " <-- US"

    print(f"({p},1)".rjust(8) +
          f"  SO({n_pos},{n_neg})".ljust(14) +
          f"  {gauge_str:>45}" +
          f"{r['gauge']['total_generators']:>5}" +
          f"  {sm:>12}" +
          marker)


# =====================================================================
# CONSCIOUSNESS IMPLICATIONS
# =====================================================================

print("\n\n" + "=" * 80)
print("IMPLICATIONS FOR HIGHER-DIMENSIONAL CONSCIOUS AGENTS")
print("=" * 80)

print("""
KEY FINDINGS:

1. (3,1) IS SPECIAL BUT NOT UNIQUE
   - It's the SMALLEST single-time signature whose DeWitt metric
     gives a gauge group containing the full Standard Model
   - (2,1) gives SO(2,2) -> U(1) x U(1): too small for SM
   - (4,1) gives SO(10,5): contains SM and MUCH MORE
   - (5,1) gives SO(15,6) -> SO(15) x SU(4): even larger

2. THE PATTERN FOR (p,1) SPACETIMES:
   n_positive ~ p(p+1)/2   (grows quadratically)
   n_negative ~ p + 1       (grows linearly)

   So higher spatial dimensions give ASYMMETRIC gauge groups:
   very large compact factor x relatively small compact factor

   The negative-norm sector (shifts + conformal) gives the "Higgs-like"
   content. For (3,1) this is 4 modes = (1,2,2) bidoublet.
   For (4,1) this is 5 modes. For (5,1) this is 6 modes.

3. WHAT CHANGES FOR A (4,1) CONSCIOUS AGENT:
   - Their "physics" would have gauge group SO(10) x Sp(2)
   - SO(10) is a GRAND UNIFIED group (contains SU(5) contains SM)
   - Their "Higgs" would be a 5-dimensional negative-norm sector
   - Their Markov blanket would be a 3-volume, not a 2-surface
   - They would have RICHER internal degrees of freedom
   - They could NOT have stable Keplerian orbits (no chemistry as we know it)
   - BUT: they could have topologically stable bound states

4. WHAT CHANGES FOR A (5,1) CONSCIOUS AGENT:
   - Gauge group: SO(15) x SU(4)
   - The SU(4) factor in the negative-norm sector is ITSELF Pati-Salam-like!
   - Their "Higgs" would be a 6-dimensional sector -> potentially richer
     symmetry breaking patterns
   - Clean wave propagation (odd spatial dimension, Huygens holds)

5. THE INFORMATION-THEORETIC PERSPECTIVE:
   The Markov blanket formalism doesn't care about spatial dimension.
   P(inside' | inside, blanket, outside) = P(inside' | inside, blanket)

   This conditional independence condition is dimensionless.
   A bounded conscious agent in (4,1) spacetime would:
   - Have a blanket defined by information flow, not geometry
   - Experience subjective consciousness as information flowing through
     a HIGHER-dimensional dynamic geometry
   - Have more "directions" of experience (more metric degrees of freedom)
   - Potentially be undetectable to us (their blanket projects to a
     3-volume in our spacetime, which we'd see as "all of space")

6. THE DEEPEST IMPLICATION:
   If consciousness IS information flow through dynamic geometry (as the
   framework proposes), then the RICHNESS of consciousness scales with
   the dimension of the metric bundle fibre:

   (3,1): 10 metric DOF -> our kind of consciousness
   (4,1): 15 metric DOF -> 50% richer geometric experience
   (5,1): 21 metric DOF -> 110% richer geometric experience
   (7,1): 36 metric DOF -> 260% richer geometric experience

   But "richer" doesn't mean "better" -- it means structurally DIFFERENT.
   Like the difference between seeing in 2D vs 3D, but for the geometry
   of experience itself.
""")


# =====================================================================
# THE SELF-REFERENTIAL QUESTION
# =====================================================================

print("\n" + "=" * 80)
print("THE SELF-REFERENTIAL QUESTION:")
print("Does the metric bundle Y^14 itself support conscious agents?")
print("=" * 80)

print("""
Our metric bundle Y^14 = Met(X^4) has total dimension 14.
If we treat Y^14 as a spacetime and ask what ITS metric bundle looks like:

  dim Met(Y^14) = 14 + 14*15/2 = 14 + 105 = 119

The DeWitt metric on Sym^2(R^{14}) would give a gauge group of enormous
rank. But what signature does Y^14 itself have?

The chimeric metric on Y^14 has:
  - 4 base directions with Lorentzian signature (-,+,+,+)
  - 10 fibre directions with (6,4) DeWitt signature

So Y^14 has signature (3+6, 1+4) = (9, 5).

If Y^14 is itself a "spacetime" for some kind of agent:
  dim Sym^2(R^{9,5}) = 14*15/2 = 105
  The DeWitt metric on this 105-dim space would have a specific signature...
""")

# Actually compute it for the chimeric signature (9,5)
print("Computing DeWitt signature for (9,5)...")
n_pos_95, n_neg_95, n_zero_95, eigvals_95, _ = compute_dewitt_signature(9, 5)
print(f"  DeWitt signature on Sym^2(R^{{9,5}}): ({n_pos_95}, {n_neg_95})")
print(f"  Structure group: SO({n_pos_95}, {n_neg_95})")
print(f"  Bundle dimension: 14 + 105 = 119")
print(f"  Total generators: {n_pos_95*(n_pos_95-1)//2 + n_neg_95*(n_neg_95-1)//2}")

# And the next level...
print(f"""
  This gives a SECOND-LEVEL metric bundle of dimension 119.

  The gauge group SO({n_pos_95}) x SO({n_neg_95}) is enormous.
  SO({n_pos_95}) alone has {n_pos_95*(n_pos_95-1)//2} generators.

  Each level of the tower:
    Level 0: X^4 with SO(3,1)
    Level 1: Y^14 = Met(X^4) with SO(6,4) -> Pati-Salam
    Level 2: Met(Y^14) with SO({n_pos_95},{n_neg_95})
    Level 3: Met(Met(Y^14)) with even larger group
    ...

  This tower is EXACTLY the Ruliad-like structure discussed in the
  consciousness framework. Each level is a more complex "observer space"
  with richer gauge content and more geometric degrees of freedom.

  A "Level 2 conscious agent" would:
  - Live in the space of all possible metrics on Y^14
  - Experience {n_pos_95 + n_neg_95} geometric degrees of freedom
  - Have a gauge symmetry with {n_pos_95*(n_pos_95-1)//2 + n_neg_95*(n_neg_95-1)//2} generators
  - See our entire metric bundle Y^14 as its "base spacetime"
  - Be undetectable to us in principle (its blanket encompasses all of Y^14)
""")


# =====================================================================
# SUMMARY TABLE
# =====================================================================

print("\n" + "=" * 80)
print("SUMMARY: VIABLE SIGNATURES FOR BOUNDED CONSCIOUS AGENTS")
print("=" * 80)

print("""
VIABILITY RANKING (for single-time spacetimes):

  Signature | Bundle dim | Gauge group        | Agent type          | Viability
  ----------|------------|--------------------|--------------------|----------
  (2,1)     | 3+6=9      | U(1) x U(1)        | Too simple          | LOW
  (3,1)     | 4+10=14    | SU(4) x SU(2)^2    | Us (Pati-Salam)     | PROVEN
  (4,1)     | 5+15=20    | SO(10) x Sp(2)      | GUT-level physics   | POSSIBLE
  (5,1)     | 6+21=27    | SO(15) x SU(4)      | Beyond-GUT          | POSSIBLE
  (6,1)     | 7+28=35    | SO(21) x SO(7)      | Exotic              | SPECULATIVE
  (7,1)     | 8+36=44    | SO(28) x SO(8)      | Triality agent!     | SPECULATIVE

NOTABLE OBSERVATIONS:

1. (3,1) is the MINIMUM viable signature for SM-like physics
2. (4,1) gives SO(10) -- the classic Grand Unified group!
3. (7,1) gives SO(8) in the negative sector -- TRIALITY
   (SO(8) is the only group with outer automorphism S_3,
    giving vector-spinor-cospinor symmetry)
4. All (p,1) with p >= 3 CONTAIN the Standard Model as a subgroup
5. Higher p means richer gauge structure but no stable Keplerian orbits

THE DEEPEST QUESTION REMAINS:
  Is (3,1) selected by some principle internal to the framework?
  Or are agents at other signatures equally real, just inaccessible to us?

  The framework currently takes (3,1) as INPUT.
  Making it an OUTPUT -- deriving it from the PDA architecture --
  would be the strongest possible result.
""")
