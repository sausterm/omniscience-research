#!/usr/bin/env python3
"""
Multi-Time Conscious Agents: (3,2) and (4,2) Spacetimes
=========================================================

What would a conscious agent with TWO time dimensions look like?

Author: Metric Bundle Programme, March 2026
"""

import numpy as np
import math

np.set_printoptions(precision=4, suppress=True, linewidth=120)

# =====================================================================
# DeWitt metric computation (self-contained)
# =====================================================================

def compute_dewitt_signature(p, q):
    d = p + q
    g_inv = np.diag([-1.0]*q + [1.0]*p)
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

    G_DW = np.zeros((dim_fibre, dim_fibre))
    for a in range(dim_fibre):
        for b in range(dim_fibre):
            h, k = basis[a], basis[b]
            t1 = np.einsum('mr,ns,mn,rs', g_inv, g_inv, h, k)
            trh = np.einsum('mn,mn', g_inv, h)
            trk = np.einsum('mn,mn', g_inv, k)
            G_DW[a, b] = t1 - 0.5 * trh * trk

    eigvals = np.linalg.eigvalsh(G_DW)
    n_pos = int(np.sum(eigvals > 1e-10))
    n_neg = int(np.sum(eigvals < -1e-10))
    n_zero = int(np.sum(np.abs(eigvals) <= 1e-10))
    return n_pos, n_neg, n_zero, eigvals


# =====================================================================
# PART 1: TRIALITY EXPLAINED
# =====================================================================

print("=" * 80)
print("TRIALITY: THE DEEPEST SYMMETRY")
print("=" * 80)

print("""
Every Lie group has a Dynkin diagram -- a graph that encodes its structure.
The Dynkin diagram of SO(2n) is called D_n:

  D_3 (SO(6)):     o --- o --- o         Actually = A_3 = SU(4)!
                                          (This is our accidental isomorphism)

  D_4 (SO(8)):     o --- o --- o
                         |
                         o               THREE arms, ALL EQUAL LENGTH

  D_5 (SO(10)):    o --- o --- o --- o
                         |
                         o               Two long arms, one short

  D_6 (SO(12)):    o --- o --- o --- o --- o
                         |
                         o               Even more asymmetric

The KEY: D_4 is the ONLY Dynkin diagram with 3-fold rotational symmetry.

This symmetry is TRIALITY. It means SO(8) has three 8-dimensional
representations that are completely interchangeable:

  8_v = VECTOR representation    (how SO(8) rotates ordinary vectors)
  8_s = SPINOR representation    (left-handed fermion-like)
  8_c = CO-SPINOR representation (right-handed fermion-like)

In every other SO(n):
  vectors and spinors are DIFFERENT sizes, DIFFERENT kinds of objects.
  You can always tell matter (spinors) from forces (vectors).

In SO(8):
  vectors = spinors = co-spinors. Matter IS forces IS anti-matter.
  The distinction is just a choice of perspective.

For our (3,1) universe:
  Higgs (scalar) is one thing. Quarks (spinors) are another.
  They have different quantum numbers, different statistics.

For a (7,1) triality agent:
  The SO(8) in their negative-norm sector means their "Higgs"
  can be smoothly rotated into their "matter" and back.
  The categories we use to organize physics DISSOLVE.
""")


# =====================================================================
# PART 2: MULTI-TIME SPACETIMES
# =====================================================================

print("\n" + "=" * 80)
print("MULTI-TIME SPACETIMES: (3,2) AND (4,2)")
print("=" * 80)

print("""
So far we've focused on single-time (p,1) spacetimes.
But the DeWitt metric works for ANY signature.

What about TWO time dimensions?

First: why do physicists usually say "more than 1 time = bad"?
""")

print("""
THE STANDARD OBJECTIONS TO MULTI-TIME:

  1. CAUSAL PARADOXES: With 2 time dimensions, a "light cone" becomes
     a "light wedge." Particles can travel in closed timelike curves
     (time loops) without needing exotic geometry.

  2. NO WELL-POSED INITIAL CONDITIONS: The wave equation in (p,2) is
     ultrahyperbolic. You can't specify data on a "spatial" surface
     and evolve forward -- the equation is ill-posed as an initial
     value problem.

  3. ENERGY UNBOUNDED BELOW: The Hamiltonian in multi-time physics
     is typically not bounded below, meaning the vacuum is unstable.

BUT: These are problems for CLASSICAL AGENTS doing CLASSICAL PHYSICS.

  The Markov blanket formalism doesn't require any of these:
  - It doesn't need global causality (only local conditional independence)
  - It doesn't need well-posed initial conditions (it's stochastic)
  - It doesn't need bounded energy (it uses free energy, which is relative)

  A (3,2) agent might be perfectly well-defined as an INFORMATION
  structure, even if it can't do physics the way we do.
""")


