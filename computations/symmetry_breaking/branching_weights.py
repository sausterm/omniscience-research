"""
BRANCHING RULE via WEIGHT THEORY (no Clifford algebra needed)
==============================================================

The 16-dim spinor of Spin(9) has weights (±½,±½,±½,±½) in the
orthonormal basis of the B₄ Cartan. We project these onto the
Cartan of Spin(4) ≅ SU(2)_L × SU(2)_R embedded via the (3,3)
isotropy representation.

This approach computes the branching rule analytically.
"""

import numpy as np
from collections import Counter

# ================================================================
# The 16 weights of the Spin(9) spinor
# ================================================================

# Spin(9) = B₄, rank 4
# Spinor rep = highest weight ω₄ = (½,½,½,½)
# All 16 weights: (±½,±½,±½,½) — all sign combinations

weights_B4 = []
for s1 in [+1, -1]:
    for s2 in [+1, -1]:
        for s3 in [+1, -1]:
            for s4 in [+1, -1]:
                weights_B4.append(np.array([s1/2, s2/2, s3/2, s4/2]))

print(f"Spin(9) spinor: {len(weights_B4)} weights")
print(f"Highest weight: {weights_B4[0]}")

# ================================================================
# The SO(4) → SO(9) embedding via (3,3)
# ================================================================

# R⁹ = R³ ⊗ R³ where SO(3)_L acts on the first factor
# and SO(3)_R on the second.
#
# We need the Cartan generators of SO(3)_L and SO(3)_R as elements
# of the Cartan of SO(9).
#
# SO(9) Cartan generators: H₁, H₂, H₃, H₄
# These generate rotations in the (1,2), (3,4), (5,6), (7,8) planes.
# The 9th direction is "unpaired."
#
# For SO(3)_L ⊗ SO(3)_R on R³⊗R³ = R⁹, we need to choose a
# REAL orthonormal basis of R⁹ and express the Cartan generators
# L₃ ⊗ I and I ⊗ R₃ in terms of the SO(9) Cartan.

# The spin-1 representation of SO(3) on R³:
# Standard basis (x,y,z), with L₃ generating rotation in the (x,y) plane:
# L₃ = [[0,-1,0],[1,0,0],[0,0,0]]
# This has eigenvalues 0, ±i (anti-Hermitian)
# The Hermitian version iL₃ has eigenvalues 0, ±1

# For R⁹ = R³_L ⊗ R³_R, use basis ordered as:
# (x_L⊗x_R, x_L⊗y_R, x_L⊗z_R, y_L⊗x_R, y_L⊗y_R, y_L⊗z_R, z_L⊗x_R, z_L⊗y_R, z_L⊗z_R)

# L₃⊗I acts on R⁹ as the 9×9 matrix:
# L₃ ⊗ I₃ = block structure rotating (x_L, y_L) components

# In this basis, L₃⊗I has the matrix:
# For rows/cols labeled (aL, aR) with aL,aR ∈ {x,y,z}:
# (L₃⊗I)[(aL,aR),(bL,bR)] = (L₃)_{aL,bL} δ_{aR,bR}

# L₃ = [[0,-1,0],[1,0,0],[0,0,0]]
L3_3d = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
R3_3d = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)

L3_9d = np.kron(L3_3d, np.eye(3))  # L₃ ⊗ I
R3_9d = np.kron(np.eye(3), R3_3d)  # I ⊗ R₃

print(f"\nL₃⊗I on R⁹ (9×9 antisymmetric):")
print(L3_9d.astype(int))

print(f"\nI⊗R₃ on R⁹ (9×9 antisymmetric):")
print(R3_9d.astype(int))

# These are antisymmetric 9×9 matrices (SO(9) Lie algebra elements).
# We need to express them in terms of the SO(9) Cartan generators.
#
# The SO(9) Cartan generators in the 9D (vector) rep are:
# H_k = rotation in the (2k-1, 2k) plane, i.e.,
# (H_k)_{2k-1,2k} = -1, (H_k)_{2k,2k-1} = +1, rest zero.
# (using 0-indexed: (H_k)_{2k,2k+1} = -1, etc.)

