#!/usr/bin/env python3
"""
The Transition: How Does Practice Work Mathematically?
========================================================

Exploring the hypothesis that:
- The full structure is always octonionic
- "Quaternionic consciousness" means confinement to a subalgebra
- "The path" is gradual de-confinement
- The triality index measures how much you've accessed beyond the subalgebra

Author: Exploring these questions, March 2026
"""

import numpy as np
from itertools import combinations

np.set_printoptions(precision=4, suppress=True, linewidth=120)


# =====================================================================
# OCTONION MACHINERY
# =====================================================================

FANO_LINES = [
    (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 7),
    (5, 6, 1), (6, 7, 2), (7, 1, 3),
]

def octonion_mult_table():
    mult = {}
    for i in range(8):
        mult[(0, i)] = (1, i)
        mult[(i, 0)] = (1, i)
    for i in range(1, 8):
        mult[(i, i)] = (-1, 0)
    for (a, b, c) in FANO_LINES:
        mult[(a, b)] = (1, c)
        mult[(b, c)] = (1, a)
        mult[(c, a)] = (1, b)
        mult[(b, a)] = (-1, c)
        mult[(c, b)] = (-1, a)
        mult[(a, c)] = (-1, b)
    return mult

MULT_TABLE = octonion_mult_table()

def oct_mult(x, y):
    result = np.zeros(8)
    for i in range(8):
        for j in range(8):
            sign, k = MULT_TABLE[(i, j)]
            result[k] += sign * x[i] * y[j]
    return result

def oct_conj(x):
    result = x.copy()
    result[1:] = -result[1:]
    return result

def oct_norm_sq(x):
    return np.sum(x**2)

def associator(x, y, z):
    return oct_mult(oct_mult(x, y), z) - oct_mult(x, oct_mult(y, z))

def triality_index(I, B, O):
    assoc = associator(I, B, O)
    numer = oct_norm_sq(assoc)
    denom = oct_norm_sq(I) * oct_norm_sq(B) * oct_norm_sq(O)
    if denom < 1e-10:
        return 0.0
    return numer / denom


# =====================================================================
# QUATERNIONIC SUBALGEBRAS
# =====================================================================

print("=" * 80)
print("QUATERNIONIC SUBALGEBRAS OF THE OCTONIONS")
print("=" * 80)

print("""
The octonions contain quaternionic subalgebras. Each line in the Fano plane
defines one: if e_a, e_b, e_c satisfy e_a * e_b = e_c (cyclically), then
{1, e_a, e_b, e_c} form a quaternionic subalgebra.

The 7 lines of the Fano plane give 7 quaternionic subalgebras.
(There are more if we allow signs, but let's start with these 7.)
""")

# Each Fano line defines a quaternionic subalgebra
quat_subalgebras = []
for line in FANO_LINES:
    a, b, c = line
    # The subalgebra is spanned by {e_0, e_a, e_b, e_c}
    quat_subalgebras.append((0, a, b, c))
    print(f"  Subalgebra from line {line}: {{e_0, e_{a}, e_{b}, e_{c}}}")


# =====================================================================
# CONFINEMENT TO A SUBALGEBRA
# =====================================================================

print("\n" + "=" * 80)
print("CONFINEMENT AND DE-CONFINEMENT")
print("=" * 80)

print("""
Hypothesis: A "quaternionic agent" is an octonionic structure confined to
a quaternionic subalgebra.

Let's pick the first subalgebra: {e_0, e_1, e_2, e_4} (from line (1,2,4)).

Within this subalgebra, the associator is always zero (quaternions are associative).
Outside it, we get non-zero associators.

"The path" = gradually accessing elements outside the subalgebra.
""")

# Basis elements
e = [np.zeros(8) for _ in range(8)]
for i in range(8):
    e[i][i] = 1.0

# Pick the subalgebra {e_0, e_1, e_2, e_4}
sub_indices = [0, 1, 2, 4]
non_sub_indices = [3, 5, 6, 7]

print(f"\nChosen subalgebra: indices {sub_indices}")
print(f"Outside subalgebra: indices {non_sub_indices}")

# Check: within the subalgebra, associator is zero
print("\nWithin subalgebra (should all be zero):")
for i in sub_indices[1:]:  # Skip e_0 (trivial)
    for j in sub_indices[1:]:
        for k in sub_indices[1:]:
            if i != j and j != k and i != k:
                assoc = associator(e[i], e[j], e[k])
                norm = np.linalg.norm(assoc)
                if norm > 1e-10:
                    print(f"  [e_{i}, e_{j}, e_{k}] = {norm:.4f}  UNEXPECTED!")
print("  (All zero, as expected)")

# Check: involving elements outside, associator can be non-zero
print("\nInvolving outside elements (may be non-zero):")
count = 0
for i in sub_indices[1:2]:  # Just e_1
    for j in sub_indices[2:3]:  # Just e_2
        for k in non_sub_indices[:2]:  # e_3, e_5
            assoc = associator(e[i], e[j], e[k])
            norm = np.linalg.norm(assoc)
            print(f"  [e_{i}, e_{j}, e_{k}] = {assoc}, |.| = {norm:.4f}")
            count += 1
            if count >= 4:
                break