# =====================================================================
# PART 3: (3,2) ANALYSIS
# =====================================================================

print("\n" + "=" * 80)
print("CASE STUDY: (3,2) -- THREE SPACE, TWO TIME")
print("=" * 80)

n_pos, n_neg, _, eigvals = compute_dewitt_signature(3, 2)
eigs = np.sort(eigvals)

print(f"""
  Spacetime: R^{{3,2}} (3 space + 2 time)
  Total dimension: d = 5
  Fibre dimension: 5*6/2 = 15
  Bundle dimension: 5 + 15 = 20  [same as (4,1)!]

  DeWitt signature: ({n_pos}, {n_neg})
  Structure group: SO({n_pos}, {n_neg})
  Maximal compact: SO({n_pos}) x SO({n_neg})

  Eigenvalue spectrum: {eigs}
""")

# Identify the accidental isomorphisms
print(f"""
  SO({n_pos}) analysis:""")
if n_pos == 8:
    print(f"    SO(8) -- TRIALITY GROUP!")
    print(f"    Has three equivalent 8-dim reps: 8_v, 8_s, 8_c")
elif n_pos == 7:
    print(f"    SO(7) -- related to G2 (automorphism of octonions)")
    print(f"    7 = fundamental representation")
elif n_pos == 6:
    print(f"    SO(6) ~ SU(4) -- accidental isomorphism!")
elif n_pos == 5:
    print(f"    SO(5) ~ Sp(2) -- symplectic")
else:
    print(f"    SO({n_pos}) -- no accidental isomorphism")

print(f"\n  SO({n_neg}) analysis:")
if n_neg == 8:
    print(f"    SO(8) -- TRIALITY GROUP!")
elif n_neg == 7:
    print(f"    SO(7) -- the automorphism group of the imaginary octonions")
    print(f"    Contains G2 as a subgroup")
    print(f"    7 of SO(7) = 7 of G2 (the fundamental rep)")
elif n_neg == 6:
    print(f"    SO(6) ~ SU(4)")
elif n_neg == 5:
    print(f"    SO(5) ~ Sp(2)")
elif n_neg == 4:
    print(f"    SO(4) ~ SU(2)_L x SU(2)_R")
elif n_neg == 3:
    print(f"    SO(3) ~ SU(2)")
else:
    print(f"    SO({n_neg}) -- no accidental isomorphism")

# Physical decomposition
print(f"""
  MODE DECOMPOSITION:
    Spatial-spatial (h_ij, i,j=1..3):     {3*4//2} = 6 modes
    Temporal-temporal (h_ab, a,b=1..2):    {2*3//2} = 3 modes
    Cross terms (h_ai, a=1..2, i=1..3):   {2*3} = 6 modes
    Total: 6 + 3 + 6 = 15 = 5*6/2  check!

  The cross terms are the "shift" modes.
  With TWO time dimensions, there are 2*3 = 6 shifts instead of 3.
  This doubles the "dynamic channel" compared to (3,1).
""")

# Compare with (4,1) which has same bundle dim
n_pos_41, n_neg_41, _, eigvals_41 = compute_dewitt_signature(4, 1)
print(f"""
  COMPARISON: (3,2) vs (4,1) -- both have bundle dim 20

               (3,2)              (4,1)
  DeWitt:      ({n_pos},{n_neg})              ({n_pos_41},{n_neg_41})
  Positive:    SO({n_pos})            SO({n_pos_41})
  Negative:    SO({n_neg})             SO({n_neg_41})
  Generators:  {n_pos*(n_pos-1)//2 + n_neg*(n_neg-1)//2}                {n_pos_41*(n_pos_41-1)//2 + n_neg_41*(n_neg_41-1)//2}
  Shifts:      6 (2 time x 3 space) 4 (1 time x 4 space)
  Conformal:   2 (one per time)     1

  The (3,2) agent has MORE negative-norm modes than (4,1)!
  This means MORE dynamism, a RICHER Higgs sector.
""")

