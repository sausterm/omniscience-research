"""Base HTTP client with auth, retries, and error handling."""

from __future__ import annotations

import os
import time
from typing import Any

import requests

from .exceptions import (
    OmniAPIError,
    OmniAuthError,
    OmniRateLimitError,
    OmniValidationError,
)

DEFAULT_BASE_URL = "https://api.omnisciences.io"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0  # seconds: 1, 2, 4


class BaseClient:
    """Low-level HTTP client shared by all product clients."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        self.api_key = api_key or os.environ.get("OMNI_API_KEY", "")
        self.base_url = (
            base_url or os.environ.get("OMNI_API_URL", DEFAULT_BASE_URL)
        ).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ------------------------------------------------------------------
    # Core request method
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        """Issue an HTTP request with retry + exponential backoff.

        Returns the parsed JSON response body.
        """
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                resp = self._session.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    timeout=self.timeout,
                )
                return self._handle_response(resp)

            except (OmniRateLimitError, requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    wait = BACKOFF_FACTOR * (2 ** attempt)
                    if isinstance(exc, OmniRateLimitError) and exc.retry_after:
                        wait = exc.retry_after
                    time.sleep(wait)
                    continue
                raise

            except OmniAPIError:
                raise

        # Should not reach here, but just in case:
        raise last_exc  # type: ignore[misc]

    def _handle_response(self, resp: requests.Response) -> Any:
        """Parse response, raising typed exceptions on errors."""
        if resp.status_code == 204:
            return None

        # Try to get JSON body for error detail
        try:
            body = resp.json()
        except ValueError:
            body = {"detail": resp.text}

        if resp.ok:
            return body

        detail = body.get("detail", resp.text)

        if resp.status_code in (401, 403):
            raise OmniAuthError(
                f"Authentication failed: {detail}",
                status_code=resp.status_code,
                response=body,
            )

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            raise OmniRateLimitError(
                message=f"Rate limit exceeded: {detail}",
                retry_after=float(retry_after) if retry_after else None,
                status_code=resp.status_code,
                response=body,
            )

        if resp.status_code == 422:
            raise OmniValidationError(
                f"Validation error: {detail}",
                status_code=422,
                response=body,
            )

        raise OmniAPIError(
            f"API error ({resp.status_code}): {detail}",
            status_code=resp.status_code,
            response=body,
        )

    # Convenience wrappers

    def get(self, path: str, **kwargs) -> Any:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> Any:
        return self._request("POST", path, json=json, **kwargs)