# Let's identify which pairs of indices are rotated by L₃⊗I and I⊗R₃.

# L₃⊗I: non-zero entries at positions where L₃ acts
# L₃ maps x→-y (index 0→1), y→x (index 1→0), z→0.
# So in R⁹: (x_L, a_R) → -(y_L, a_R) for each a_R
#            (y_L, a_R) → +(x_L, a_R) for each a_R

# Using our ordering: (x_L,x_R)=0, (x_L,y_R)=1, (x_L,z_R)=2,
#                      (y_L,x_R)=3, (y_L,y_R)=4, (y_L,z_R)=5,
#                      (z_L,x_R)=6, (z_L,y_R)=7, (z_L,z_R)=8

# L₃⊗I rotates pairs: (0,3), (1,4), (2,5) — three 2-planes
# I⊗R₃ rotates pairs: (0,1), (3,4), (6,7) — three 2-planes

# But the SO(9) Cartan uses pairs (0,1), (2,3), (4,5), (6,7).
# So L₃⊗I and I⊗R₃ are NOT Cartan generators — they rotate
# in planes that don't align with the standard Cartan!

# We need to diagonalize L₃⊗I and I⊗R₃ (or rather, their
# Hermitian versions) to find the weight projections.

# The key insight: L₃⊗I and I⊗R₃ commute, so we can
# simultaneously diagonalize them over C. The eigenvalues of
# iL₃⊗I are (m_L, m_R) where m_L ∈ {-1,0,1} and the eigenvalue
# depends only on the L-index.

# For the SO(9) spinor weights w = (h₁,h₂,h₃,h₄), we need:
# m_L(w) = eigenvalue of iL₃ on the spinor state with weight w
# m_R(w) = eigenvalue of iR₃ on the spinor state with weight w

# To find this map, we need to express L₃⊗I as a linear combination
# of the SO(9) generators, then evaluate on spinor weights.

# In the vector representation of SO(9), a generator Σ_{pq} acts
# on the vector e_r as: Σ_{pq} e_r = δ_{qr} e_p - δ_{pr} e_q
# (generating rotation in the (p,q) plane)

# L₃⊗I rotates in planes (0,3), (1,4), (2,5):
# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
# (each with coefficient +1, since L₃ has entry +1 at (1,0) and -1 at (0,1),
#  which corresponds to rotation from index 0 to index 3, etc.)

# Verify:
print("\nDecomposing L₃⊗I into SO(9) generators:")
print(f"Non-zero entries of L₃⊗I:")
for i in range(9):
    for j in range(9):
        if abs(L3_9d[i, j]) > 0.5:
            print(f"  ({i},{j}): {L3_9d[i,j]:+.0f}")

print(f"\nNon-zero entries of I⊗R₃:")
for i in range(9):
    for j in range(9):
        if abs(R3_9d[i, j]) > 0.5:
            print(f"  ({i},{j}): {R3_9d[i,j]:+.0f}")

# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}  (rotations in planes (0,3), (1,4), (2,5))
# I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}  (rotations in planes (0,1), (3,4), (6,7))

# In the spinor representation, Σ_{pq} acts as ½γ_p γ_q.
# The weight of a spinor state under the Cartan is determined by
# which planes it "lives in."

# The standard Cartan of SO(9) uses rotations in planes (0,1), (2,3), (4,5), (6,7):
# H₁ = Σ_{01}, H₂ = Σ_{23}, H₃ = Σ_{45}, H₄ = Σ_{67}
# The spinor weights are (h₁, h₂, h₃, h₄) = eigenvalues of (iH₁, iH₂, iH₃, iH₄)

# Now:
# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
# I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67} = H₁ + Σ_{34} + H₄

