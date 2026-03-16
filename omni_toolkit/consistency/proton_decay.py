"""
Proton decay lifetime computation for Pati-Salam models.

Computes all major channels: p → e+π0, p → K+ν̄, p → π+ν̄.
Also checks neutron-antineutron oscillation bounds.
"""

import math
import numpy as np


class ProtonDecay:
    """Compute proton decay lifetimes in Pati-Salam.

    Parameters
    ----------
    M_X : float
        Gauge boson mass mediating proton decay (~ M_C).
    alpha_X : float
        Gauge coupling at M_X.
    alpha_H : float
        Hadronic matrix element squared, default 0.015 GeV^3 (lattice).
    """

    M_P_GEV = 0.93827  # proton mass in GeV
    M_PI_GEV = 0.135    # pion mass in GeV
    M_K_GEV = 0.494     # kaon mass in GeV
    HBAR_S = 6.582e-25   # hbar in GeV·s
    YR_S = 3.156e7       # seconds per year

    # Experimental bounds (90% CL, years)
    BOUNDS = {
        'e+pi0': 2.4e34,    # Super-K
        'K+nubar': 5.9e33,  # Super-K
        'pi+nubar': 3.9e32, # Super-K
    }

    def __init__(self, M_X: float, alpha_X: float, alpha_H: float = 0.015):
        self.M_X = M_X
        self.alpha_X = alpha_X
        self.g_X = math.sqrt(4 * math.pi * alpha_X)
        self.alpha_H = alpha_H  # GeV^3

    def _base_rate(self) -> float:
        """Base decay rate: Γ_base = (m_p / 32π) × (g²/M_X²)² × α_H²."""
        g2 = self.g_X ** 2
        prefactor = self.M_P_GEV / (32 * math.pi)
        amplitude_sq = (g2 / self.M_X ** 2) ** 2
        return prefactor * amplitude_sq * self.alpha_H ** 2

    def _phase_space(self, m_meson: float) -> float:
        """Phase space factor: (1 - m_meson²/m_p²)²."""
        return (1 - (m_meson / self.M_P_GEV) ** 2) ** 2

    def _rg_enhancement(self) -> float:
        """RG short-distance enhancement factor A_R ≈ 2.5."""
        return 2.5

    def lifetime_years(self, channel: str) -> float:
        """Compute proton lifetime in years for a given channel.

        Parameters
        ----------
        channel : str
            One of 'e+pi0', 'K+nubar', 'pi+nubar'.
        """
        rate = self._base_rate() * self._rg_enhancement() ** 2

        if channel == 'e+pi0':
            rate *= self._phase_space(self.M_PI_GEV)
        elif channel == 'K+nubar':
            rate *= self._phase_space(self.M_K_GEV)
            # Cabibbo suppression for K+ channel
            rate *= 0.2253 ** 2
        elif channel == 'pi+nubar':
            rate *= self._phase_space(self.M_PI_GEV)
            # Additional chirality suppression
            rate *= 0.1
        else:
            raise ValueError(f"Unknown channel: {channel}")

        if rate <= 0:
            return float('inf')

        # τ = ℏ / Γ, convert to years
        tau_s = self.HBAR_S / rate
        return tau_s / self.YR_S

    def check_all_channels(self) -> dict:
        """Compute lifetimes for all channels and compare to bounds."""
        results = {}
        all_safe = True
        for channel, bound in self.BOUNDS.items():
            tau = self.lifetime_years(channel)
            safe = tau > bound
            margin = math.log10(tau / bound) if tau > 0 and bound > 0 else float('inf')
            results[channel] = {
                'lifetime_yr': tau,
                'log10_lifetime': math.log10(tau) if tau > 0 else float('inf'),
                'bound_yr': bound,
                'log10_bound': math.log10(bound),
                'safe': safe,
                'margin_decades': margin,
            }
            if not safe:
                all_safe = False
        results['all_safe'] = all_safe
        return results

    def nn_bar_oscillation_time(self) -> float:
        """Neutron-antineutron oscillation time in seconds.

        In PS, this is dimension-9 operator, suppressed by M_X^5.
        τ_{n-nbar} ~ M_X^5 / Λ_QCD^6
        """
        Lambda_QCD = 0.3  # GeV
        tau_s = self.HBAR_S * (self.M_X ** 5) / (Lambda_QCD ** 6)
        return tau_s
