"""
Anyonic Braiding and Topological Gates
=======================================

Implements braid group representations for anyonic quantum computing:
  - Braid group generators satisfying Yang-Baxter equation
  - Fibonacci anyons (universal for quantum computation)
  - Ising anyons (Majorana-based)
  - Gate compilation via braid words

The connection to the Metric Bundle Programme:
  - Instanton action S = 8pi^2/g^2 gives braiding phase theta = 2pi*S mod 2pi
  - The pi_3(GL+(4)/SO(3,1)) = Z topological charge IS the anyon number
  - Chern-Simons level k determines the anyon model

References:
  - Nayak et al., Rev. Mod. Phys. 80, 1083 (2008)
  - Preskill, lecture notes on topological quantum computation
  - Freedman, Kitaev, Wang, Commun. Math. Phys. 227, 587 (2002)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict


# ============================================================
# Braid Group
# ============================================================

@dataclass
class BraidGroup:
    """Braid group B_n on n strands.

    Generators sigma_1, ..., sigma_{n-1} satisfy:
    - Yang-Baxter: sigma_i sigma_{i+1} sigma_i = sigma_{i+1} sigma_i sigma_{i+1}
    - Far commutativity: sigma_i sigma_j = sigma_j sigma_i for |i-j| >= 2
    """
    n_strands: int

    @property
    def n_generators(self) -> int:
        return self.n_strands - 1

    def yang_baxter_check(self, representation) -> bool:
        """Verify Yang-Baxter equation for a representation.

        Parameters
        ----------
        representation : callable
            Maps generator index i -> matrix sigma_i.

        Returns
        -------
        bool
            True if sigma_i sigma_{i+1} sigma_i = sigma_{i+1} sigma_i sigma_{i+1}
            for all valid i.
        """
        for i in range(self.n_generators - 1):
            si = representation(i)
            si1 = representation(i + 1)
            lhs = si @ si1 @ si
            rhs = si1 @ si @ si1
            if not np.allclose(lhs, rhs, atol=1e-10):
                return False
        return True

    def far_commutativity_check(self, representation) -> bool:
        """Verify far commutativity for a representation."""
        for i in range(self.n_generators):
            for j in range(i + 2, self.n_generators):
                si = representation(i)
                sj = representation(j)
                if not np.allclose(si @ sj, sj @ si, atol=1e-10):
                    return False
        return True


@dataclass
class BraidWord:
    """A word in the braid group (sequence of generator applications).

    Each element is (generator_index, power) where power can be negative
    for inverse generators.
    """
    generators: List[Tuple[int, int]]
    n_strands: int

    @property
    def length(self) -> int:
        """Total number of crossings."""
        return sum(abs(p) for _, p in self.generators)

    def evaluate(self, representation) -> np.ndarray:
        """Evaluate the braid word in a given representation.

        Parameters
        ----------
        representation : callable
            Maps generator index i -> matrix sigma_i.
        """
        result = None
        for idx, power in self.generators:
            mat = representation(idx)
            if power < 0:
                mat = np.linalg.inv(mat)
                power = -power
            for _ in range(power):
                if result is None:
                    result = mat.copy()
                else:
                    result = result @ mat
        if result is None:
            # Empty braid = identity
            dim = representation(0).shape[0]
            return np.eye(dim, dtype=complex)
        return result

    def __repr__(self) -> str:
        parts = []
        for idx, power in self.generators:
            if power == 1:
                parts.append(f"s{idx+1}")
            elif power == -1:
                parts.append(f"s{idx+1}^-1")
            else:
                parts.append(f"s{idx+1}^{power}")
        return " ".join(parts)


# ============================================================
# Anyon Models
# ============================================================

@dataclass
class AnyonModel:
    """Abstract anyon model with fusion rules and braiding data.

    An anyon model is specified by:
    - Particle types (labels)
    - Fusion rules: a x b = sum_c N^c_{ab} c
    - F-matrices (associativity/recoupling)
    - R-matrices (braiding)
    """
    name: str
    particle_types: List[str]
    fusion_rules: Dict[Tuple[str, str], List[str]]
    r_matrices: Dict[Tuple[str, str], complex]
    f_matrices: Optional[Dict] = field(default=None, repr=False)
    is_universal: bool = False

    def fusion_space_dim(self, particles: List[str]) -> int:
        """Dimension of the fusion space for a list of particles.

        This is the number of ways the particles can fuse to vacuum.
        For Fibonacci anyons with n tau particles, this is F_{n+1}
        (the (n+1)-th Fibonacci number).
        """
        if len(particles) <= 1:
            return 1

        # Build fusion tree iteratively
        outcomes = {particles[0]: 1}
        for p in particles[1:]:
            new_outcomes = {}
            for existing, count in outcomes.items():
                if (existing, p) in self.fusion_rules:
                    for product in self.fusion_rules[(existing, p)]:
                        new_outcomes[product] = new_outcomes.get(product, 0) + count
            outcomes = new_outcomes

        # Count paths that end at vacuum
        vacuum = self.particle_types[0]  # Convention: first type is vacuum
        return outcomes.get(vacuum, 0)

    def topological_spin(self, particle: str) -> complex:
        """Topological spin theta_a = R^{aa}_c for self-braiding."""
        if (particle, particle) in self.r_matrices:
            return self.r_matrices[(particle, particle)]
        return 1.0

    def quantum_dimension(self, particle: str) -> float:
        """Quantum dimension d_a from fusion rules.

        For Fibonacci: d_tau = phi = (1 + sqrt(5))/2
        For Ising: d_sigma = sqrt(2)
        """
        if particle == self.particle_types[0]:  # vacuum
            return 1.0

        # Compute from fusion matrix eigenvalue
        types = self.particle_types
        n = len(types)
        N = np.zeros((n, n))
        for i, a in enumerate(types):
            if (particle, a) in self.fusion_rules:
                for c in self.fusion_rules[(particle, a)]:
                    j = types.index(c)
                    N[i, j] += 1

        if np.all(N == 0):
            return 1.0
        eigenvalues = np.linalg.eigvals(N)
        return float(np.max(np.abs(eigenvalues)))

    def total_quantum_dimension(self) -> float:
        """Total quantum dimension D = sqrt(sum d_a^2)."""
        d_sq_sum = sum(self.quantum_dimension(p) ** 2 for p in self.particle_types)
        return np.sqrt(d_sq_sum)


def fibonacci_anyons() -> AnyonModel:
    """Fibonacci anyon model (SU(2) Chern-Simons at level k=3).

    Particle types: {1 (vacuum), tau}
    Fusion rules: tau x tau = 1 + tau
    This model is UNIVERSAL for quantum computation.

    The braiding matrix for two tau particles in the 2D fusion space is:
    R = diag(e^{4pi*i/5}, e^{-3pi*i/5})
    """
    phi = (1 + np.sqrt(5)) / 2  # golden ratio

    # R-matrices (braiding phases)
    r_matrices = {
        ('1', '1'): 1.0,
        ('1', 'tau'): 1.0,
        ('tau', '1'): 1.0,
        ('tau', 'tau'): np.exp(4j * np.pi / 5),  # R^{tau,tau}_1
    }

    # F-matrix for (tau, tau, tau) -> tau recoupling
    # F^{tau,tau,tau}_{tau} is a 2x2 unitary
    f_tau = np.array([
        [1 / phi, np.sqrt(1 / phi)],
        [np.sqrt(1 / phi), -1 / phi],
    ], dtype=complex)

    f_matrices = {
        ('tau', 'tau', 'tau', 'tau'): f_tau,
    }

    return AnyonModel(
        name="Fibonacci",
        particle_types=['1', 'tau'],
        fusion_rules={
            ('1', '1'): ['1'],
            ('1', 'tau'): ['tau'],
            ('tau', '1'): ['tau'],
            ('tau', 'tau'): ['1', 'tau'],
        },
        r_matrices=r_matrices,
        f_matrices=f_matrices,
        is_universal=True,
    )


def ising_anyons() -> AnyonModel:
    """Ising anyon model (SU(2) Chern-Simons at level k=2).

    Particle types: {1 (vacuum), psi (fermion), sigma (Majorana)}
    Fusion rules:
        sigma x sigma = 1 + psi
        psi x psi = 1
        sigma x psi = sigma
    NOT universal alone (generates Clifford group only).
    """
    r_matrices = {
        ('1', '1'): 1.0,
        ('1', 'psi'): 1.0,
        ('1', 'sigma'): 1.0,
        ('psi', '1'): 1.0,
        ('psi', 'psi'): -1.0,  # fermion exchange
        ('psi', 'sigma'): -1j,
        ('sigma', '1'): 1.0,
        ('sigma', 'psi'): -1j,
        ('sigma', 'sigma'): np.exp(-1j * np.pi / 8),
    }

    return AnyonModel(
        name="Ising",
        particle_types=['1', 'psi', 'sigma'],
        fusion_rules={
            ('1', '1'): ['1'],
            ('1', 'psi'): ['psi'],
            ('1', 'sigma'): ['sigma'],
            ('psi', '1'): ['psi'],
            ('psi', 'psi'): ['1'],
            ('psi', 'sigma'): ['sigma'],
            ('sigma', '1'): ['sigma'],
            ('sigma', 'psi'): ['sigma'],
            ('sigma', 'sigma'): ['1', 'psi'],
        },
        r_matrices=r_matrices,
        is_universal=False,
    )


# ============================================================
# Braiding representations
# ============================================================

def fibonacci_braid_matrices(n_anyons: int) -> callable:
    """Braiding representation for n Fibonacci anyons.

    Returns a callable that maps generator index i to the
    braiding matrix sigma_i acting on the fusion Hilbert space.

    For n anyons, the fusion space dimension is F_{n-1} (Fibonacci number).
    The braid generators act as unitary matrices on this space.

    Parameters
    ----------
    n_anyons : int
        Number of tau anyons (>= 3 for non-trivial braiding).

    Returns
    -------
    callable
        representation(i) -> np.ndarray for generator sigma_i.
    """
    if n_anyons < 3:
        raise ValueError(f"Need >= 3 anyons for non-trivial braiding, got {n_anyons}")

    phi = (1 + np.sqrt(5)) / 2
    tau = 1 / phi

    # R-matrix eigenvalues
    r1 = np.exp(4j * np.pi / 5)   # fuse to 1
    r_tau = np.exp(-3j * np.pi / 5)  # fuse to tau

    # F-matrix
    F = np.array([
        [tau, np.sqrt(tau)],
        [np.sqrt(tau), -tau],
    ], dtype=complex)

    def _fib(n):
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return a

    dim = _fib(n_anyons - 1)

    def representation(i):
        """Braiding matrix for generator sigma_{i+1}."""
        if i < 0 or i >= n_anyons - 1:
            raise ValueError(f"Generator index {i} out of range for {n_anyons} anyons")

        if dim == 1:
            return np.array([[r1]], dtype=complex)

        if dim == 2:
            # Two-dimensional representation
            # sigma_1 acts as R in the standard basis
            # sigma_2 acts as F^{-1} R F
            R = np.diag([r1, r_tau])
            if i == 0:
                return R
            else:
                return np.linalg.inv(F) @ R @ F

        # For larger spaces, build block-diagonal structure
        # This is a simplified version using the recursive structure
        mat = np.eye(dim, dtype=complex)

        # The braiding matrix acts non-trivially on a 2x2 block
        # determined by which pair of anyons is being exchanged
        block_start = min(i, dim - 2)
        R = np.diag([r1, r_tau])

        if i % 2 == 0:
            mat[block_start:block_start + 2, block_start:block_start + 2] = R
        else:
            block = np.linalg.inv(F) @ R @ F
            mat[block_start:block_start + 2, block_start:block_start + 2] = block

        return mat

    return representation


def ising_braid_matrices(n_anyons: int) -> callable:
    """Braiding representation for n Ising (Majorana) anyons.

    For 2n Majorana modes, the fusion space is 2^{n-1} dimensional.
    Braiding generates the Clifford group on this space.

    Parameters
    ----------
    n_anyons : int
        Number of sigma anyons (must be even, >= 4).
    """
    if n_anyons < 4 or n_anyons % 2 != 0:
        raise ValueError(f"Need even number >= 4 of Ising anyons, got {n_anyons}")

    n_pairs = n_anyons // 2
    dim = 2 ** (n_pairs - 1)

    def representation(i):
        if i < 0 or i >= n_anyons - 1:
            raise ValueError(f"Generator index {i} out of range for {n_anyons} anyons")

        # Braiding adjacent Majorana modes
        # sigma_i exchanges anyons i and i+1
        # For intra-pair braiding: phase gate
        # For inter-pair braiding: entangling gate
        mat = np.eye(dim, dtype=complex)

        if dim == 1:
            mat[0, 0] = np.exp(-1j * np.pi / 8)
            return mat

        # Simplified: braiding within a pair gives a phase
        pair_i = i // 2
        if i % 2 == 0:
            # Intra-pair braiding: exp(-i pi/8) on the relevant qubit
            phase = np.exp(-1j * np.pi / 8)
            if pair_i < dim:
                # Acts as Z^{1/4} on the pair's qubit
                half = dim // 2
                if half > 0:
                    mat[:half, :half] *= phase
                    mat[half:, half:] *= np.conj(phase)
        else:
            # Inter-pair braiding: entangling gate between adjacent pairs
            half = dim // 2
            if half >= 1:
                # Acts like a controlled-phase
                for j in range(half):
                    mat[j, j] = np.cos(np.pi / 8)
                    if j + half < dim:
                        mat[j, j + half] = -1j * np.sin(np.pi / 8)
                        mat[j + half, j] = -1j * np.sin(np.pi / 8)
                        mat[j + half, j + half] = np.cos(np.pi / 8)

        return mat

    return representation


# ============================================================
# Braiding from instanton action
# ============================================================

def braiding_phase_from_instanton(instanton_action: float) -> float:
    """Compute braiding phase from instanton action.

    The topological action gives the braiding phase:
        theta = 2*pi * S (mod 2*pi)

    For the GL+(4)/SO(3,1) fibre bundle:
        S = 8*pi^2 / g_PS^2 = 290.3

    Parameters
    ----------
    instanton_action : float
        Instanton action S (dimensionless).

    Returns
    -------
    float
        Braiding phase in [0, 2*pi).
    """
    return (2 * np.pi * instanton_action) % (2 * np.pi)


def braiding_phase_from_chern_simons(k: int, charge: int = 1) -> float:
    """Compute braiding phase from Chern-Simons level.

    For U(1) at level k: theta = pi * charge^2 / k
    For SU(2) at level k: theta depends on the representation.

    Parameters
    ----------
    k : int
        Chern-Simons level.
    charge : int
        Topological charge of the anyon.
    """
    return np.pi * charge ** 2 / k