# Wait, Σ_{34} is not a Cartan generator (Cartan uses (2,3) not (3,4)).
# Σ_{34} ≠ H₂. In fact, H₂ = Σ_{23}.

# I need to be more careful with the index ordering.

# Let me re-derive. The 9 basis vectors of R⁹, ordered as
# tensor product indices:
# Index 0: (x_L, x_R) — L₃ eigenvalue of x_L is 0... wait, no.

# Actually, L₃ acting on R³ maps x↦-y, y↦x, z↦0.
# So L₃ has matrix L₃[0,1] = -1, L₃[1,0] = +1 (and rest 0).
# L₃⊗I on R⁹:
# L₃⊗I maps (x_L,a_R) → -(y_L,a_R) i.e., index 3a_R+0 → -(3·1+a_R) = -(3+a_R)
# and (y_L,a_R) → +(x_L,a_R) i.e., index 3+a_R → +(a_R)
# So for a_R = 0: (0,3) pair, L₃⊗I maps e_0 → -e_3 and e_3 → +e_0
# For a_R = 1: (1,4) pair, maps e_1 → -e_4 and e_4 → +e_1
# For a_R = 2: (2,5) pair, maps e_2 → -e_5 and e_5 → +e_2

# So L₃⊗I = Σ_{30} + Σ_{41} + Σ_{52} (with the convention
# Σ_{pq} maps e_q → e_p and e_p → -e_q)
# Or equivalently: L₃⊗I = -Σ_{03} - Σ_{14} - Σ_{25}

# Let's verify by checking: L₃⊗I acting on e_0:
# e_0 = (x_L, x_R). L₃ maps x_L → -y_L, so result is -(y_L, x_R) = -e_3.
# Σ_{03} maps e_0 → -e_3 (convention: Σ_{pq} e_q = e_p, Σ_{pq} e_p = -e_q).
# Wait, need to check: Σ_{pq} = E_{pq} - E_{qp} where (E_{pq})_{rs} = δ_{pr}δ_{qs}.
# So Σ_{03} e_0 = E_{03}e_0 - E_{30}e_0 = 0 - e_3·δ_{00} = -e_3?
# No: E_{30}e_0 = δ_{00}·e_3 = e_3. And E_{03}e_0 = δ_{30}·e_0 = 0.
# So Σ_{03}e_0 = 0 - e_3 = -e_3.
# Σ_{03}e_3 = E_{03}e_3 - E_{30}e_3 = δ_{33}e_0 - 0 = e_0. ✓

# So Σ_{03} maps e_0 → -e_3 and e_3 → +e_0.
# L₃⊗I also maps e_0 → -e_3 and e_3 → +e_0.
# So L₃⊗I restricted to the (0,3) plane IS Σ_{03}.

# Therefore: L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
# Similarly: I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}

# Wait, let me verify I⊗R₃ on e_0 = (x_L, x_R):
# R₃ maps x_R → -y_R, so result is (x_L, -y_R) = -e_1.
# Σ_{01} maps e_0 → -e_1 ✓

# I⊗R₃ on e_3 = (y_L, x_R):
# R₃ maps x_R → -y_R, so result is (y_L, -y_R) = -e_4.
# Σ_{34} maps e_3 → -e_4 ✓

# I⊗R₃ on e_6 = (z_L, x_R):
# R₃ maps x_R → -y_R, so result is (z_L, -y_R) = -e_7.
# Σ_{67} maps e_6 → -e_7 ✓

print("\nL₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}")
print("I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}")

# ================================================================
# Express J_L^3 and J_R^3 in terms of SO(9) Cartan
# ================================================================

# The standard SO(9) Cartan uses H_k = Σ_{2k-2, 2k-1} for k=1,...,4:
# H₁ = Σ_{01}, H₂ = Σ_{23}, H₃ = Σ_{45}, H₄ = Σ_{67}

# Now express our generators:
# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
# I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}

