"""OmniSciences API client — unified access to all product APIs.

Usage::

    import omnisciences

    client = omnisciences.OmniClient(api_key="omni_...")

    # Portfolio optimization
    cov = client.portfolio.covariance(returns_array)
    weights = client.portfolio.optimize(returns_array, strategy="risk_parity")

    # DTI analysis
    result = client.dti.analyze(tensor_3x3)

    # PCET rate prediction
    rate = client.pcet.rate({"V_el": 0.02, "delta_G": -0.5, ...})

    # BCI classification
    pred = client.bci.classify(covariance_matrices, labels)
"""

from __future__ import annotations

from .base import BaseClient
from .portfolio import PortfolioClient
from .dti import DTIClient
from .pcet import PCETClient
from .bci import BCIClient
from .exceptions import (
    OmniAPIError,
    OmniAuthError,
    OmniRateLimitError,
    OmniValidationError,
)


class OmniClient:
    """Unified client for all OmniSciences APIs.

    Args:
        api_key: API key string. Falls back to OMNI_API_KEY env var.
        base_url: Override base URL. Falls back to OMNI_API_URL env var,
                  then https://api.omnisciences.io.
        timeout: Request timeout in seconds (default 60).
        max_retries: Number of retries on transient failures (default 3).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60,
        max_retries: int = 3,
    ):
        self._base = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.portfolio = PortfolioClient(self._base)
        self.dti = DTIClient(self._base)
        self.pcet = PCETClient(self._base)
        self.bci = BCIClient(self._base)


__all__ = [
    "OmniClient",
    "OmniAPIError",
    "OmniAuthError",
    "OmniRateLimitError",
    "OmniValidationError",
]