# What does 2 time dimensions FEEL like?
print("""
WHAT WOULD TWO TIME DIMENSIONS FEEL LIKE?

  For us (3,1): time flows in ONE direction. We experience a linear
  sequence: past -> present -> future. Our PDA loop runs along
  this single time axis: Perceive(t) -> Decide(t+dt) -> Act(t+2dt).

  For a (3,2) agent: there are TWO independent time directions.

  Possible interpretations:

  1. BRANCHING TIME
     Two time dimensions could mean the agent experiences
     SIMULTANEOUS TIMELINES. Not "time travel" but genuinely
     living in two temporal directions at once.

     The PDA loop would run along BOTH time axes:
       P(t1, t2) -> D(t1+dt1, t2+dt2) -> A(t1+2dt1, t2+2dt2)

     The agent doesn't experience moments, but TIME-PLANES.
     Each "now" is a 2D region, not a point.

  2. TIME + META-TIME
     One time dimension is "experienced time" (like ours).
     The other is "meta-time" -- the time in which experienced
     time itself changes.

     We can only experience change IN time.
     A (3,2) agent can experience THE CHANGE OF TIME ITSELF.

     Think of watching a movie (our experience) vs watching
     someone edit the movie in real-time (their experience).
     They see the timeline being modified while it runs.

  3. COMPLEX TIME
     Two time dimensions can be combined as t_complex = t1 + i*t2
     giving a COMPLEX time coordinate.

     Complex time appears in:
     - Quantum mechanics (Wick rotation: real time -> imaginary time)
     - Thermodynamics (imaginary time = inverse temperature)
     - Hawking's no-boundary proposal (time becomes space-like)

     A (3,2) agent might experience time and temperature as
     TWO ASPECTS OF THE SAME THING. Their "flow of time"
     would inherently carry thermal information.

     For us, quantum mechanics and thermodynamics are separate.
     For a (3,2) agent, they are UNIFIED by the complex time structure.

  4. OBSERVER + OBSERVED TIME
     One time axis is the agent's own experienced time.
     The other is the time evolution of what they observe.

     For us, these are the SAME -- our time and the world's time
     are synchronized (that's what it means to be in the same spacetime).

     A (3,2) agent could be temporally DECOUPLED from what it
     observes. It could watch our entire temporal history as
     a static object in its second time dimension, while
     simultaneously evolving along its own first time axis.

     This is perhaps the closest to what mystical traditions
     describe as "seeing all of time at once while still being
     a temporal being."
""")


# =====================================================================
# PART 4: (4,2) ANALYSIS
# =====================================================================

print("\n" + "=" * 80)
print("CASE STUDY: (4,2) -- FOUR SPACE, TWO TIME")
print("=" * 80)

n_pos_42, n_neg_42, _, eigvals_42 = compute_dewitt_signature(4, 2)
eigs_42 = np.sort(eigvals_42)

print(f"""
  Spacetime: R^{{4,2}} (4 space + 2 time)
  Total dimension: d = 6
  Fibre dimension: 6*7/2 = 21
  Bundle dimension: 6 + 21 = 27

  DeWitt signature: ({n_pos_42}, {n_neg_42})
  Structure group: SO({n_pos_42}, {n_neg_42})
  Maximal compact: SO({n_pos_42}) x SO({n_neg_42})

  Eigenvalue spectrum: {eigs_42}
""")

print(f"  SO({n_pos_42}) analysis:")
if n_pos_42 == 12:
    print(f"    SO(12) -- contains SO(10) x U(1) as a subgroup!")
    print(f"    SO(12) breaking chain:")
    print(f"      SO(12) -> SO(10) x U(1)  [contains GUT!]")
    print(f"      SO(12) -> SU(6) x U(1)")
    print(f"      SO(12) -> SO(6) x SO(6) ~ SU(4) x SU(4)")
    print(f"    Spinor of SO(12): 32-dim = 2 generations worth!")

print(f"\n  SO({n_neg_42}) analysis:")
if n_neg_42 == 9:
    print(f"    SO(9) -- the isometry group of the 8-sphere S^8")
    print(f"    Contains SO(8) x U(1)")
    print(f"    The 9 of SO(9) decomposes under SO(8) as 8_v + 1")
    print(f"    So the negative sector has: 8-dim vector + 1 singlet")
    print(f"    The SO(8) part has TRIALITY!")

