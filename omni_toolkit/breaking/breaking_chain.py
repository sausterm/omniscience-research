"""
Multi-step symmetry breaking chains.

The Pati-Salam breaking chain:
  G_PS = SU(4) × SU(2)_L × SU(2)_R
    → SU(3) × SU(2)_L × SU(2)_R × U(1)_{B-L}  at M_C (classical, from CP³)
    → SU(3) × SU(2)_L × U(1)_Y                   at M_R (MECHANISM OPEN)
    → SU(3) × U(1)_EM                             at M_Z (radiative)

STATUS:
  - SU(4) → SU(3) × U(1)_{B-L}: DERIVED from CP³ curvature
  - SU(2)_R → U(1)_Y: MECHANISM OPEN (neither CW nor instantons work alone)
  - EW → U(1)_EM: standard radiative breaking
"""

import numpy as np
import math
from dataclasses import dataclass, field
from typing import Optional, List, Callable


@dataclass
class BreakingStep:
    """A single step in a symmetry breaking chain.

    Parameters
    ----------
    name : str
        Description of the breaking (e.g., "SU(4) → SU(3) × U(1)_{B-L}").
    scale : float
        Breaking scale in GeV.
    mechanism : str
        How the breaking occurs ('classical', 'radiative', 'open', etc.).
    residual_group : str
        The unbroken group after this step.
    goldstone_count : int
        Number of Goldstone bosons eaten.
    derivation_status : str
        'DERIVED', 'FITTED', 'OPEN', etc.
    """

    name: str
    scale: float
    mechanism: str
    residual_group: str
    goldstone_count: int = 0
    derivation_status: str = 'DERIVED'


