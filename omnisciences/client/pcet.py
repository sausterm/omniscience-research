"""Client for the PCET Rate Theory Engine API."""

from __future__ import annotations

from typing import Any

from .base import BaseClient


class PCETClient:
    """Proton-Coupled Electron Transfer rate prediction from Marcus theory + vibronic tunneling."""

    def __init__(self, _client: BaseClient):
        self._c = _client

    def benchmarks(self) -> list[dict]:
        """Retrieve benchmark enzyme systems with predicted vs experimental KIE.

        Returns:
            List of dicts with name, description, KIE_exp, KIE_pred, KIE_error_pct, k_H_pred.
        """
        return self._c.get("/v1/benchmarks")

    def rate(self, params: dict) -> dict:
        """Compute PCET rate from explicit physical parameters.

        Args:
            params: Dict with keys such as V_el, delta_G, lambda_reorg, omega_H,
                    d_DA, method, temperature, delta_0.

        Returns:
            Dict with k_H, k_D, KIE, E_a, omega_H, omega_D, method,
            tunneling_contribution.
        """
        return self._c.post("/v1/rate/parameters", json=params)

    def electrochemical(self, params: dict) -> dict:
        """Compute electrochemical PCET rate with overpotential.

        Args:
            params: Dict with keys such as V_el, delta_G_base, lambda_reorg,
                    omega_H, d_DA, overpotential, direction, temperature.

        Returns:
            Dict with k_H, k_D, KIE, overpotential, direction.
        """
        return self._c.post("/v1/rate/electrochemical", json=params)

    def uncertainty(self, params: dict) -> dict:
        """Monte Carlo uncertainty quantification for rate predictions.

        Args:
            params: Dict with parameter means and errors (e.g. V_el, V_el_err,
                    delta_G, delta_G_err, ..., n_samples, temperature, seed).

        Returns:
            Dict with k_H_mean, k_H_std, k_H_ci, k_D_mean, k_D_std,
            KIE_mean, KIE_std, KIE_ci, sensitivities, n_samples.
        """
        return self._c.post("/v1/rate/uncertainty", json=params)