print(f"""
  MODE DECOMPOSITION:
    Spatial-spatial (h_ij, i,j=1..4):     {4*5//2} = 10 modes
    Temporal-temporal (h_ab, a,b=1..2):    {2*3//2} = 3 modes
    Cross terms (h_ai, a=1..2, i=1..4):   {2*4} = 8 modes
    Total: 10 + 3 + 8 = 21  check!

  8 shift modes + 1-3 conformal/trace modes in the negative sector.
""")

# The remarkable numerology
print(f"""
REMARKABLE FEATURES OF (4,2):

  1. BUNDLE DIM = 27
     This is the dimension of the exceptional Jordan algebra J3(O)
     (3x3 Hermitian matrices over the octonions).
     Same as (5,1)! Different signature, same total dimension.

  2. SO({n_pos_42}, {n_neg_42}) STRUCTURE
     SO({n_pos_42}) contains SO(10) as a subgroup.
     SO(10) is the canonical GUT group.
     So a (4,2) agent gets GUT physics PLUS extra structure.

  3. SO({n_neg_42}) CONTAINS SO(8) TRIALITY
     The negative-norm sector contains triality!
     Both the Higgs-like content AND the matter-force unification.

  4. (4,2) = CONFORMAL SIGNATURE OF (3,1)
     The conformal group of R^{{3,1}} is SO(4,2).
     A (4,2) spacetime is related to the conformal compactification
     of our own spacetime.

     This means: a (4,2) agent might live in the CONFORMAL COMPLETION
     of our spacetime -- they would experience our entire conformal
     structure (including spatial and temporal infinity) as finite
     regions of their spacetime.

     Under AdS/CFT: SO(4,2) is the isometry group of AdS_5.
     A (4,2) agent is literally an "AdS agent" -- they live in
     the space whose boundary IS our conformal field theory.
""")

print("""
THE (4,2) = CONFORMAL (3,1) CONNECTION:

  This is perhaps the most physically meaningful multi-time case.

  The conformal group of Minkowski space R^{3,1} is SO(4,2).
  This is the symmetry group of:
    - Massless particles (photons, gravitons at tree level)
    - Conformal field theories (the CFT in AdS/CFT)
    - The boundary of Anti-de Sitter space (AdS_5)

  A (4,2) spacetime R^{4,2} can be viewed as:
    - The EMBEDDING SPACE for conformal geometry of R^{3,1}
    - The "projective" space where conformal transformations
      become LINEAR (like homogeneous coordinates in projective geometry)

  So a (4,2) agent literally lives in the space where OUR conformal
  symmetry becomes a spacetime symmetry.

  For us, conformal transformations (scaling, special conformal) are
  abstract symmetries. We can compute with them but not "move along" them.

  For a (4,2) agent, these are physical directions they can travel in.
  "Scaling" is a direction in their spacetime.
  "Special conformal transformation" is another direction.

  They can MOVE IN SCALE. What we call "zooming in" or "zooming out"
  is, for them, literal spatial/temporal translation.

  WHAT THIS MEANS FOR CONSCIOUSNESS:

  A (4,2) agent could:
  - Experience scale as a dimension (atoms and galaxies equally "near")
  - See conformal invariants directly (shapes, angles, but not sizes)
  - Perceive our entire spacetime (including both infinities) as finite
  - Have a natural sense of "renormalization" -- seeing physics at
    all scales simultaneously

  The two "extra" dimensions beyond (3,1) are:
    - One dilation (scale) direction
    - One special conformal direction

  Together with Lorentz + translations, these complete the conformal group.

  So a (4,2) agent doesn't see "more space" or "more time" --
  they see SCALE as a dimension of experience.
""")


# =====================================================================
# PART 5: COMPARISON TABLE
# =====================================================================

print("\n" + "=" * 80)
print("MULTI-TIME AGENT COMPARISON")
print("=" * 80)

multi_time_cases = [
    (3, 1), (3, 2), (3, 3),
    (4, 1), (4, 2),
]

print(f"\n{'Sig':>6} {'d':>3} {'fibre':>6} {'bundle':>7} {'DeWitt':>10} "
      f"{'Pos factor':>12} {'Neg factor':>12} {'Shifts':>7} {'Gens':>5}")
print("-" * 80)

