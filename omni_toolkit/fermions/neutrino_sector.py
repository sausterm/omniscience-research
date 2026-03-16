"""
Neutrino sector: seesaw mechanism and Majorana masses.

The SU(4) relation Y_ν = Y_up forces m_D(ν) = m_D(up) at M_PS.
This creates a TENSION with the observed neutrino mass scale:
  m_ν₃ = m_t² / v_R ~ 30 keV (with b/a=0, v_R=10⁹ GeV)
  Observed: m_ν₃ ~ 0.05 eV (factor of 6×10⁵ too heavy)

Resolution paths:
  1. Inverse seesaw with μ_S ~ TeV (preferred)
  2. Composite Δ_R with enhanced f
  3. NJL mechanism

STATUS:
  - SU(4) relation Y_ν = Y_up: DERIVED
  - Type-I seesaw mechanism: STANDARD
  - Normal ordering (m₃ > m₂ > m₁): DERIVED from Sp(1)
  - Specific mass values: FITTED via p-parameter or μ_S
  - TENSION between gauge (v_R ~ 10⁹) and seesaw (v_R ~ 6×10¹⁴) is OPEN
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


# Physical constants
V_EW = 246.0          # GeV, electroweak VEV
M_PLANCK = 1.22e19    # GeV


@dataclass
class NeutrinoSector:
    """Neutrino masses from seesaw mechanism in Pati-Salam.

    Parameters
    ----------
    dirac_masses : ndarray or None
        Dirac masses (m_D) for three generations in GeV.
        Default: SU(4) prediction m_D(ν) = m_up at M_PS.
    v_R : float
        Right-handed breaking scale in GeV.
    seesaw_type : str
        'type_I', 'inverse', or 'parametric'.
    mu_S : float or None
        Singlet Majorana mass for inverse seesaw (GeV).
    """

    dirac_masses: Optional[np.ndarray] = None
    v_R: float = 1.1e9
    seesaw_type: str = 'type_I'
    mu_S: Optional[float] = None

    def __post_init__(self):
        if self.dirac_masses is None:
            # SU(4) prediction: m_D(ν) = m_up at M_PS (DERIVED)
            self.dirac_masses = np.array([0.9e-3, 0.42, 90.0])  # u, c, t at M_PS (GeV)
        self.dirac_masses = np.asarray(self.dirac_masses, dtype=float)

    @property
    def majorana_masses(self) -> np.ndarray:
        """Right-handed Majorana masses M_R.

        With f = 1 (Yukawa coupling to Δ_R): M_R = f × v_R for all generations.
        """
        return np.full(3, self.v_R)

    def light_masses_type_I(self) -> np.ndarray:
        """Light neutrino masses from type-I seesaw.

        m_ν = m_D² / M_R (generation by generation, assuming diagonal).
        """
        M_R = self.majorana_masses
        return self.dirac_masses**2 / M_R

    def light_masses_inverse(self) -> np.ndarray:
        """Light neutrino masses from inverse seesaw.

        m_ν = m_D² × μ_S / M_R² (much lighter than type-I for same v_R).
        """
        if self.mu_S is None:
            raise ValueError("mu_S required for inverse seesaw")
        M_R = self.majorana_masses
        return self.dirac_masses**2 * self.mu_S / M_R**2

    def light_masses_parametric(self, p: float = 0.53) -> np.ndarray:
        """Parametric seesaw with mild hierarchy exponent.

        M_R,i ∝ m_D,i^p → m_ν,i ∝ m_D,i^{2-p}

        The exponent p = 0.53 is FITTED to match oscillation data.
        """
        m_D = self.dirac_masses
        m_D_max = m_D[-1]
        M_R_max = self.v_R

        # M_R,i = M_R_max × (m_D,i / m_D_max)^p
        M_R = M_R_max * (m_D / m_D_max)**p
        return m_D**2 / M_R

    def light_masses(self) -> np.ndarray:
        """Compute light neutrino masses based on seesaw_type."""
        if self.seesaw_type == 'type_I':
            return self.light_masses_type_I()
        elif self.seesaw_type == 'inverse':
            return self.light_masses_inverse()
        elif self.seesaw_type == 'parametric':
            return self.light_masses_parametric()
        else:
            raise ValueError(f"Unknown seesaw type: {self.seesaw_type}")

    def mass_squared_differences(self) -> dict:
        """Compute Δm² and compare to oscillation data.

        Observed (NuFIT 5.2, NO):
          Δm²₂₁ = 7.42 × 10⁻⁵ eV²
          Δm²₃₁ = 2.515 × 10⁻³ eV²
        """
        m = self.light_masses()  # in GeV
        m_eV = m * 1e9  # Convert to eV

        dm21_sq = m_eV[1]**2 - m_eV[0]**2
        dm31_sq = m_eV[2]**2 - m_eV[0]**2

        dm21_sq_obs = 7.42e-5   # eV²
        dm31_sq_obs = 2.515e-3  # eV²

        return {
            'masses_eV': m_eV,
            'dm21_sq': dm21_sq,
            'dm31_sq': dm31_sq,
            'dm21_sq_obs': dm21_sq_obs,
            'dm31_sq_obs': dm31_sq_obs,
            'ratio': dm21_sq / dm31_sq if abs(dm31_sq) > 1e-30 else float('inf'),
            'ratio_obs': dm21_sq_obs / dm31_sq_obs,
            'ordering': 'normal' if m_eV[2] > m_eV[1] > m_eV[0] else 'inverted/other',
        }

    def tension_diagnostic(self) -> dict:
        """Diagnose the neutrino mass tension.

        With b/a = 0 (symmetric point), SU(4) forces m_D(ν₃) = m_t ≈ 90 GeV.
        Type-I seesaw with v_R = 1.1×10⁹ gives m_ν₃ ~ 7 keV (too heavy).
        The required v_R for correct m_ν₃ ≈ 0.05 eV is ~ 1.6×10¹⁴ GeV.
        """
        m_type_I = self.light_masses_type_I()
        m_eV = m_type_I * 1e9

        m_nu3_obs = 0.05  # eV
        v_R_needed = self.dirac_masses[2]**2 / (m_nu3_obs * 1e-9)

        return {
            'type_I_m_nu3_eV': m_eV[2],
            'observed_m_nu3_eV': m_nu3_obs,
            'ratio': m_eV[2] / m_nu3_obs,
            'v_R_used': self.v_R,
            'v_R_needed_for_correct_mass': v_R_needed,
            'log10_tension': np.log10(m_eV[2] / m_nu3_obs),
            'status': 'TENSION' if m_eV[2] / m_nu3_obs > 10 else 'OK',
        }

    def inverse_seesaw_mu_S(self, alpha_R: float = 0.02) -> float:
        """Two-loop estimate of μ_S from geometry.

        μ_S ~ (α_R / 4π)² × v_R

        For α_R ≈ 0.02, v_R = 10⁹: μ_S ~ 250 GeV.
        """
        return (alpha_R / (4 * np.pi))**2 * self.v_R

    def effective_mass_0nubb(self) -> float:
        """Effective Majorana mass for 0νββ decay.

        |m_ee| = |Σ_i U²_{ei} m_i|
        Using TBM mixing: U_e1 = 2/√6, U_e2 = 1/√3, U_e3 ≈ 0.
        """
        m = self.light_masses() * 1e9  # eV
        # TBM mixing
        U_e = np.array([2.0/np.sqrt(6), 1.0/np.sqrt(3), 0.0])
        return abs(np.sum(U_e**2 * m))

    def summary(self) -> dict:
        """Full neutrino sector summary."""
        tension = self.tension_diagnostic()
        dm = self.mass_squared_differences()
        m_ee = self.effective_mass_0nubb()

        return {
            'seesaw_type': self.seesaw_type,
            'dirac_masses_GeV': self.dirac_masses.tolist(),
            'v_R_GeV': self.v_R,
            'light_masses_eV': (self.light_masses() * 1e9).tolist(),
            'mass_ordering': dm['ordering'],
            'dm21_sq': dm['dm21_sq'],
            'dm31_sq': dm['dm31_sq'],
            'm_ee_eV': m_ee,
            'tension_status': tension['status'],
            'derivation_notes': {
                'SU4_relation': 'DERIVED (m_D(nu) = m_up)',
                'seesaw': 'STANDARD mechanism',
                'mass_values': 'FITTED (v_R or mu_S parameter)',
                'ordering': 'DERIVED (Sp(1) → normal)',
            },
        }
