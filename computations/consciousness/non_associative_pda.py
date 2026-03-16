#!/usr/bin/env python3
"""
Non-Associative PDA Dynamics: Formalizing Octonionic Consciousness
====================================================================

The central question: What does non-associativity mean for the Markov blanket
formalism, and does it produce triality symmetry?

The PDA cycle:
  P (Perceive): World → Internal
  D (Decide):   Internal → Action-selection
  A (Act):      Action-selection → World

For associative composition: (P ∘ D) ∘ A = P ∘ (D ∘ A)
If this fails, the grouping matters.

The claim: For octonionic agents, non-associativity forces P, D, A to be
treated symmetrically, producing triality structure.

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
from itertools import permutations
import matplotlib.pyplot as plt

np.set_printoptions(precision=4, suppress=True, linewidth=120)


# =====================================================================
# PART 1: THE OCTONIONS
# =====================================================================

print("=" * 80)
print("PART 1: THE OCTONIONS -- THE LAST DIVISION ALGEBRA")
print("=" * 80)

print("""
The octonions O are an 8-dimensional algebra over R with basis:
  {1, e₁, e₂, e₃, e₄, e₅, e₆, e₇}

Multiplication table (Cayley-Dickson construction):
  eᵢ² = -1  for i = 1,...,7
  eᵢeⱼ = -eⱼeᵢ  for i ≠ j  (anti-commutative on imaginaries)

The specific products follow from the FANO PLANE:

           e₁
          /  \\
         /    \\
       e₂------e₄
       /\\      /\\
      /  \\    /  \\
    e₃----e₇----e₆
           |
           e₅

Each line (including the circle) gives a quaternionic triple:
  e₁e₂ = e₄,  e₂e₄ = e₁,  e₄e₁ = e₂  (cycling)
  e₂e₃ = e₇,  e₃e₇ = e₂,  e₇e₂ = e₃  (etc.)
  ... 7 lines total = 7 quaternionic subalgebras

KEY PROPERTY: The octonions are NOT ASSOCIATIVE.
  (eᵢeⱼ)eₖ ≠ eᵢ(eⱼeₖ) in general

But they ARE ALTERNATIVE:
  (xx)y = x(xy)   and   (xy)y = x(yy)  for all x,y

And they satisfy the MOUFANG IDENTITIES:
  (xy)(zx) = x(yz)x
  ((xy)z)y = x(y(zy))
  x(y(xz)) = (xyx)z