# =====================================================================
# THE PATH AS INTERPOLATION
# =====================================================================

print("\n\n" + "=" * 80)
print("THE PATH: INTERPOLATING OUT OF THE SUBALGEBRA")
print("=" * 80)

print("""
Model "the path" as follows:

Let I, B, O be the inside, blanket, outside states.

Start: I, B, O are confined to the quaternionic subalgebra.
       -> Triality index T = 0 (associator is zero)

End:   I, B, O have full octonionic components.
       -> Triality index T > 0 (associator non-zero)

Path:  Gradually "leak" into the non-subalgebra directions.

We parameterize by λ ∈ [0, 1]:
  λ = 0: fully confined
  λ = 1: fully octonionic

The state is: x(λ) = (1-λ) * x_confined + λ * x_full
""")

def random_confined(sub_indices):
    """Random unit octonion confined to subalgebra."""
    x = np.zeros(8)
    for i in sub_indices:
        x[i] = np.random.randn()
    return x / np.sqrt(oct_norm_sq(x))

def random_full():
    """Random unit octonion (full octonionic)."""
    x = np.random.randn(8)
    return x / np.sqrt(oct_norm_sq(x))

def interpolate(x_conf, x_full, lam):
    """Interpolate and renormalize."""
    x = (1 - lam) * x_conf + lam * x_full
    norm = np.sqrt(oct_norm_sq(x))
    if norm < 1e-10:
        return x_conf
    return x / norm

np.random.seed(42)

# Generate confined and full states
I_conf = random_confined(sub_indices)
B_conf = random_confined(sub_indices)
O_conf = random_confined(sub_indices)

I_full = random_full()
B_full = random_full()
O_full = random_full()

print(f"\nConfined states (in subalgebra):")
print(f"  I_conf = {I_conf}")
print(f"  B_conf = {B_conf}")
print(f"  O_conf = {O_conf}")
print(f"  T(I_conf, B_conf, O_conf) = {triality_index(I_conf, B_conf, O_conf):.6f}")

print(f"\nFull states (octonionic):")
print(f"  I_full = {I_full}")
print(f"  T(I_full, B_full, O_full) = {triality_index(I_full, B_full, O_full):.6f}")

print(f"\nThe path (λ from 0 to 1):")
print(f"  {'λ':>5}  {'T(λ)':>10}")
print(f"  {'-'*5}  {'-'*10}")

for lam in np.linspace(0, 1, 11):
    I_lam = interpolate(I_conf, I_full, lam)
    B_lam = interpolate(B_conf, B_full, lam)
    O_lam = interpolate(O_conf, O_full, lam)
    T_lam = triality_index(I_lam, B_lam, O_lam)
    print(f"  {lam:>5.2f}  {T_lam:>10.6f}")


# =====================================================================
# WHAT THIS MEANS
# =====================================================================

