"""Tests for jquants.exceptions module."""

import pytest

from jquants.exceptions import (
    JQuantsAPIError,
    JQuantsForbiddenError,
    JQuantsRateLimitError,
)


class TestJQuantsAPIError:
    """Tests for JQuantsAPIError base class."""

    def test_constructor_preserves_attributes(self):
        """E001: Constructor preserves status_code and response_body."""
        error = JQuantsAPIError(
            message="Test error",
            status_code=400,
            response_body='{"message": "Bad request"}',
        )

        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_body == '{"message": "Bad request"}'

    def test_status_code_none_allowed(self):
        """E002: status_code=None is allowed for non-HTTP errors."""
        error = JQuantsAPIError(
            message="Pagination error",
            status_code=None,
            response_body=None,
        )

        assert error.status_code is None
        assert error.response_body is None

    def test_message_propagation(self):
        """E003: Error message is correctly propagated."""
        message = "API returned unexpected response"
        error = JQuantsAPIError(message)

        assert str(error) == message
        # Default values
        assert error.status_code is None
        assert error.response_body is None


class TestJQuantsForbiddenError:
    """Tests for JQuantsForbiddenError (403 Forbidden)."""

    def test_inherits_from_api_error(self):
        """JQuantsForbiddenError can be caught with except JQuantsAPIError."""
        error = JQuantsForbiddenError("Forbidden", status_code=403)

        assert isinstance(error, JQuantsAPIError)

    def test_can_be_caught_by_base_class(self):
        """Verify catch behavior with except JQuantsAPIError."""
        with pytest.raises(JQuantsAPIError):
            raise JQuantsForbiddenError("Plan limitation", status_code=403)


class TestJQuantsRateLimitError:
    """Tests for JQuantsRateLimitError (429 Too Many Requests)."""

    def test_inherits_from_api_error(self):
        """JQuantsRateLimitError can be caught with except JQuantsAPIError."""
        error = JQuantsRateLimitError("Rate limit exceeded", status_code=429)

        assert isinstance(error, JQuantsAPIError)

    def test_can_be_caught_by_base_class(self):
        """Verify catch behavior with except JQuantsAPIError."""
        with pytest.raises(JQuantsAPIError):
            raise JQuantsRateLimitError("Too many requests", status_code=429)