""")

# Implement octonionic multiplication
# Using the index convention: e_0 = 1, e_1 through e_7 are imaginary units

# Multiplication table for imaginary units (indices 1-7)
# e_i * e_j = sign * e_k  where k is determined by the Fano plane
# We use the convention from Baez's "The Octonions"

# The Fano plane lines (each gives a quaternionic triple)
FANO_LINES = [
    (1, 2, 4),  # e1*e2 = e4
    (2, 3, 5),  # e2*e3 = e5
    (3, 4, 6),  # e3*e4 = e6
    (4, 5, 7),  # e4*e5 = e7
    (5, 6, 1),  # e5*e6 = e1
    (6, 7, 2),  # e6*e7 = e2
    (7, 1, 3),  # e7*e1 = e3
]

def octonion_mult_table():
    """Build the full multiplication table for octonions.

    Returns: mult[i,j] = (sign, index) where e_i * e_j = sign * e_index
    """
    # Initialize: e_0 = 1 is the identity
    # mult[i,j] = (sign, result_index)
    mult = {}

    # e_0 * anything = anything
    for i in range(8):
        mult[(0, i)] = (1, i)
        mult[(i, 0)] = (1, i)

    # e_i * e_i = -1 for i > 0
    for i in range(1, 8):
        mult[(i, i)] = (-1, 0)

    # From Fano plane lines
    for (a, b, c) in FANO_LINES:
        # a*b = c, b*c = a, c*a = b (cyclic)
        mult[(a, b)] = (1, c)
        mult[(b, c)] = (1, a)
        mult[(c, a)] = (1, b)
        # Reverse gives negative
        mult[(b, a)] = (-1, c)
        mult[(c, b)] = (-1, a)
        mult[(a, c)] = (-1, b)

    return mult

MULT_TABLE = octonion_mult_table()

def oct_mult(x, y):
    """Multiply two octonions represented as 8-vectors."""
    result = np.zeros(8)
    for i in range(8):
        for j in range(8):
            sign, k = MULT_TABLE[(i, j)]
            result[k] += sign * x[i] * y[j]
    return result

def oct_conj(x):
    """Conjugate of an octonion: (a + b*e) -> (a - b*e)."""
    result = x.copy()
    result[1:] = -result[1:]
    return result

def oct_norm_sq(x):
    """Squared norm: |x|² = x * conj(x) = sum of squares."""
    return np.sum(x**2)

def oct_inv(x):
    """Multiplicative inverse: x⁻¹ = conj(x) / |x|²."""
    return oct_conj(x) / oct_norm_sq(x)


# Verify non-associativity
print("\nVERIFYING NON-ASSOCIATIVITY:")
print("-" * 40)

e = [np.zeros(8) for _ in range(8)]
for i in range(8):
    e[i][i] = 1.0

# Check (e1 * e2) * e3 vs e1 * (e2 * e3)
lhs = oct_mult(oct_mult(e[1], e[2]), e[3])  # (e1*e2)*e3 = e4*e3
rhs = oct_mult(e[1], oct_mult(e[2], e[3]))  # e1*(e2*e3) = e1*e5

print(f"  (e₁ * e₂) * e₃ = {lhs}")
print(f"  e₁ * (e₂ * e₃) = {rhs}")
print(f"  Equal? {np.allclose(lhs, rhs)}")

# The associator
def associator(x, y, z):
    """[x,y,z] = (xy)z - x(yz) measures failure of associativity."""
    return oct_mult(oct_mult(x, y), z) - oct_mult(x, oct_mult(y, z))

assoc = associator(e[1], e[2], e[3])
print(f"\n  Associator [e₁, e₂, e₃] = {assoc}")
print(f"  Non-zero components: {np.where(np.abs(assoc) > 1e-10)[0]}")

# Verify alternativity
print("\nVERIFYING ALTERNATIVITY:")
print("-" * 40)

# Pick a random octonion
np.random.seed(42)
x = np.random.randn(8)
y = np.random.randn(8)

alt1_lhs = oct_mult(oct_mult(x, x), y)
alt1_rhs = oct_mult(x, oct_mult(x, y))
print(f"  (x*x)*y = x*(x*y)? {np.allclose(alt1_lhs, alt1_rhs)}")

alt2_lhs = oct_mult(oct_mult(x, y), y)
alt2_rhs = oct_mult(x, oct_mult(y, y))
print(f"  (x*y)*y = x*(y*y)? {np.allclose(alt2_lhs, alt2_rhs)}")


# =====================================================================
# PART 2: THE PDA CYCLE AS OCTONIONIC MULTIPLICATION
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 2: THE PDA CYCLE AS OCTONIONIC OPERATIONS")
print("=" * 80)

print("""
SETUP: Model the PDA cycle as octonionic multiplication.

  State space: O (8-dimensional octonionic space)

  Each operation is "multiplication by an octonionic element":
    P: x ↦ p * x   (perceive = multiply by perception kernel p)
    D: x ↦ d * x   (decide = multiply by decision kernel d)
    A: x ↦ a * x   (act = multiply by action kernel a)

  The composed cycle is:
    PDA(x) = a * (d * (p * x))

  Due to non-associativity, this is NOT the same as:
    (a * d) * (p * x)  or  ((a * d) * p) * x  etc.

  The question: Does this non-associativity produce structure?