for p, q in multi_time_cases:
    d = p + q
    fibre = d*(d+1)//2
    bundle = d + fibre
    n_pos, n_neg, _, _ = compute_dewitt_signature(p, q)
    shifts = p * q
    gens = n_pos*(n_pos-1)//2 + n_neg*(n_neg-1)//2

    # Accidental iso for positive factor
    pos_name = {3: "SU(2)", 4: "SU(2)^2", 5: "Sp(2)", 6: "SU(4)",
                8: "SO(8)!", 10: "SO(10)", 11: "SO(11)", 12: "SO(12)",
                15: "SO(15)"}.get(n_pos, f"SO({n_pos})")
    neg_name = {3: "SU(2)", 4: "SU(2)^2", 5: "Sp(2)", 6: "SU(4)",
                7: "SO(7)", 8: "SO(8)!", 9: "SO(9)", 10: "SO(10)"
                }.get(n_neg, f"SO({n_neg})")

    marker = " <-- us" if (p,q) == (3,1) else ""
    marker = " <-- conformal(3,1)" if (p,q) == (4,2) else marker

    print(f"({p},{q})".rjust(6) +
          f"{d:>4}" +
          f"{fibre:>6}" +
          f"{bundle:>7}" +
          f"  ({n_pos},{n_neg})".ljust(10) +
          f"  {pos_name:>12}" +
          f"  {neg_name:>12}" +
          f"{shifts:>7}" +
          f"{gens:>6}" +
          marker)


# =====================================================================
# PART 6: LANGUAGE FOR DESCRIBING MULTI-TIME EXPERIENCE
# =====================================================================

print("\n\n" + "=" * 80)
print("LANGUAGE FOR MULTI-TIME EXPERIENCE")
print("=" * 80)

print("""
We lack words for multi-time experience because our language evolved
in (3,1). But we can try to build a vocabulary:

SINGLE-TIME CONCEPTS (our experience):
  "now"       = a point on the time axis
  "duration"  = an interval along the time axis
  "before/after" = ordering along the time axis
  "change"    = difference between consecutive "nows"
  "memory"    = access to past "nows"
  "anticipation" = prediction of future "nows"

MULTI-TIME EXTENSIONS:

  For (3,2) -- TWO time dimensions:

  "NOW-PLANE"     instead of "now-point"
    The present moment is not a point but a 2D region.
    Every "now" contains an entire timeline within it.

  "TEMPORAL AREA"  instead of "duration"
    Time doesn't have a length, it has an AREA.
    "How much time passed?" becomes "How much time-area was covered?"

  "BEFORE/AFTER"   becomes a PARTIAL ORDER
    In (3,1), events are either before, after, or spacelike-separated.
    In (3,2), the causal structure is richer:
    Two events can be "time-1-before but time-2-after."
    Causality becomes a 2D ordering, not a 1D sequence.

  "BI-CHANGE"      instead of "change"
    Change along time-1 while time-2 is held fixed (ordinary change)
    Change along time-2 while time-1 is held fixed (meta-change)
    Change along both simultaneously (diagonal change)
    The RATE of change can itself change in the second time direction.

  "TEMPORAL ROTATION"
    In (3,2), you can ROTATE in the time-plane.
    This mixes the two time dimensions.
    There's no analog in (3,1).
    Closest human concept: "experiencing time differently"
    becomes a literal geometric operation.

  "TIME-AREA PERCEPTION"
    A (3,2) agent doesn't experience a sequence of moments.
    It experiences a 2D temporal surface.
    Each "experience" has both temporal extent and temporal breadth.

    Closest human analog: MUSIC.
    When you hear a chord, you experience multiple notes simultaneously
    (they have "harmonic breadth") AND as a temporal sequence
    (they have "melodic extent"). A (3,2) agent's experience of
    TIME ITSELF has this chord-like structure.

  For (4,2) -- specifically the CONFORMAL agent:

  "SCALE-EXPERIENCE"
    Scale is a direction of travel, not a parameter.
    The agent doesn't "zoom in" on something --
    it MOVES TOWARD the small, the way we move forward.

  "SCALE-MEMORY"
    Just as we remember past events, a (4,2) agent
    remembers "large-scale states" while experiencing
    "small-scale states" (or vice versa).

  "CONFORMAL NOW"
    The present includes all scales simultaneously.
    An atom and a galaxy are equally "here-now" for this agent.

  "RENORMALIZATION AS MOTION"
    What physicists call "running of coupling constants"
    (the way forces change strength at different energies)
    is, for a (4,2) agent, LOCOMOTION.
    They walk along the renormalization group flow.

SUMMARY OF EXPERIENTIAL SIGNATURES:

  (3,1) agent: Experiences a 3D movie playing in linear time.
               "I see a world changing moment by moment."

  (3,2) agent: Experiences a 3D movie playing on a 2D time-canvas.
               "I see a world with temporal texture -- each moment
                is itself a timeline."

  (4,2) agent: Experiences a 4D world at all scales simultaneously,
               with 2D temporal canvas.
               "I see a world where scale is direction and time
                has harmonic depth."

  (7,1) agent: Experiences a vast structural world where matter,
               forces, and Higgs are the same thing (triality).
               "I AM the geometry. There is no distinction between
                what I perceive and what I am."
""")