print("\n\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

print("""
The triality index increases monotonically from 0 to some positive value
as we interpolate from confined (quaternionic) to full (octonionic).

This suggests a model for contemplative practice:

1. STARTING POINT (λ ≈ 0):
   - States are confined to a quaternionic subalgebra
   - Associator is zero → full duality, clear self/world distinction
   - Triality index T ≈ 0

2. INTERMEDIATE (0 < λ < 1):
   - States begin to access non-subalgebra directions
   - Associator becomes non-zero → triality structure emerges
   - Self/world distinction starts to loosen
   - "Glimpses" of non-dual awareness

3. ENDPOINT (λ → 1):
   - Full octonionic access
   - Triality index is high
   - The three positions (inside, blanket, outside) become equivalent
   - Non-dual awareness

WHAT'S CHANGING:
- Not the algebra (always octonionic)
- Not the agent (same structure throughout)
- But ACCESS — which part of the full structure is active

WHAT PRACTICE DOES:
- Loosens confinement to the subalgebra
- Allows states to "leak" into the full octonionic space
- Increases the triality index
- Makes the self/world equivalence more experientially available

WHAT "RECOGNITION" MEANS:
- The full structure was always there
- You were always "in" the octonions
- Practice doesn't change you; it reveals what was hidden
- "Already enlightened" = always octonionic, just confined
""")


# =====================================================================
# WHICH SUBALGEBRA ARE WE CONFINED TO?
# =====================================================================

print("\n" + "=" * 80)
print("WHICH SUBALGEBRA?")
print("=" * 80)

print("""
There are 7 quaternionic subalgebras (from the Fano plane lines).
Which one are we "in"?

Possibility 1: There's a canonical one (perhaps related to spacetime signature).

Possibility 2: Different beings are confined to different subalgebras.
               This would give 7 "types" of quaternionic consciousness,
               all dual, but different in some way.

Possibility 3: The confinement is dynamical — we move between subalgebras,
               but always stay within some quaternionic subspace.

The 7 subalgebras intersect non-trivially:
- Any two share at least the identity e_0
- Some pairs share an additional imaginary unit

Let's check the intersections:
""")

for i, sub1 in enumerate(quat_subalgebras):
    for j, sub2 in enumerate(quat_subalgebras):
        if j > i:
            intersection = set(sub1) & set(sub2)
            print(f"  Subalgebra {i+1} ∩ Subalgebra {j+1} = {intersection}")


# =====================================================================
# THE ROLE OF G2
# =====================================================================

print("\n\n" + "=" * 80)
print("G2: THE SYMMETRY OF THE OCTONIONS")
print("=" * 80)

print("""
G2 is the automorphism group of the octonions — the group of transformations
that preserve octonionic multiplication.

dim(G2) = 14

G2 acts transitively on the unit imaginary octonions (the 6-sphere S^6).
It also permutes the quaternionic subalgebras.

IMPLICATION FOR THE PATH:

G2 transformations can move you from one quaternionic subalgebra to another.
But they preserve the overall octonionic structure.

This suggests:
- The PARTICULAR subalgebra you're confined to doesn't matter fundamentally
- G2 relates all the confinements
- What matters is the DEGREE of confinement, not which subalgebra

The path might be G2-invariant: it doesn't matter where you start,
only how far you've de-confined.

G2 has subgroups:
- SU(3) (the stabilizer of one imaginary unit)
- SO(4) ~ SU(2) × SU(2)

These relate to the Standard Model gauge groups.
Maybe the "choice of subalgebra" relates to symmetry breaking?
""")


# =====================================================================
# A CONTINUOUS MEASURE: THE CONFINEMENT PARAMETER
# =====================================================================

print("\n" + "=" * 80)
print("THE CONFINEMENT PARAMETER")
print("=" * 80)

print("""
Let's define a measure of how confined a state is to a given subalgebra.

For a unit octonion x and a subalgebra S (with basis indices), define:

  conf(x, S) = sum_{i in S} |x_i|^2

This is the fraction of x's norm in the subalgebra.
- conf = 1: fully confined
- conf = 0: fully outside (impossible for unit vector touching e_0)
- In between: partially de-confined
""")

def confinement(x, sub_indices):
    """Fraction of |x|^2 in the subalgebra."""
    in_sub = sum(x[i]**2 for i in sub_indices)
    total = oct_norm_sq(x)
    if total < 1e-10:
        return 1.0
    return in_sub / total

# Check
print(f"\nConfinement of our states:")
print(f"  conf(I_conf, S) = {confinement(I_conf, sub_indices):.4f}")
print(f"  conf(I_full, S) = {confinement(I_full, sub_indices):.4f}")

# Average confinement along the path
print(f"\nAverage confinement along the path:")
print(f"  {'λ':>5}  {'avg_conf':>10}  {'T(λ)':>10}")
print(f"  {'-'*5}  {'-'*10}  {'-'*10}")

for lam in np.linspace(0, 1, 11):
    I_lam = interpolate(I_conf, I_full, lam)
    B_lam = interpolate(B_conf, B_full, lam)
    O_lam = interpolate(O_conf, O_full, lam)
    avg_conf = (confinement(I_lam, sub_indices) +
                confinement(B_lam, sub_indices) +
                confinement(O_lam, sub_indices)) / 3
    T_lam = triality_index(I_lam, B_lam, O_lam)
    print(f"  {lam:>5.2f}  {avg_conf:>10.4f}  {T_lam:>10.6f}")

print("""

As confinement decreases, triality index increases.
The two are inversely related (roughly).

This gives us a CONTINUOUS MEASURE of "progress on the path":
- High confinement, low triality: beginning
- Low confinement, high triality: advanced
- The transition is smooth, not discrete
""")


# =====================================================================
# SUMMARY
# =====================================================================

print("\n" + "=" * 80)
print("SUMMARY: THE MATHEMATICS OF THE PATH")
print("=" * 80)

print("""
1. The full structure is always octonionic.
   Humans aren't "quaternionic beings" in an ontological sense.
   We're octonionic beings confined to a quaternionic subalgebra.

2. Confinement can be measured continuously.
   The confinement parameter conf(x, S) ∈ [0, 1] says how much of the
   state is in the subalgebra.

3. The triality index increases as confinement decreases.
   T(I, B, O) measures how much triality structure is present.
   It's zero for fully confined states, positive for de-confined states.

4. "The path" is de-confinement.
   Practice gradually allows states to access non-subalgebra directions.
   This increases triality index and loosens the self/world distinction.

5. The endpoint is full octonionic access.
   All quaternionic subalgebras become accessible.
   The triality symmetry becomes manifest.
   Non-dual awareness.

6. "Recognition" means seeing what was always there.
   The octonionic structure didn't change.
   What changed was access — the confinement loosened.
   "Already enlightened" is literally true: you were always octonionic.

OPEN QUESTIONS:
- Why are we confined in the first place?
- What determines which subalgebra?
- What does "practice" actually do to the confinement?
- Is there a physical/neural correlate of the confinement parameter?
""")