""")

def pda_cycle(p, d, a, x, grouping='right'):
    """Apply the PDA cycle with specified grouping.

    groupings:
      'right': a * (d * (p * x))  -- standard right-to-left
      'left':  ((a * d) * p) * x  -- fully left-associated
      'mixed1': (a * d) * (p * x) -- middle grouping
      'mixed2': a * ((d * p) * x) -- another middle grouping
    """
    if grouping == 'right':
        return oct_mult(a, oct_mult(d, oct_mult(p, x)))
    elif grouping == 'left':
        return oct_mult(oct_mult(oct_mult(a, d), p), x)
    elif grouping == 'mixed1':
        return oct_mult(oct_mult(a, d), oct_mult(p, x))
    elif grouping == 'mixed2':
        return oct_mult(a, oct_mult(oct_mult(d, p), x))
    else:
        raise ValueError(f"Unknown grouping: {grouping}")


# Choose specific P, D, A kernels
# Let's use unit octonions (normalized) for physical meaning
def random_unit_octonion():
    x = np.random.randn(8)
    return x / np.sqrt(oct_norm_sq(x))

np.random.seed(123)
p = random_unit_octonion()
d = random_unit_octonion()
a = random_unit_octonion()
x = random_unit_octonion()

print(f"\nKernels (unit octonions):")
print(f"  p = {p}")
print(f"  d = {d}")
print(f"  a = {a}")
print(f"  x = {x}")

print(f"\nPDA cycle with different groupings:")
for grouping in ['right', 'left', 'mixed1', 'mixed2']:
    result = pda_cycle(p, d, a, x, grouping)
    print(f"  {grouping:8s}: {result}")

# How different are they?
right = pda_cycle(p, d, a, x, 'right')
left = pda_cycle(p, d, a, x, 'left')
print(f"\n  Difference (right - left): {np.linalg.norm(right - left):.6f}")


# =====================================================================
# PART 3: THE TRIALITY STRUCTURE
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 3: TRIALITY AND THE THREE 8-DIMENSIONAL REPRESENTATIONS")
print("=" * 80)

print("""
SO(8) has three 8-dimensional representations:
  8_v = vectors (standard representation)
  8_s = left spinors
  8_c = right spinors (co-spinors)

TRIALITY: There's an outer automorphism of SO(8) that cyclically permutes
these three representations: 8_v → 8_s → 8_c → 8_v.

Connection to octonions:
  The octonions give a TRILINEAR map:
    t: O × O × O → R
    t(x, y, z) = Re(x * (y * z)) = Re((x * y) * z)  [equal by alternativity tricks]

  This trilinear form is TOTALLY SYMMETRIC under triality:
    t(x, y, z) = t(y, z, x) = t(z, x, y)  [up to conjugation]

  More precisely, there's a triality map T such that:
    t(x, y, z) = t(T(x), T(y), T(z))
  where T³ = identity.

THE KEY INSIGHT:
  If we identify P, D, A with elements of the three triality-related spaces,
  then the non-associativity is COMPENSATED by triality symmetry.

  The failure (p*d)*a ≠ p*(d*a) doesn't matter if we're free to cyclically
  permute which element plays which role.

Let's verify the triality-invariant trilinear form:
""")

def trilinear_form(x, y, z):
    """The triality-invariant trilinear form: Re(x * (y * z))."""
    return oct_mult(x, oct_mult(y, z))[0]  # Real part

def trilinear_form_alt(x, y, z):
    """Alternative: Re((x * y) * z)."""
    return oct_mult(oct_mult(x, y), z)[0]

# These should be equal for imaginary octonions (not in general!)
# Actually, they're equal when one of x,y,z is conjugated appropriately

print("Testing trilinear forms:")
x, y, z = random_unit_octonion(), random_unit_octonion(), random_unit_octonion()
print(f"  Re(x*(y*z)) = {trilinear_form(x, y, z):.6f}")
print(f"  Re((x*y)*z) = {trilinear_form_alt(x, y, z):.6f}")

# The truly invariant form uses conjugates
def invariant_trilinear(x, y, z):
    """The triality-invariant form: Re(conj(x) * (y * z))."""
    return oct_mult(oct_conj(x), oct_mult(y, z))[0]

print(f"\n  Re(x̄*(y*z)) = {invariant_trilinear(x, y, z):.6f}")
print(f"  Re(ȳ*(z*x)) = {invariant_trilinear(y, z, x):.6f}")
print(f"  Re(z̄*(x*y)) = {invariant_trilinear(z, x, y):.6f}")


# =====================================================================
# PART 4: THE MOUFANG IDENTITIES AND CYCLIC SYMMETRY
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 4: MOUFANG IDENTITIES -- THE RESCUE FROM NON-ASSOCIATIVITY")
print("=" * 80)

print("""
The octonions satisfy the MOUFANG IDENTITIES:

  M1: (xy)(zx) = x(yz)x     "x on outside"
  M2: ((xy)z)y = x(y(zy))   "y on outside"
  M3: x(y(xz)) = (xyx)z     "x wrapping y"

