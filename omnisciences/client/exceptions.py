"""Exception classes for the OmniSciences API client."""


class OmniAPIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class OmniAuthError(OmniAPIError):
    """Raised on 401/403 authentication or authorization failures."""
    pass


class OmniRateLimitError(OmniAPIError):
    """Raised on 429 rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float | None = None,
        **kwargs,
    ):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class OmniValidationError(OmniAPIError):
    """Raised on 422 validation errors."""
    pass