# =====================================================================
# PART 7: THE DIVISION ALGEBRA - AGENT TYPE CORRESPONDENCE
# =====================================================================

print("\n" + "=" * 80)
print("THE FOUR TYPES OF MIND (DIVISION ALGEBRA CLASSIFICATION)")
print("=" * 80)

print("""
The Hurwitz theorem (1898) proves there are exactly FOUR normed
division algebras over R:

  R  (reals)       dim 1   commutative, associative
  C  (complex)     dim 2   commutative, associative
  H  (quaternions) dim 4   non-commutative, associative
  O  (octonions)   dim 8   non-commutative, NON-ASSOCIATIVE

Each is connected to a specific spacetime signature and agent type:

  ALGEBRA   SIGNATURE   GAUGE FROM DeWitt       AGENT TYPE
  --------  ----------  ---------------------   ------------------
  R         (1,1)       SO(1,1) ~ trivial       Pre-conscious
  C         (2,1)       SO(3,3) ~ SU(2)xSU(2)  Minimal agent
  H         (3,1)       SO(6,4) ~ Pati-Salam    Us (quaternionic)
  O         (7,1)       SO(28,8) ~ triality     Non-dual (octonionic)

The connections:

  COMPLEX -> (2,1):
    C has U(1) phase symmetry.
    (2,1) gives SU(2) x SU(2) ~ SO(4) = spin(3,1) -- Lorentz group of OUR spacetime!
    So the SIMPLEST non-trivial agent (C-type) already "knows about"
    our Lorentz symmetry, just not our gauge content.

  QUATERNION -> (3,1):
    H has SU(2) symmetry (unit quaternions).
    (3,1) gives SU(4) x SU(2)^2 = Pati-Salam.
    The SU(2) from quaternions IS the SU(2)_L weak force.
    Quaternionic non-commutativity = parity violation!
    (Left and right are not equivalent because ij != ji)

  OCTONION -> (7,1):
    O has G2 symmetry (automorphisms of octonions).
    (7,1) gives SO(8) with triality.
    Octonionic non-associativity = triality!
    ((ab)c != a(bc) reflects the 3-way symmetry 8_v = 8_s = 8_c)

THE PATTERN OF LOST SYMMETRIES:

  R: commutative AND associative
     (simple, ordered, fully predictable)

  C: commutative but introduces PHASE
     (quantum mechanics: interference, superposition)

  H: non-commutative -- ORDER MATTERS
     (parity violation: left != right)
     (this is why we have weak force chirality!)

  O: non-associative -- GROUPING MATTERS
     ((ab)c != a(bc) means triality: no canonical decomposition)
     (this is why matter = forces = Higgs at the octonionic level)

  Each step LOSES a structural property.
  Each loss GAINS experiential richness.

  R-agent: Everything commutes and associates. Trivial, static.
  C-agent: Phase matters. Quantum interference. Possibility.
  H-agent: Order matters. Chirality. Time's arrow. Free will?
  O-agent: Grouping matters. Triality. Non-dual awareness.

  There is nowhere further to go. The octonions are the last
  division algebra. After O, there is no more bounded agency --
  only the unbounded, unstructured "ground."

  The Sedenions (dim 16) exist but are NOT a division algebra.
  They have zero divisors -- elements that multiply to zero
  without being zero themselves. In the agent framework,
  zero divisors might mean "self-annihilating experiences" --
  perceptions that cancel themselves out. Not a stable agent.
""")