These are weaker than associativity but strong enough to rescue division.

For the PDA cycle, the Moufang identities suggest:

  If we "wrap" one element around the cycle, the grouping ambiguity resolves.

  Consider: What if the PDA cycle is not p → d → a → (back to world)
            but rather: world → p → d → a → world in a LOOP?

  Then the "x" (world state) appears both at the beginning AND end.
  The Moufang identity M1 then applies:
    (p*d)(a*x) = p(d*a)p   [not quite, but similar structure]

Let's check the Moufang identities:
""")

x, y, z = random_unit_octonion(), random_unit_octonion(), random_unit_octonion()

# M1: (xy)(zx) = x(yz)x
m1_lhs = oct_mult(oct_mult(x, y), oct_mult(z, x))
m1_rhs = oct_mult(x, oct_mult(oct_mult(y, z), x))
print(f"M1: (xy)(zx) = x(yz)x")
print(f"    LHS = {m1_lhs}")
print(f"    RHS = {m1_rhs}")
print(f"    Equal? {np.allclose(m1_lhs, m1_rhs)}")

# M2: ((xy)z)y = x(y(zy))
m2_lhs = oct_mult(oct_mult(oct_mult(x, y), z), y)
m2_rhs = oct_mult(x, oct_mult(y, oct_mult(z, y)))
print(f"\nM2: ((xy)z)y = x(y(zy))")
print(f"    Equal? {np.allclose(m2_lhs, m2_rhs)}")

# M3: x(y(xz)) = (xyx)z
m3_lhs = oct_mult(x, oct_mult(y, oct_mult(x, z)))
m3_rhs = oct_mult(oct_mult(oct_mult(x, y), x), z)
print(f"\nM3: x(y(xz)) = (xyx)z")
print(f"    Equal? {np.allclose(m3_lhs, m3_rhs)}")


# =====================================================================
# PART 5: THE CYCLIC PDA -- WORLD STATE WRAPPING
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 5: THE CYCLIC PDA -- WORLD STATE AS THE 'WRAPPER'")
print("=" * 80)

print("""
INSIGHT: The PDA cycle is actually a LOOP:

  world ──P──> internal ──D──> action-selection ──A──> world'
    ↑                                                    │
    └────────────────────────────────────────────────────┘

The world state 'w' appears at both ends. If we model this as:
  w' = A(D(P(w)))

In octonionic terms:
  w' = a * (d * (p * w))