# These are NOT Cartan generators (Σ_{03} mixes Cartan planes 1 and 2).
# The spinor weights (h₁,h₂,h₃,h₄) are eigenvalues of (iH₁,iH₂,iH₃,iH₄).
# To find m_L and m_R, we need the eigenvalues of iL₃⊗I and iI⊗R₃
# on each spinor weight state.

# For spinors: the generators act as Σ_{pq} = ½γ_pγ_q (in spinor rep).
# A weight state |h₁,h₂,h₃,h₄⟩ has eigenvalues:
#   iH_k |h⟩ = h_k |h⟩  (where h_k = ±½)

# For a non-Cartan generator like Σ_{03}:
# Σ_{03} = ½γ₀γ₃
# This is NOT diagonal — it mixes different weight states.
# So L₃⊗I is NOT diagonal in the spinor weight basis!

# This means the SO(4) Cartan generators mix different Spin(9) weight states.
# The branching cannot be read off directly from the weight diagram.
# We need to diagonalize the SO(4) Cartan WITHIN the spinor representation.

# KEY: Since L₃⊗I and I⊗R₃ commute, we can simultaneously
# diagonalize them in the 16-dim spinor space. Their joint eigenvalues
# give the (m_L, m_R) quantum numbers.

# For the spinor of SO(9), we work with the abstract weight states.
# Each weight state |s₁,s₂,s₃,s₄⟩ (s_k = ±½) is determined by
# the chirality choices in each 2-plane.

# The non-Cartan generators act on weight states via:
# Σ_{pq} for p,q in DIFFERENT Cartan planes mixes weight states.
# Specifically, γ_p γ_q for p ∈ plane i, q ∈ plane j flips the
# signs of h_i and h_j.

# For Σ_{03}: indices 0 is in plane 1 (pair 0,1) and 3 is in plane 2 (pair 2,3).
# γ₀γ₃ flips h₁ and h₂.
# More precisely: in the weight basis, γ_{2k} and γ_{2k+1} are
# related to the ladder operators of plane k.

# Let me use a concrete construction.
# The spinor space of SO(2n+1) is the same as SO(2n) — it's 2^n dimensional.
# For SO(8) → SO(9), the 9th gamma is the chirality of SO(8).

# Use the explicit gamma matrix construction for SO(8):
# γ₁,...,γ₈ for Cl(8), and γ₉ = γ₁γ₂...γ₈ (chirality)

# For Cl(2n), the weight states are labeled by n bits.
# The action of gamma matrices:
# γ_{2k-1} = σ_x on bit k, tensored with σ_z on bits 1,...,k-1
# γ_{2k}   = σ_y on bit k, tensored with σ_z on bits 1,...,k-1

# So for n=4 (Cl(8)):
# Bit ordering: b₁, b₂, b₃, b₄ where b_k ∈ {0, 1}
# State |b₁b₂b₃b₄⟩ has weight h_k = ½(-1)^{b_k}
# i.e., h_k = +½ if b_k=0, h_k = -½ if b_k=1

print("\n" + "=" * 60)
print("SPINOR STATES AND WEIGHT SYSTEM")
print("=" * 60)

# Label the 16 spinor states by bits (b1,b2,b3,b4)
states = []
for b1 in range(2):
    for b2 in range(2):
        for b3 in range(2):
            for b4 in range(2):
                h = tuple(0.5 * (-1)**b for b in [b1, b2, b3, b4])
                states.append({'bits': (b1,b2,b3,b4), 'weight': h})

# Action of gamma matrices on states:
# γ_{2k-1} |...b_k...⟩ = (-1)^{b_1+...+b_{k-1}} |...b̄_k...⟩ (flip bit k)
#   × factor from σ_x: always +1
#   × factor from σ_z^{k-1}: (-1)^{b_1+...+b_{k-1}}
# γ_{2k} |...b_k...⟩ = (-1)^{b_1+...+b_{k-1}} × i(-1)^{b_k} |...b̄_k...⟩
#   × factor from σ_y: i(-1)^{b_k} (since σ_y|0⟩ = i|1⟩, σ_y|1⟩ = -i|0⟩)

