"""
Fermion mass spectrum from Froggatt-Nielsen mechanism.

Mass hierarchy: m_i/m_3 ~ ε^{n_i} where n_i are FN charges
and ε = 1/√20 from fibre geometry.

CRITICAL HONESTY NOTES:
  - ε = 1/√20 is DERIVED from geometry (dim_fibre = 10)
  - The FN charges (n₁, n₂, n₃) for each sector are FITTED to data
  - Different sectors (up, down, lepton) have DIFFERENT effective ε-powers
  - This CANNOT be derived from Pati-Salam + Sp(1) alone
  - Sector splitting requires SU(5) embedding or additional physics

STATUS:
  - Universal ε: DERIVED
  - 1:ε²:ε⁴ hierarchy pattern: DERIVED from Sp(1) breaking
  - Sector-specific charges: FITTED
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, List


# Observed fermion masses at M_Z (GeV, PDG 2024)
FERMION_MASSES_MZ = {
    'up': [0.00216, 1.27, 172.69],       # u, c, t
    'down': [0.00467, 0.0934, 4.18],     # d, s, b
    'lepton': [0.000511, 0.1057, 1.777], # e, μ, τ
}


@dataclass
class FermionSpectrum:
    """Fermion mass hierarchy from Froggatt-Nielsen mechanism.

    Parameters
    ----------
    epsilon : float
        Expansion parameter. Default 1/√20.
    fn_charges : dict or None
        FN charges {sector: [n₁, n₂, n₃]} for each sector.
        Default: fitted values from TOE analysis.
    """

    epsilon: float = None
    fn_charges: Optional[Dict[str, List[float]]] = None

    def __post_init__(self):
        if self.epsilon is None:
            self.epsilon = 1.0 / np.sqrt(20.0)
        if self.fn_charges is None:
            # Default fitted charges (from quark_mass_analysis.py)
            self.fn_charges = {
                'up': [4.0, 1.5, 0.0],      # FITTED
                'down': [2.5, 1.0, 0.0],     # FITTED
                'lepton': [3.0, 1.0, 0.0],   # FITTED
            }

    def mass_ratios(self, sector: str) -> np.ndarray:
        """Compute mass ratios m_i/m_3 for a given sector.

        Parameters
        ----------
        sector : str
            One of 'up', 'down', 'lepton'.

        Returns shape (3,) array of ratios.
        """
        charges = np.array(self.fn_charges[sector])
        return self.epsilon ** charges

    def masses_from_scale(self, sector: str, m3: float) -> np.ndarray:
        """Compute masses given the heaviest generation mass.

        Parameters
        ----------
        sector : str
            Sector name.
        m3 : float
            Mass of heaviest generation in GeV.
        """
        ratios = self.mass_ratios(sector)
        return ratios * m3

    def effective_epsilon(self, sector: str) -> float:
        """Effective ε for adjacent-generation ratio m₂/m₃ in given sector.

        ε_eff = (m₂/m₃)^{1/(n₂-n₃)}
        """
        charges = self.fn_charges[sector]
        delta_n = charges[1] - charges[2]
        if abs(delta_n) < 1e-10:
            return 1.0
        obs = FERMION_MASSES_MZ[sector]
        ratio = obs[1] / obs[2]
        return ratio ** (1.0 / delta_n)

    def comparison_table(self) -> dict:
        """Compare predictions to observed masses for all sectors.

        Returns dict with sector → {predicted_ratios, observed_ratios, errors}.
        """
        results = {}
        for sector in ['up', 'down', 'lepton']:
            obs = np.array(FERMION_MASSES_MZ[sector])
            obs_ratios = obs / obs[2]

            pred_ratios = self.mass_ratios(sector)

            # Compute predicted masses assuming m₃ is input
            pred_masses = pred_ratios * obs[2]

            errors = np.abs(pred_masses - obs) / obs * 100

            results[sector] = {
                'observed_masses': obs,
                'predicted_ratios': pred_ratios,
                'observed_ratios': obs_ratios,
                'predicted_masses': pred_masses,
                'errors_pct': errors,
                'fn_charges': self.fn_charges[sector],
                'derivation_status': 'FITTED (charges sector-specific)',
            }

        return results

    def hierarchy_pattern(self) -> dict:
        """Verify the universal 1:ε²:ε⁴ hierarchy from Sp(1) breaking.

        The DERIVED prediction is that ALL sectors should have the pattern
        1 : ε² : ε⁴ with ε = 1/√20. In reality, different sectors
        deviate from this due to sector-specific physics.
        """
        eps = self.epsilon

        # Universal Sp(1) prediction
        universal_ratios = np.array([eps**4, eps**2, 1.0])

        results = {}
        for sector in ['up', 'down', 'lepton']:
            obs = np.array(FERMION_MASSES_MZ[sector])
            obs_ratios = obs / obs[2]

            # Deviation from universal prediction
            log_deviation = np.log10(obs_ratios / universal_ratios)

            results[sector] = {
                'universal_prediction': universal_ratios,
                'observed_ratios': obs_ratios,
                'log10_deviation': log_deviation,
            }

        return {
            'epsilon': eps,
            'universal_pattern': '1 : ε² : ε⁴',
            'sectors': results,
            'note': ('Universal pattern is DERIVED from Sp(1) breaking. '
                     'Sector deviations require FITTED FN charges.'),
        }

    def sp1_breaking_charges(self) -> dict:
        """FN charges from one-step Sp(1) → U(1) breaking.

        With breaking along K-direction:
          q₃ = 0 (heaviest, aligned with VEV)
          q₂ = q₁ = 2 (degenerate, perpendicular to VEV)

        This gives a DEGENERATE 1st and 2nd generation.
        The degeneracy is lifted by two-step breaking Sp(1) → U(1) → {1}.
        """
        return {
            'one_step_charges': [2, 2, 0],
            'note': 'One-step gives q₁ = q₂ (degenerate). Two-step needed for 3 distinct.',
            'two_step_charges': [3, 1, 0],
            'two_step_note': 'Sequential breaking: Sp(1)→U(1)→{1}. Gives m₁:m₂:m₃ = ε⁶:ε²:1.',
            'derivation_status': 'DERIVED (pattern), FITTED (exact charges per sector)',
        }