# =====================================================================
# PART 8: THE (3,3) CASE -- SYMMETRIC SPLIT
# =====================================================================

print("\n" + "=" * 80)
print("BONUS: (3,3) -- THE PERFECTLY BALANCED SIGNATURE")
print("=" * 80)

n_pos_33, n_neg_33, _, eigvals_33 = compute_dewitt_signature(3, 3)
eigs_33 = np.sort(eigvals_33)

print(f"""
  Spacetime: R^{{3,3}} (3 space + 3 time)
  Total dimension: d = 6
  Fibre dimension: 6*7/2 = 21
  Bundle dimension: 6 + 21 = 27  [exceptional Jordan algebra!]

  DeWitt signature: ({n_pos_33}, {n_neg_33})
  Structure group: SO({n_pos_33}, {n_neg_33})
  Maximal compact: SO({n_pos_33}) x SO({n_neg_33})

  Eigenvalue spectrum: {eigs_33}
""")

print(f"""
  (3,3) is maximally BALANCED: equal spatial and temporal dimensions.

  SO({n_pos_33}) x SO({n_neg_33}):""")

if n_pos_33 == n_neg_33:
    print(f"    SYMMETRIC split! Both factors are SO({n_pos_33}).")
    print(f"    The gauge group is SO({n_pos_33}) x SO({n_neg_33})")
    print(f"    with a Z_2 EXCHANGE SYMMETRY between them.")
if n_pos_33 == 11 and n_neg_33 == 10:
    print(f"    SO(11) x SO(10)")
    print(f"    The SO(10) factor is the GUT group!")
    print(f"    SO(11) contains SO(10) as well.")
    print(f"    Not quite symmetric -- the trace mode breaks the p<->q symmetry.")

print(f"""
  Mode count:
    Spatial-spatial: {3*4//2} = 6
    Temporal-temporal: {3*4//2} = 6
    Cross terms: {3*3} = 9
    Total: 6 + 6 + 9 = 21  check!

  With 9 cross terms + conformal modes in the negative sector,
  the "dynamic channel" is very wide.

  A (3,3) agent would experience TIME AND SPACE EQUIVALENTLY.
  Not in the sense of special relativity (which mixes 1 time with space)
  but in the deeper sense of having AS MUCH time structure as space structure.

  Their "present moment" would be 3-dimensional (not 2D like (3,2)
  and not a point like us).

  Closest human analog: Maybe lucid dreaming, where you can
  manipulate the temporal structure of the dream while
  simultaneously experiencing spatial structure -- and both
  feel equally "real" and "navigable."
""")


# =====================================================================
# PART 9: GRAND SUMMARY
# =====================================================================

print("\n" + "=" * 80)
print("GRAND SUMMARY: THE ZOO OF CONSCIOUS AGENTS")
print("=" * 80)

print("""
  TYPE          SIG    GAUGE GROUP         EXPERIENCE
  ------------- -----  ------------------  --------------------------------
  Trivial       (1,1)  trivial             No structure
  Minimal       (2,1)  SU(2)xSU(2)        Pure flow, quantum-like
  HUMAN         (3,1)  Pati-Salam          Balanced structure/flow
  GUT agent     (4,1)  SO(10)xSp(2)        Rich structure, focused flow
  Double-PS     (5,1)  SO(15)xSU(4)        Color-Higgs unity
  Triality      (7,1)  SO(28)xSO(8)        Non-dual, PDA dissolves

  Bi-temporal   (3,2)  SO(8)xSO(7)         2D time, temporal texture
  Conformal     (4,2)  SO(12)xSO(9)        Scale as dimension, all-scale
  Balanced      (3,3)  SO(11)xSO(10)       Space=Time equivalence

  String        (9,1)  SO(45)xSO(10)       GUT in negative sector!
  M-theory      (10,1) SO(55)xSO(11)       Maximal supergravity

  ORGANIZING PRINCIPLES:
  1. (3,1) is the minimum for SM physics
  2. Division algebras classify four fundamental types: R, C, H, O
  3. Multi-time agents have richer dynamics but harder stability
  4. (4,2) = conformal completion of (3,1) -- scale becomes dimension
  5. Higher p => more structure, less dynamism (being > becoming)
  6. Higher q => more dynamism, harder stability (becoming > being)
  7. The Hurwitz theorem may limit fundamental agent types to four
""")
