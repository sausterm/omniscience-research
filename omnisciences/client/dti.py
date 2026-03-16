"""Client for the DTI Curvature Analysis API."""

from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseClient


class DTIClient:
    """Diffusion tensor analysis using Riemannian geometry of GL+(3)/SO(3)."""

    def __init__(self, _client: BaseClient):
        self._c = _client

    def analyze(self, tensor: np.ndarray) -> dict:
        """Full analysis of a single 3x3 SPD diffusion tensor.

        Args:
            tensor: (3, 3) symmetric positive-definite array.

        Returns:
            Dict with fa, md, curvature_anisotropy, tissue_type, confidence, eigenvalues.
        """
        resp = self._c.post("/dti/analyze", json={"tensor": tensor.tolist()})
        resp["eigenvalues"] = np.array(resp["eigenvalues"])
        return resp

    def distance(self, tensor_a: np.ndarray, tensor_b: np.ndarray) -> dict:
        """Geodesic distance between two diffusion tensors.

        Args:
            tensor_a: (3, 3) SPD array.
            tensor_b: (3, 3) SPD array.

        Returns:
            Dict with distance value.
        """
        return self._c.post("/dti/distance", json={
            "tensor1": tensor_a.tolist(),
            "tensor2": tensor_b.tolist(),
        })

    def interpolate(
        self,
        tensor_a: np.ndarray,
        tensor_b: np.ndarray,
        t: float = 0.5,
    ) -> dict:
        """Geodesic interpolation between two tensors.

        Args:
            tensor_a: (3, 3) SPD array (t=0).
            tensor_b: (3, 3) SPD array (t=1).
            t: Interpolation parameter in [0, 1].

        Returns:
            Dict with interpolated tensor, fa, md, curvature_anisotropy.
        """
        resp = self._c.post("/dti/interpolate", json={
            "tensor1": tensor_a.tolist(),
            "tensor2": tensor_b.tolist(),
            "t": t,
        })
        resp["tensor"] = np.array(resp["tensor"])
        return resp

    def batch(self, tensors: list[np.ndarray]) -> dict:
        """Batch analysis of multiple tensors (up to 10,000).

        Args:
            tensors: List of (3, 3) SPD arrays.

        Returns:
            Dict with fa, md, curvature_anisotropy arrays and count.
        """
        resp = self._c.post("/dti/batch", json={
            "tensors": [t.tolist() for t in tensors],
        })
        resp["fa"] = np.array(resp["fa"])
        resp["md"] = np.array(resp["md"])
        resp["curvature_anisotropy"] = np.array(resp["curvature_anisotropy"])
        return resp

    def health(self) -> dict:
        """Health check with geometry metadata.

        Returns:
            Dict with status, version, geometry info.
        """
        return self._c.get("/dti/health")