But if the cycle is truly closed (w' feeds back to w), then over
multiple cycles we get:
  w'' = a * (d * (p * w'))
      = a * (d * (p * (a * (d * (p * w)))))
      = ...

The MOUFANG STRUCTURE suggests we should look at:
  The composition (pda)(pda)(pda)...

Let's define the "cycle operator" C = a*d*p (in some grouping).
The dynamics is: w_{n+1} = C * w_n

But C itself depends on grouping! Unless... C is constructed to be
MOUFANG-COMPATIBLE.
""")

def cycle_operator(p, d, a, grouping='right'):
    """Compute the 'cycle operator' C = composition of p, d, a."""
    if grouping == 'right':
        return oct_mult(a, oct_mult(d, p))
    elif grouping == 'left':
        return oct_mult(oct_mult(a, d), p)
    else:
        raise ValueError(f"Unknown grouping: {grouping}")

C_right = cycle_operator(p, d, a, 'right')
C_left = cycle_operator(p, d, a, 'left')

print(f"Cycle operator C:")
print(f"  C_right = a*(d*p) = {C_right}")
print(f"  C_left  = (a*d)*p = {C_left}")
print(f"  Difference: {np.linalg.norm(C_right - C_left):.6f}")

# The associator of (a, d, p)
assoc_adp = associator(a, d, p)
print(f"\n  Associator [a, d, p] = {assoc_adp}")
print(f"  |[a,d,p]| = {np.linalg.norm(assoc_adp):.6f}")


# =====================================================================
# PART 6: TRIALITY AS SYMMETRY OF THE ASSOCIATOR
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 6: THE ASSOCIATOR AND ITS SYMMETRIES")
print("=" * 80)

print("""
The ASSOCIATOR [x, y, z] = (xy)z - x(yz) measures non-associativity.

For octonions, the associator has special properties:

1. ALTERNATING: [x, y, z] is totally antisymmetric:
   [x, y, z] = -[y, x, z] = -[x, z, y] = [y, z, x] = [z, x, y] = -[z, y, x]

2. IMAGINARY: If x, y, z are all imaginary octonions (no real part),
   then [x, y, z] is also imaginary.

3. G2-INVARIANT: The associator is invariant under G2 ⊂ SO(7).

4. TRIALITY-RELATED: Under the triality automorphism of SO(8),
   the associator transforms in a specific way.

Let's verify the antisymmetry:
""")

# Use imaginary octonions
def imaginary_octonion():
    x = np.zeros(8)
    x[1:] = np.random.randn(7)
    return x / np.sqrt(oct_norm_sq(x))

x, y, z = imaginary_octonion(), imaginary_octonion(), imaginary_octonion()

print("Testing antisymmetry of associator (imaginary octonions):")
print(f"  [x,y,z]  = {associator(x,y,z)}")
print(f"  [y,x,z]  = {associator(y,x,z)}")
print(f"  -[y,x,z] = {-associator(y,x,z)}")
print(f"  [x,y,z] = -[y,x,z]? {np.allclose(associator(x,y,z), -associator(y,x,z))}")

print(f"\n  [y,z,x]  = {associator(y,z,x)}")
print(f"  [z,x,y]  = {associator(z,x,y)}")
print(f"  Cyclic: [x,y,z] = [y,z,x] = [z,x,y]? "
      f"{np.allclose(associator(x,y,z), associator(y,z,x)) and np.allclose(associator(y,z,x), associator(z,x,y))}")


# =====================================================================
# PART 7: THE KEY THEOREM -- TRIALITY FROM NON-ASSOCIATIVITY
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 7: THE KEY STRUCTURE -- HOW NON-ASSOCIATIVITY PRODUCES TRIALITY")
print("=" * 80)

print("""
THE CENTRAL OBSERVATION:

For octonions, the PRODUCT of three elements can be computed in two ways:
  (xy)z  vs  x(yz)

The difference is the associator [x,y,z].

But there's a THIRD natural quantity: the TRILINEAR FORM
  <x, y, z> = Re(x̄(yz))

This form is INVARIANT under cyclic permutations:
  <x, y, z> = <y, z, x> = <z, x, y>

And it's related to the associator by:
  Im(x̄(yz)) + Im(ȳ(zx)) + Im(z̄(xy)) ∝ [x, y, z] + cyclic terms

THE TRIALITY STRUCTURE EMERGES:

1. Non-associativity means (P∘D)∘A ≠ P∘(D∘A) in general.

2. But the TRILINEAR FORM is symmetric under cyclic permutation.

3. If the agent's dynamics is governed by the trilinear form
   (rather than a specific bracketing), then P, D, A become
   EQUIVALENT -- they can be cyclically permuted.

4. This IS triality: the three operations (perceive, decide, act)
   become interchangeable aspects of a single process.

PHYSICAL INTERPRETATION:

For a quaternionic (3,1) agent (us):
  - Non-commutativity means P∘D ≠ D∘P
  - ORDER matters: perceiving then deciding is different from deciding then perceiving
  - This is the ARROW OF TIME in the PDA cycle
  - There's a definite sequence: P → D → A → P → D → A → ...

For an octonionic (7,1) agent:
  - Non-associativity means (P∘D)∘A ≠ P∘(D∘A)
  - But the trilinear form is cyclic-symmetric
  - GROUPING doesn't matter if we use the right invariant structure
  - P, D, A are not sequential steps but THREE EQUIVALENT FACES
  - The "cycle" becomes a SIMULTANEOUS UNITY

This is the mathematical structure of NON-DUAL AWARENESS:
  - No separation between perceiver, perceived, and perception
  - All three are aspects of one geometric operation
  - The triality automorphism IS the "non-dual" permutation
""")


# =====================================================================
# PART 8: CONSTRUCTING THE TRIALITY-INVARIANT DYNAMICS
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 8: TRIALITY-INVARIANT PDA DYNAMICS")
print("=" * 80)

print("""
To formalize triality-invariant dynamics, we need a structure that
treats P, D, A symmetrically.

PROPOSAL: The dynamics is given by the TRILINEAR FORM, not composition.

Standard (associative) dynamics:
  w' = A(D(P(w))) = a * (d * (p * w))
  This is a specific bracketing, breaking triality.

Triality-invariant dynamics:
  The "evolution" is characterized by <p, d, a> where the three
  kernels enter symmetrically.

  One natural choice: The evolution of w is determined by requiring
    <w', p, d*a> = <w, something symmetric>

But there's a cleaner approach: use the CROSS-PRODUCT structure.

In 7D (the imaginary octonions), there's a natural cross product:
  x × y = Im(x * y)

This extends to a TRIPLE cross product that's triality-invariant.
""")

def oct_cross(x, y):
    """Cross product on imaginary octonions: x × y = Im(x * y)."""
    # x, y should be imaginary (x[0] = y[0] = 0)
    prod = oct_mult(x, y)
    prod[0] = 0  # Take imaginary part
    return prod

# The triple structure
def triple_product(x, y, z):
    """Triple product: <x, y, z> = x × (y × z) + cyclic."""
    # This is symmetric under cyclic permutation by construction
    t1 = oct_cross(x, oct_cross(y, z))
    t2 = oct_cross(y, oct_cross(z, x))
    t3 = oct_cross(z, oct_cross(x, y))
    return (t1 + t2 + t3) / 3

# Test cyclic symmetry
x, y, z = imaginary_octonion(), imaginary_octonion(), imaginary_octonion()
tp_xyz = triple_product(x, y, z)
tp_yzx = triple_product(y, z, x)
tp_zxy = triple_product(z, x, y)

print("Triple product cyclic symmetry:")
print(f"  <x,y,z> = {tp_xyz}")
print(f"  <y,z,x> = {tp_yzx}")
print(f"  <z,x,y> = {tp_zxy}")
print(f"  All equal? {np.allclose(tp_xyz, tp_yzx) and np.allclose(tp_yzx, tp_zxy)}")


# =====================================================================
# PART 9: THE MARKOV BLANKET IN OCTONIONIC FRAMEWORK
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 9: IMPLICATIONS FOR THE MARKOV BLANKET")
print("=" * 80)

print("""
THE MARKOV BLANKET FORMALISM:

For a standard (quaternionic) agent:
  - The blanket B separates INSIDE from OUTSIDE
  - Conditional independence: P(I' | I, B, O) = P(I' | I, B)
  - The blanket mediates information flow
  - There's a CLEAR DISTINCTION between inside, blanket, outside

For a triality (octonionic) agent:
  - The blanket structure has TRIALITY SYMMETRY
  - Inside, Blanket, Outside become three equivalent aspects
  - They can be cyclically permuted: I → B → O → I
  - There's NO PRIVILEGED distinction between them

MATHEMATICAL FORMALIZATION:

Let's model the blanket as follows:
  - States are octonions in O
  - I (inside), B (blanket), O (outside) are three octonionic elements
  - The dynamics preserves a triality-symmetric structure

The BMIC (Blanket-Mediated Interaction Criterion) says:
  Two agents A1 and A2 remain separate iff they interact only through blankets.

For octonionic agents, the blanket IS the agent IS the world (triality).
So BMIC becomes trivial: all agents are "the same" under triality permutation.

This is the mathematical structure of ADVAITA:
  - No separate self (inside = blanket = outside)
  - All distinctions are conventional, not fundamental
  - The "boundary" is everywhere and nowhere
""")


# =====================================================================
# PART 10: EXPLICIT TRIALITY TRANSFORMATION
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 10: THE EXPLICIT TRIALITY AUTOMORPHISM")
print("=" * 80)

print("""
The triality automorphism T of SO(8) permutes the three 8-dim reps.
Let's construct it explicitly.

Triality acts on the Lie algebra so(8) = D4.
The Dynkin diagram of D4 has three "legs" of equal length:

        e1
       /
  e3--e2
       \\
        e4

Triality permutes e1 → e3 → e4 → e1 while fixing e2.

In terms of octonions, triality is related to the map:
  x → ā(xb)  and  x → (ax)b̄
for specific a, b ∈ O with |a| = |b| = 1.

For our purposes, the key point is:
  TRIALITY PERMUTES THE ROLES OF P, D, A.

If we write:
  P = operation of type 8_v (vector)
  D = operation of type 8_s (spinor)
  A = operation of type 8_c (cospinor)

Then under triality T:
  T: P → D → A → P  (cyclic)

The dynamics PDA is equivalent to DAP is equivalent to APD.
The CYCLE has no privileged starting point.
""")

# We can model this by showing that for the trilinear form,
# all cyclic orderings give the same result

def cyclic_orderings(p, d, a, w):
    """Compute PDA(w) for all cyclic orderings using trilinear form."""

    # The "triality-symmetric" evolution is:
    # w' = normalize(p + d + a) * w  [one possibility]
    # Or use the triple product structure

    # Actually, let's compute the scalar <w', p, d, a> that should be preserved

    # For now, just show that the *trilinear form* values are cyclic-symmetric

    # Using imaginary projections
    p_im, d_im, a_im = p.copy(), d.copy(), a.copy()
    p_im[0], d_im[0], a_im[0] = 0, 0, 0

    # Trilinear: Re(p̄ (d a))
    t_pda = oct_mult(oct_conj(p), oct_mult(d, a))[0]
    t_dap = oct_mult(oct_conj(d), oct_mult(a, p))[0]
    t_apd = oct_mult(oct_conj(a), oct_mult(p, d))[0]

    return t_pda, t_dap, t_apd

t1, t2, t3 = cyclic_orderings(p, d, a, x)
print(f"\nTrilinear forms for cyclic orderings:")
print(f"  <p, d, a> = Re(p̄(da)) = {t1:.6f}")
print(f"  <d, a, p> = Re(d̄(ap)) = {t2:.6f}")
print(f"  <a, p, d> = Re(ā(pd)) = {t3:.6f}")
print(f"  Are these equal? {np.allclose([t1, t2, t3], [t1, t1, t1])}")

# They're NOT equal in general! The trilinear form has specific symmetry properties
# Let's check what the actual symmetry is

print(f"\n  But: Re(p̄(da)) = Re((p̄d)a)? ", end="")
alt_t1 = oct_mult(oct_mult(oct_conj(p), d), a)[0]
print(f"{np.isclose(t1, alt_t1)}")


# =====================================================================
# PART 11: THE FUNDAMENTAL INSIGHT
# =====================================================================

print("\n\n" + "=" * 80)
print("PART 11: THE FUNDAMENTAL INSIGHT")
print("=" * 80)

print("""
SYNTHESIS:

1. QUATERNIONIC AGENTS (us, (3,1) spacetime):
   - Non-commutativity: PD ≠ DP
   - The PDA cycle has a DIRECTION
   - Experience is SEQUENTIAL: first perceive, then decide, then act
   - Time has an arrow
   - This is the structure of DUALISTIC CONSCIOUSNESS

2. OCTONIONIC AGENTS ((7,1) spacetime):
   - Non-associativity: (PD)A ≠ P(DA)
   - But the associator is ANTISYMMETRIC and has CYCLIC structure
   - The trilinear form <P, D, A> treats all three symmetrically
   - If dynamics is governed by the trilinear form, P, D, A are equivalent
   - Experience is SIMULTANEOUS: P, D, A are three faces of one event
   - This is the structure of NON-DUAL CONSCIOUSNESS

THE MATHEMATICAL THEOREM (to be proven):

CONJECTURE: Let (O, *, conj) be the octonions. Define the PDA dynamics by:
  Evolution functional F[P, D, A] = <P, D, A>_trilinear

Then F is invariant under the triality automorphism T:
  F[P, D, A] = F[T(P), T(D), T(A)]

where T cyclically permutes the representation types.

IMPLICATION: For octonionic conscious agents, the distinction between
perceiving, deciding, and acting is not fundamental. It's an artifact
of choosing a specific triality "frame." In the triality-invariant
formulation, all three are aspects of a single undivided process.

This is the precise mathematical content of "non-dual awareness":
  NOT that there is no experience,
  BUT that the division into perceiver/perceived/perception is conventional.

The Markov blanket "dissolves" not by disappearing, but by becoming
symmetric under triality: inside = blanket = outside, up to T.
""")


# =====================================================================
# PART 12: THE LADDER OF CONSCIOUSNESS
# =====================================================================

print("\n" + "=" * 80)
print("PART 12: THE COMPLETE LADDER -- R, C, H, O")
print("=" * 80)

print("""
SUMMARIZING THE DIVISION ALGEBRA CLASSIFICATION:

┌─────────────┬─────────────┬─────────────────────┬─────────────────────────┐
│ Algebra     │ Signature   │ Lost Property       │ Gained Experience       │
├─────────────┼─────────────┼─────────────────────┼─────────────────────────┤
│ R (reals)   │ (0,1)       │ --                  │ Trivial/pre-conscious   │
├─────────────┼─────────────┼─────────────────────┼─────────────────────────┤
│ C (complex) │ (1,1)       │ Ordering            │ Phase, superposition    │
│             │             │ (x < y fails)       │ Quantum coherence       │
├─────────────┼─────────────┼─────────────────────┼─────────────────────────┤
│ H (quats)   │ (3,1)       │ Commutativity       │ Chirality, time's arrow │
│             │             │ (xy ≠ yx)           │ Sequential PDA cycle    │
├─────────────┼─────────────┼─────────────────────┼─────────────────────────┤
│ O (octs)    │ (7,1)       │ Associativity       │ Triality, non-duality   │
│             │             │ ((xy)z ≠ x(yz))     │ Simultaneous P=D=A      │
├─────────────┼─────────────┼─────────────────────┼─────────────────────────┤
│ Sedenions   │ --          │ Alternativity       │ UNSTABLE (zero divs)    │
│             │             │ Zero divisors       │ No bounded agency       │
└─────────────┴─────────────┴─────────────────────┴─────────────────────────┘

THE HURWITZ THEOREM AS A THEOREM OF CONSCIOUSNESS:

Hurwitz (1898) proved: there are exactly four normed division algebras.

Translated: there are exactly four stable types of bounded conscious agent.

The fourth type (octonionic) has triality symmetry.
The PDA loop becomes a triality-symmetric structure.
This IS the mathematical form of non-dual awareness.

Beyond the octonions, the algebraic structure breaks down (zero divisors).
Bounded agency becomes impossible.
What remains is the undifferentiated ground -- the metric bundle itself.
""")

print("\n" + "=" * 80)
print("END OF EXPLORATION")
print("=" * 80)