@dataclass
class BreakingChain:
    """Multi-step symmetry breaking chain with scale hierarchy.

    Parameters
    ----------
    initial_group : str
        The unified group at the highest scale.
    steps : list of BreakingStep
        Ordered list of breaking steps (highest scale first).
    """

    initial_group: str = "SU(4) x SU(2)_L x SU(2)_R"
    steps: List[BreakingStep] = field(default_factory=list)

    @classmethod
    def pati_salam_chain(cls, M_C: float = 4.5e16, M_R: float = 1.1e9,
                          M_Z: float = 91.19) -> 'BreakingChain':
        """Standard Pati-Salam breaking chain.

        Parameters
        ----------
        M_C : float
            Color unification scale (GeV).
        M_R : float
            Left-right breaking scale (GeV).
        M_Z : float
            Electroweak scale (GeV).
        """
        steps = [
            BreakingStep(
                name="SU(4) → SU(3)_c × U(1)_{B-L}",
                scale=M_C,
                mechanism="classical (CP³ curvature potential)",
                residual_group="SU(3) x SU(2)_L x SU(2)_R x U(1)_{B-L}",
                goldstone_count=9,
                derivation_status="DERIVED",
            ),
            BreakingStep(
                name="SU(2)_R × U(1)_{B-L} → U(1)_Y",
                scale=M_R,
                mechanism="OPEN (CW + instantons insufficient alone)",
                residual_group="SU(3) x SU(2)_L x U(1)_Y",
                goldstone_count=3,
                derivation_status="OPEN",
            ),
            BreakingStep(
                name="SU(2)_L × U(1)_Y → U(1)_EM",
                scale=M_Z,
                mechanism="radiative (standard EW)",
                residual_group="SU(3) x U(1)_EM",
                goldstone_count=3,
                derivation_status="STANDARD",
            ),
        ]

        return cls(
            initial_group="SU(4) x SU(2)_L x SU(2)_R",
            steps=steps,
        )

    def scale_hierarchy(self) -> dict:
        """Compute scale ratios and hierarchy."""
        if len(self.steps) < 2:
            return {}

        results = {}
        for i in range(len(self.steps) - 1):
            s1 = self.steps[i]
            s2 = self.steps[i + 1]
            ratio = s1.scale / s2.scale
            results[f'{s1.name} / {s2.name}'] = {
                'scale_1': s1.scale,
                'scale_2': s2.scale,
                'ratio': ratio,
                'log10_ratio': math.log10(ratio) if ratio > 0 else float('inf'),
            }

        return results

    def total_goldstones(self) -> int:
        """Total Goldstone bosons eaten across all steps."""
        return sum(s.goldstone_count for s in self.steps)

    def instanton_action(self, g_PS: float = 0.52) -> dict:
        """Instanton action on the fibre GL+(4)/SO(3,1).

        π₃(GL+(4)/SO(3,1)) = Z, generator wraps SU(2)_R relative to SU(2)_L.
        S_inst = 8π²/g²_PS ≈ 290.3 → exp(-S) ~ 10⁻¹²⁶ (catastrophically small).

        STATUS: DERIVED, but too small to generate M_R ~ 10⁹ by ~118 orders.
        """
        S = 8 * np.pi**2 / g_PS**2
        exp_S = np.exp(-S)
        N_eff = 1.0  # Dynkin index of SU(2)_R in 10 of SO(6,4)

        return {
            'pi3': 'Z',
            'instanton_action': S,
            'exp_minus_S': exp_S,
            'log10_exp_minus_S': -S / np.log(10),
            'N_eff': N_eff,
            'note': ('N_eff ≈ 1 (fibre d.o.f. enter prefactor, NOT exponent). '
                     'SU(2)_R is NOT asymptotically free (b = -5/3).'),
            'status': 'TOO SUPPRESSED (~118 orders below needed scale)',
        }

    def coleman_weinberg_hierarchy(self, g_PS: float = 0.52,
                                     M_C: float = 4.5e16) -> dict:
        """CW analysis for SU(2)_R breaking.

        Perturbative CW gives v_R ≈ 0.73 M_C — NO hierarchy.
        λ_Δ starts at 0 (L-R symmetric), immediately positive from gauge loops.

        STATUS: DERIVED, but gives no hierarchy.
        """
        v_R_CW = 0.73 * M_C
        ratio = v_R_CW / M_C

        return {
            'v_R_CW': v_R_CW,
            'v_R_over_M_C': ratio,
            'hierarchy_generated': ratio < 0.1,
            'note': ('CW gives v_R ~ M_C (no hierarchy). '
                     'Fermion loops (f_nu ~ 0 from b/a=0) cannot help.'),
            'status': 'NO HIERARCHY',
        }

    def scalar_content(self) -> dict:
        """Scalar representations from fibre geometry.

        From fibre tangent space:
          V⁻ (4D): (1, 2, 2)₀ — Higgs bidoublet
          V⁺ (6D): (3, 1, 1) ⊕ (3̄, 1, 1) — color triplets

        Missing: Δ_R ~ (1, 1, 3) not in tangent space.
        Composite: Δ_R from Λ²(V⁻) = (1,3,1) ⊕ (1,1,3).
        """
        return {
            'from_V_minus': [
                {'rep': '(1, 2, 2)_0', 'name': 'Higgs bidoublet Φ',
                 'dof': 4, 'status': 'DERIVED'},
            ],
            'from_V_plus': [
                {'rep': '(3, 1, 1) + (3̄, 1, 1)', 'name': 'Color triplet σ',
                 'dof': 6, 'status': 'DERIVED'},
            ],
            'composite': [
                {'rep': '(1, 3, 1)', 'name': 'Δ_L from Λ²(V⁻)',
                 'dof': 3, 'status': 'COMPOSITE'},
                {'rep': '(1, 1, 3)', 'name': 'Δ_R from Λ²(V⁻)',
                 'dof': 3, 'status': 'COMPOSITE'},
            ],
            'note': 'Δ_R is NOT in the fibre tangent space; arises from Λ²(V⁻).',
        }

    def summary(self) -> dict:
        """Full breaking chain summary."""
        return {
            'initial_group': self.initial_group,
            'steps': [
                {
                    'name': s.name,
                    'scale_GeV': s.scale,
                    'log10_scale': math.log10(s.scale) if s.scale > 0 else float('-inf'),
                    'mechanism': s.mechanism,
                    'residual': s.residual_group,
                    'goldstones': s.goldstone_count,
                    'status': s.derivation_status,
                }
                for s in self.steps
            ],
            'total_goldstones': self.total_goldstones(),
            'hierarchy': self.scale_hierarchy(),
        }
