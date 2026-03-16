"""Client for the Riemannian Portfolio Optimization API."""

from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseClient


class PortfolioClient:
    """Riemannian portfolio optimization on the SPD covariance manifold."""

    def __init__(self, _client: BaseClient):
        self._c = _client

    def covariance(
        self,
        returns: np.ndarray,
        method: str = "frechet",
        window: int = 60,
        annualize: bool = False,
        **kwargs: Any,
    ) -> np.ndarray:
        """Estimate covariance matrix using Riemannian (Frechet) or classical methods.

        Args:
            returns: (T, d) array of asset returns.
            method: One of "frechet", "log_euclidean", "arithmetic".
            window: Rolling window size.
            annualize: Multiply by 252 if True.

        Returns:
            (d, d) covariance matrix as numpy array.
        """
        body = {
            "returns": returns.tolist(),
            "method": method,
            "window": window,
            "annualize": annualize,
            **kwargs,
        }
        resp = self._c.post("/portfolio/covariance", json=body)
        return np.array(resp["covariance"])

    def optimize(
        self,
        returns: np.ndarray,
        strategy: str = "min_variance",
        method: str = "riemannian",
        long_only: bool = False,
        expected_returns: np.ndarray | None = None,
        risk_aversion: float = 1.0,
        window: int = 60,
        **kwargs: Any,
    ) -> dict:
        """Optimize portfolio weights.

        Args:
            returns: (T, d) array of asset returns.
            strategy: "min_variance", "risk_parity", "max_diversification", "mean_variance".
            method: Covariance method ("riemannian", "euclidean", "ledoit_wolf").
            long_only: Enforce non-negative weights (min_variance only).
            expected_returns: Required for mean_variance strategy.
            risk_aversion: Risk aversion parameter for mean_variance.
            window: Rolling window size.

        Returns:
            Dict with keys: weights, expected_risk, condition_number, strategy, method, details.
        """
        body: dict[str, Any] = {
            "returns": returns.tolist(),
            "strategy": strategy,
            "method": method,
            "long_only": long_only,
            "risk_aversion": risk_aversion,
            "window": window,
            **kwargs,
        }
        if expected_returns is not None:
            body["expected_returns"] = expected_returns.tolist()
        resp = self._c.post("/portfolio/optimize", json=body)
        resp["weights"] = np.array(resp["weights"])
        return resp

    def regime_detection(
        self,
        returns: np.ndarray,
        window: int = 60,
        step: int = 5,
        threshold: float = 2.0,
        **kwargs: Any,
    ) -> dict:
        """Detect regime changes via geodesic distances between rolling covariances.

        Args:
            returns: (T, d) array of asset returns.
            window: Rolling window size.
            step: Step size between consecutive windows.
            threshold: Z-score threshold for change detection.

        Returns:
            Dict with geodesic_distances, euclidean_distances, change indices, n_detections.
        """
        body = {
            "returns": returns.tolist(),
            "window": window,
            "step": step,
            "threshold": threshold,
            **kwargs,
        }
        resp = self._c.post("/portfolio/regime-detection", json=body)
        resp["geodesic_distances"] = np.array(resp["geodesic_distances"])
        resp["euclidean_distances"] = np.array(resp["euclidean_distances"])
        return resp

    def forecast(
        self,
        returns: np.ndarray,
        horizon: int = 3,
        window: int = 60,
        **kwargs: Any,
    ) -> dict:
        """Forecast future covariance matrices.

        Args:
            returns: (T, d) array of asset returns.
            horizon: Number of steps ahead to forecast.
            window: Rolling window size.

        Returns:
            Dict with "euclidean" and "riemannian" forecast entries.
        """
        body = {
            "returns": returns.tolist(),
            "n_ahead": horizon,
            "window": window,
            **kwargs,
        }
        return self._c.post("/portfolio/forecast", json=body)

    def compare(
        self,
        returns: np.ndarray,
        window: int = 60,
        **kwargs: Any,
    ) -> dict:
        """Compare covariance estimation methods side-by-side.

        Args:
            returns: (T, d) array of asset returns.
            window: Rolling window size.

        Returns:
            Dict keyed by method name with condition numbers, weights, etc.
        """
        body = {
            "returns": returns.tolist(),
            "window": window,
            **kwargs,
        }
        return self._c.post("/portfolio/compare", json=body)
