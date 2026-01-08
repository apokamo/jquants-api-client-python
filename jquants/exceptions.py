"""Custom exceptions for J-Quants API client."""


class JQuantsAPIError(Exception):
    """J-Quants API base exception.

    All J-Quants client errors inherit from this class.
    Users can catch all client-related errors with `except JQuantsAPIError`.

    Attributes:
        status_code: HTTP status code (None for non-HTTP errors like pagination issues)
        response_body: Raw response body for debugging (truncated to 2048 chars)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize JQuantsAPIError.

        Args:
            message: Error message
            status_code: HTTP status code (None for non-HTTP errors)
            response_body: Raw response body for debugging
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class JQuantsForbiddenError(JQuantsAPIError):
    """Forbidden error (403 Forbidden).

    Raised when access is denied. Common causes:
    - Invalid or expired API key
    - Plan limitation (e.g., Free plan accessing Premium-only endpoints)
    - Invalid resource path
    """

    pass


class JQuantsRateLimitError(JQuantsAPIError):
    """Rate limit exceeded (429 Too Many Requests).

    Raised when the API rate limit is exceeded after retry attempts.
    """

    pass