# The Cartan generators:
# H_k = iΣ_{2k-2,2k-1} = (i/2)γ_{2k-2}γ_{2k-1} = -(1/2)σ_z on bit k
# (Actually, the Hermitian Cartan is H_k^{herm} = iΣ_{2k-2,2k-1}.)
# Its eigenvalue on |...b_k...⟩ is h_k = ½(-1)^{b_k}.

# For a generator Σ_{pq} where p is in plane i and q is in plane j:
# It mixes the bits of planes i and j.

# Let's compute the action of L₃⊗I and I⊗R₃ on the spinor states.

# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
# I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}

# Σ_{pq} in spinor rep = ½γ_p γ_q

def gamma_action(k, bits):
    """Action of γ_k on state |bits⟩. Returns (coefficient, new_bits).
    k is 0-indexed (γ_0 through γ_8)."""
    bits = list(bits)
    if k < 8:
        # k corresponds to plane k//2 + 1, with γ_{2j} and γ_{2j+1} for plane j+1
        plane = k // 2  # 0-indexed plane
        is_second = k % 2  # 0 for γ_{2j}, 1 for γ_{2j+1}

        # Phase from σ_z on earlier planes
        phase = (-1) ** sum(bits[:plane])

        if is_second == 0:
            # γ_{2j} = σ_z^{⊗plane} ⊗ σ_x ⊗ I^{⊗rest}
            # σ_x flips bit, with coefficient +1
            coeff = phase * 1
        else:
            # γ_{2j+1} = σ_z^{⊗plane} ⊗ σ_y ⊗ I^{⊗rest}
            # σ_y|0⟩ = i|1⟩, σ_y|1⟩ = -i|0⟩
            coeff = phase * 1j * (-1)**bits[plane]

        new_bits = bits.copy()
        new_bits[plane] = 1 - bits[plane]  # flip bit
        return coeff, tuple(new_bits)
    else:
        # γ_8 = σ_z ⊗ σ_z ⊗ σ_z ⊗ σ_z = chirality
        coeff = (-1) ** sum(bits)
        return coeff, tuple(bits)

def sigma_action(p, q, bits):
    """Action of Σ_{pq} = ½γ_p γ_q on |bits⟩."""
    # First apply γ_q, then γ_p
    c1, new_bits1 = gamma_action(q, bits)
    c2, new_bits2 = gamma_action(p, new_bits1)
    return 0.5 * c1 * c2, new_bits2

# Build the 16×16 matrix for L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
def build_matrix(gen_pairs):
    """Build 16×16 matrix for a sum of Σ_{pq} generators."""
    M = np.zeros((16, 16), dtype=complex)
    bit_to_idx = {}
    for idx, s in enumerate(states):
        bit_to_idx[s['bits']] = idx

    for idx_in, s in enumerate(states):
        for p, q in gen_pairs:
            coeff, new_bits = sigma_action(p, q, s['bits'])
            idx_out = bit_to_idx[new_bits]
            M[idx_out, idx_in] += coeff
    return M

# L₃⊗I = Σ_{03} + Σ_{14} + Σ_{25}
ML = build_matrix([(0, 3), (1, 4), (2, 5)])

# I⊗R₃ = Σ_{01} + Σ_{34} + Σ_{67}
MR = build_matrix([(0, 1), (3, 4), (6, 7)])

print(f"\nL₃⊗I matrix (16×16): anti-Hermitian? {np.allclose(ML + ML.conj().T, 0)}")
print(f"I⊗R₃ matrix (16×16): anti-Hermitian? {np.allclose(MR + MR.conj().T, 0)}")
print(f"[L₃⊗I, I⊗R₃] = 0? {np.allclose(ML @ MR - MR @ ML, 0)}")

# Hermitian versions
hML = 1j * ML  # eigenvalues = m_L values
hMR = 1j * MR  # eigenvalues = m_R values

