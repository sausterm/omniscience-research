"""Client for the BCI (Brain-Computer Interface) Riemannian Classification API."""

from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseClient


class BCIClient:
    """EEG/BCI classification using Riemannian geometry of SPD covariance matrices."""

    def __init__(self, _client: BaseClient):
        self._c = _client

    def classify(
        self,
        covariances: np.ndarray,
        labels: np.ndarray,
        method: str = "mdm",
        **kwargs: Any,
    ) -> dict:
        """Classify EEG trials from their covariance matrices.

        Args:
            covariances: (n_trials, n_channels, n_channels) SPD matrices.
            labels: (n_trials,) integer class labels.
            method: Classification method ("mdm", "tangent_svm", "geodesic_knn").

        Returns:
            Dict with predictions, accuracy, and method-specific details.
        """
        return self._c.post("/bci/classify", json={
            "covariances": covariances.tolist(),
            "labels": labels.tolist(),
            "method": method,
            **kwargs,
        })

    def geometry(self, covariances: np.ndarray, **kwargs: Any) -> dict:
        """Compute geometric summary statistics for a set of covariance matrices.

        Args:
            covariances: (n_trials, n_channels, n_channels) SPD matrices.

        Returns:
            Dict with frechet_mean, dispersion, geodesic_distances, etc.
        """
        return self._c.post("/bci/geometry", json={
            "covariances": covariances.tolist(),
            **kwargs,
        })

    def geodesic_distance(
        self,
        cov_a: np.ndarray,
        cov_b: np.ndarray,
    ) -> dict:
        """Geodesic distance between two SPD covariance matrices.

        Args:
            cov_a: (n, n) SPD matrix.
            cov_b: (n, n) SPD matrix.

        Returns:
            Dict with distance value.
        """
        return self._c.post("/bci/geodesic-distance", json={
            "cov_a": cov_a.tolist(),
            "cov_b": cov_b.tolist(),
        })

    def tangent_space(
        self,
        covariances: np.ndarray,
        reference: np.ndarray | None = None,
        **kwargs: Any,
    ) -> dict:
        """Project SPD matrices to tangent space at a reference point.

        Args:
            covariances: (n_trials, n_channels, n_channels) SPD matrices.
            reference: (n_channels, n_channels) SPD reference point.
                       If None, the Frechet mean is used.

        Returns:
            Dict with tangent_vectors array and reference point used.
        """
        body: dict[str, Any] = {
            "covariances": covariances.tolist(),
            **kwargs,
        }
        if reference is not None:
            body["reference"] = reference.tolist()
        return self._c.post("/bci/tangent-space", json=body)
