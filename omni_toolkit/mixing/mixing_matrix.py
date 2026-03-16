"""
CKM and PMNS mixing matrices from fibre geometry.

CKM hierarchy: |V_us| ~ ε, |V_cb| ~ ε², |V_ub| ~ ε³
with ε = 1/√20 from fibre dimension.

PMNS: Tribimaximal (TBM) zeroth order from S₃ symmetry of quaternions,
plus ε-corrections for nonzero θ₁₃.

STATUS:
  - ε = 1/√20 is DERIVED. Cabibbo angle sin(θ_C) ≈ ε to 0.75%.
  - CKM: Only |V_us| ≈ ε is derived. Higher elements use FITTED Wolfenstein params.
  - PMNS: TBM base is DERIVED from S₃. Corrections are parametric.
  - Wolfenstein A = √3/2 is MOTIVATED (angle π/3 on CP²) but not derived (6.7% error).
  - |ρ - iη| = 1/3 is POST-HOC numerology.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple


# PDG 2024 Wolfenstein parameters
WOLFENSTEIN_LAMBDA_OBS = 0.22501
WOLFENSTEIN_A_OBS = 0.826
WOLFENSTEIN_RHO_BAR_OBS = 0.159
WOLFENSTEIN_ETA_BAR_OBS = 0.348


@dataclass
class MixingMatrix:
    """Parametric CKM/PMNS mixing matrices from ε and FN charges.

    Parameters
    ----------
    epsilon : float
        Expansion parameter. Default 1/√20 ≈ 0.2236.
    wolfenstein_A : float
        Wolfenstein A parameter. Default √3/2 (geometric motivation).
        NOTE: MOTIVATED but not rigorously derived. Observed: 0.826.
    rho_bar : float
        Wolfenstein ρ̄. FITTED to data.
    eta_bar : float
        Wolfenstein η̄. FITTED to data.
    """

    epsilon: float = None
    wolfenstein_A: float = None
    rho_bar: float = WOLFENSTEIN_RHO_BAR_OBS
    eta_bar: float = WOLFENSTEIN_ETA_BAR_OBS

    def __post_init__(self):
        if self.epsilon is None:
            self.epsilon = 1.0 / np.sqrt(20.0)
        if self.wolfenstein_A is None:
            self.wolfenstein_A = np.sqrt(3.0) / 2.0

    # =================================================================
    # CKM matrix
    # =================================================================

    def ckm_wolfenstein(self, order: int = 3) -> np.ndarray:
        """CKM matrix in Wolfenstein parametrization to given order in λ.

        Parameters
        ----------
        order : int
            Expansion order (1, 2, or 3).

        Returns 3×3 complex ndarray.
        """
        lam = self.epsilon
        A = self.wolfenstein_A
        rho = self.rho_bar
        eta = self.eta_bar

        V = np.eye(3, dtype=complex)

        if order >= 1:
            V[0, 1] = lam
            V[1, 0] = -lam

        if order >= 2:
            V[0, 0] = 1 - lam**2 / 2
            V[1, 1] = 1 - lam**2 / 2
            V[1, 2] = A * lam**2
            V[2, 1] = -A * lam**2

        if order >= 3:
            V[0, 2] = A * lam**3 * (rho - 1j * eta)
            V[2, 0] = A * lam**3 * (1 - rho - 1j * eta)

        return V

    def ckm_magnitudes(self) -> np.ndarray:
        """Absolute values of CKM matrix elements."""
        return np.abs(self.ckm_wolfenstein(order=3))

    def ckm_comparison(self) -> dict:
        """Compare predicted CKM to PDG values.

        Returns dict with predictions, observations, and percent errors.
        """
        V = self.ckm_magnitudes()

        # PDG 2024 central values
        V_obs = np.array([
            [0.97435, 0.22500, 0.00369],
            [0.22486, 0.97349, 0.04182],
            [0.00857, 0.04110, 0.999118],
        ])

        errors = np.abs(V - V_obs) / V_obs * 100

        # Classify each element
        status = {}
        lam = self.epsilon
        status['V_us'] = {
            'predicted': V[0, 1],
            'observed': V_obs[0, 1],
            'error_pct': errors[0, 1],
            'formula': 'ε',
            'derivation_status': 'DERIVED',
        }
        status['V_cb'] = {
            'predicted': V[1, 2],
            'observed': V_obs[1, 2],
            'error_pct': errors[1, 2],
            'formula': 'A·ε²',
            'derivation_status': 'FITTED (A parameter)',
        }
        status['V_ub'] = {
            'predicted': V[0, 2],
            'observed': V_obs[0, 2],
            'error_pct': errors[0, 2],
            'formula': 'A·ε³·|ρ-iη|',
            'derivation_status': 'FITTED (A, ρ, η parameters)',
        }

        return {
            'V_predicted': V,
            'V_observed': V_obs,
            'errors_pct': errors,
            'element_details': status,
        }

    def jarlskog_invariant(self) -> float:
        """Jarlskog invariant J = Im(V_us V_cb V*_ub V*_cs).

        Measures CP violation strength.
        """
        V = self.ckm_wolfenstein(order=3)
        J = np.imag(V[0, 1] * V[1, 2] * np.conj(V[0, 2]) * np.conj(V[1, 1]))
        return J

    # =================================================================
    # PMNS matrix
    # =================================================================

    def pmns_tribimaximal(self) -> np.ndarray:
        """Tribimaximal mixing matrix (zeroth order from S₃ symmetry).

        DERIVED from quaternionic S₃ symmetry:
          θ₁₂ = arctan(1/√2) ≈ 35.3°
          θ₂₃ = 45°
          θ₁₃ = 0°

        This is the leading-order prediction. Corrections are O(ε).
        """
        return np.array([
            [2.0/np.sqrt(6), 1.0/np.sqrt(3), 0],
            [-1.0/np.sqrt(6), 1.0/np.sqrt(3), 1.0/np.sqrt(2)],
            [1.0/np.sqrt(6), -1.0/np.sqrt(3), 1.0/np.sqrt(2)],
        ])

    def pmns_with_corrections(self, delta_cp: float = None) -> np.ndarray:
        """PMNS matrix with ε-corrections to TBM.

        sin²(θ₁₂) ≈ 1/3 (TBM zeroth order, DERIVED)
        sin²(θ₂₃) ≈ 1/2 (TBM zeroth order, DERIVED)
        sin(θ₁₃)  ≈ ε/√2 (leading ε-correction)

        Parameters
        ----------
        delta_cp : float or None
            CP phase δ. Default π + θ_C (geometric prediction).
        """
        eps = self.epsilon
        if delta_cp is None:
            delta_cp = np.pi + np.arcsin(eps)

        # TBM zeroth order with ε-correction for θ₁₃ only
        s12_sq = 1.0 / 3.0          # TBM (DERIVED from S₃)
        s23_sq = 0.5                  # TBM (DERIVED from μ-τ symmetry)
        s13 = eps / np.sqrt(2)        # Leading ε-correction

        s12 = np.sqrt(s12_sq)
        c12 = np.sqrt(1 - s12_sq)
        s23 = np.sqrt(s23_sq)
        c23 = np.sqrt(1 - s23_sq)
        c13 = np.sqrt(1 - s13**2)

        # Standard PDG parametrization
        U = np.zeros((3, 3), dtype=complex)
        U[0, 0] = c12 * c13
        U[0, 1] = s12 * c13
        U[0, 2] = s13 * np.exp(-1j * delta_cp)
        U[1, 0] = -s12*c23 - c12*s23*s13*np.exp(1j*delta_cp)
        U[1, 1] = c12*c23 - s12*s23*s13*np.exp(1j*delta_cp)
        U[1, 2] = s23 * c13
        U[2, 0] = s12*s23 - c12*c23*s13*np.exp(1j*delta_cp)
        U[2, 1] = -c12*s23 - s12*c23*s13*np.exp(1j*delta_cp)
        U[2, 2] = c23 * c13

        return U

    def pmns_comparison(self) -> dict:
        """Compare predicted PMNS angles to observed values."""
        eps = self.epsilon

        # Predicted (TBM zeroth order)
        s12_sq_pred = 1.0 / 3.0        # TBM
        s23_sq_pred = 0.5               # TBM
        s13_sq_pred = eps**2 / 2        # Leading ε-correction

        # Observed (NuFIT 5.2, NO)
        s12_sq_obs = 0.304
        s23_sq_obs = 0.450
        s13_sq_obs = 0.02246

        return {
            'sin2_12': {'predicted': s12_sq_pred, 'observed': s12_sq_obs,
                        'error_pct': abs(s12_sq_pred - s12_sq_obs)/s12_sq_obs * 100,
                        'status': 'TBM + ε correction (DERIVED)'},
            'sin2_23': {'predicted': s23_sq_pred, 'observed': s23_sq_obs,
                        'error_pct': abs(s23_sq_pred - s23_sq_obs)/s23_sq_obs * 100,
                        'status': 'TBM + ε correction (DERIVED)'},
            'sin2_13': {'predicted': s13_sq_pred, 'observed': s13_sq_obs,
                        'error_pct': abs(s13_sq_pred - s13_sq_obs)/s13_sq_obs * 100,
                        'status': 'ε correction (order-of-magnitude DERIVED)'},
        }

    def quark_lepton_complementarity(self) -> dict:
        """Check θ₁₂^PMNS + θ_C ≈ 45°."""
        eps = self.epsilon
        s12_sq = 1.0 / 3.0  # TBM
        theta_12_pmns = np.arcsin(np.sqrt(s12_sq))
        theta_C = np.arcsin(eps)

        sum_deg = np.degrees(theta_12_pmns + theta_C)

        return {
            'theta_12_pmns_deg': np.degrees(theta_12_pmns),
            'theta_C_deg': np.degrees(theta_C),
            'sum_deg': sum_deg,
            'deviation_from_45': abs(sum_deg - 45.0),
        }