print(f"\niL₃ eigenvalues: {np.sort(np.linalg.eigvalsh(hML.real))}")
print(f"iR₃ eigenvalues: {np.sort(np.linalg.eigvalsh(hMR.real))}")

# ================================================================
# Simultaneously diagonalize to find (m_L, m_R) quantum numbers
# ================================================================

print("\n" + "=" * 60)
print("SIMULTANEOUS DIAGONALIZATION")
print("=" * 60)

# Build the SU(2) Casimirs
# Need all 3 generators of each SU(2)

# SU(2)_L generators: L₁⊗I, L₂⊗I, L₃⊗I
# In SO(3), L₁ generates rotation in (y,z) plane, L₂ in (z,x), L₃ in (x,y)
# L₁ = Σ_{12}^{(3)}: maps y→-z, z→y → in R³: indices (1,2)
# L₂ = Σ_{20}^{(3)}: maps z→-x, x→z → in R³: indices (2,0)
# L₃ = Σ_{01}^{(3)}: maps x→-y, y→x → in R³: indices (0,1)

# On R⁹ = R³⊗R³:
# L₁⊗I: Σ_{12}^{(3)} ⊗ I, which rotates pairs:
#   (y_L,a_R)↔(z_L,a_R) for a_R = x,y,z
#   In R⁹ indices: (3,6), (4,7), (5,8)
# L₂⊗I: Σ_{20}^{(3)} ⊗ I, rotating pairs:
#   (z_L,a_R)↔(x_L,a_R): (6,0), (7,1), (8,2)
# L₃⊗I: already computed: (0,3), (1,4), (2,5)

# Similarly for R:
# I⊗R₁: pairs (a_L,y_R)↔(a_L,z_R): (1,2), (4,5), (7,8)
# I⊗R₂: pairs (a_L,z_R)↔(a_L,x_R): (2,0), (5,3), (8,6)
# I⊗R₃: already computed: (0,1), (3,4), (6,7)

ML1 = build_matrix([(3, 6), (4, 7), (5, 8)])
ML2 = build_matrix([(6, 0), (7, 1), (8, 2)])
ML3 = ML

MR1 = build_matrix([(1, 2), (4, 5), (7, 8)])
MR2 = build_matrix([(2, 0), (5, 3), (8, 6)])
MR3 = MR

# Casimirs: C_L = L₁² + L₂² + L₃² (anti-Hermitian, so C_L is negative)
CL = ML1 @ ML1 + ML2 @ ML2 + ML3 @ ML3
CR = MR1 @ MR1 + MR2 @ MR2 + MR3 @ MR3

# -C_L should have eigenvalues j_L(j_L+1)
neg_CL = -CL
neg_CR = -CR

print(f"\n-C_L Hermitian? {np.allclose(neg_CL, neg_CL.conj().T)}")
print(f"-C_R Hermitian? {np.allclose(neg_CR, neg_CR.conj().T)}")

evals_CL = np.sort(np.linalg.eigvalsh(neg_CL.real))
evals_CR = np.sort(np.linalg.eigvalsh(neg_CR.real))

print(f"\nEigenvalues of -C_L = j_L(j_L+1):")
for ev in np.unique(np.round(evals_CL, 4)):
    mult = np.sum(np.abs(evals_CL - ev) < 0.01)
    if ev >= -0.01:
        j = (-1 + np.sqrt(1 + 4*ev)) / 2
        print(f"  {ev:.4f} → j_L = {j:.2f}  (multiplicity {mult})")
    else:
        print(f"  {ev:.4f} → NEGATIVE (error?)  (multiplicity {mult})")

print(f"\nEigenvalues of -C_R = j_R(j_R+1):")
for ev in np.unique(np.round(evals_CR, 4)):
    mult = np.sum(np.abs(evals_CR - ev) < 0.01)
    if ev >= -0.01:
        j = (-1 + np.sqrt(1 + 4*ev)) / 2
        print(f"  {ev:.4f} → j_R = {j:.2f}  (multiplicity {mult})")
    else:
        print(f"  {ev:.4f} → NEGATIVE (error?)  (multiplicity {mult})")

# Verify SU(2) algebras
print("\nSU(2)_L algebra check: [L₁,L₂] = L₃?")
for (a,b,c) in [(0,1,2),(1,2,0),(2,0,1)]:
    Ls = [ML1, ML2, ML3]
    comm = Ls[a] @ Ls[b] - Ls[b] @ Ls[a]
    print(f"  [L{a+1},L{b+1}] = L{c+1}? {np.allclose(comm, Ls[c])}")
    if not np.allclose(comm, Ls[c]):
        print(f"  [L{a+1},L{b+1}] = -L{c+1}? {np.allclose(comm, -Ls[c])}")

print("\n[SU(2)_L, SU(2)_R] = 0?")
cross_ok = all(
    np.allclose(Ls @ Rs - Rs @ Ls, 0)
    for Ls in [ML1, ML2, ML3]
    for Rs in [MR1, MR2, MR3]
)
print(f"  {cross_ok}")

# Simultaneously diagonalize C_L, C_R, L₃, R₃
H_comb = 1000*neg_CL.real + 100*neg_CR.real + 10*(1j*ML3).real + (1j*MR3).real
evals, evecs = np.linalg.eigh(H_comb)

print("\n" + "=" * 60)
print("BRANCHING RULE RESULT")
print("=" * 60)
print(f"\n{'#':>3} {'j_L(j_L+1)':>12} {'j_L':>6} {'m_L':>6} {'j_R(j_R+1)':>12} {'j_R':>6} {'m_R':>6}")
print("-" * 65)

multiplets = Counter()
for k in range(16):
    v = evecs[:, k:k+1]
    cl = (v.conj().T @ neg_CL @ v)[0, 0].real
    cr = (v.conj().T @ neg_CR @ v)[0, 0].real
    ml = (v.conj().T @ (1j*ML3) @ v)[0, 0].real
    mr = (v.conj().T @ (1j*MR3) @ v)[0, 0].real

    jl = (-1 + np.sqrt(max(0, 1 + 4*cl))) / 2
    jr = (-1 + np.sqrt(max(0, 1 + 4*cr))) / 2

    jl_r = round(2*jl) / 2
    jr_r = round(2*jr) / 2
    ml_r = round(2*ml) / 2
    mr_r = round(2*mr) / 2

    print(f"{k+1:>3} {cl:>12.4f} {jl_r:>6.1f} {ml_r:>6.1f} {cr:>12.4f} {jr_r:>6.1f} {mr_r:>6.1f}")
    multiplets[(jl_r, jr_r)] += 1

print(f"\n{'='*60}")
print("SUMMARY: 16 of Spin(9) → SU(2)_L × SU(2)_R")
print(f"{'='*60}")
print(f"\n{'(j_L, j_R)':>12} {'dim':>5} {'copies':>7} {'dim check':>10}")
print("-" * 45)
total = 0
for (jl, jr) in sorted(multiplets.keys()):
    count = multiplets[(jl, jr)]
    dim_rep = int((2*jl+1) * (2*jr+1))
    copies = count // dim_rep
    print(f"  ({jl:.1f}, {jr:.1f}) {dim_rep:>5}   × {copies:>3}    = {copies*dim_rep:>3}")
    total += count
print(f"\nTotal: {total} (expected 16)")

singlets = multiplets.get((0.0, 0.0), 0)
print(f"\nGAUGE SINGLETS (0,0): {singlets}")
if singlets > 0:
    print(f"  → {singlets} potential generation(s) from fiber zero modes")
else:
    print(f"  → NO singlets: fiber zero modes alone cannot give generations")
    print(f"     (consistent with Parthasarathy: rank(G) ≠ rank(K) → no L² kernel)")
