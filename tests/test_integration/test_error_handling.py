"""ERR: Error handling tests.

Test IDs: ERR-001 through ERR-013
See Issue #10 for test case specifications.

Note: V2 API returns 403 (not 401) for invalid API keys.
See: https://jpx-jquants.com/ja/spec/response-status
"""

import pytest

from jquants import ClientV2
from jquants.exceptions import JQuantsAPIError, JQuantsForbiddenError

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestErrorHandlingNormal:
    """Normal error handling test cases."""

    def test_err_001_403_invalid_api_key(self, invalid_api_key: str) -> None:
        """ERR-001: Invalid API key raises JQuantsForbiddenError (403).

        Note: V2 API returns 403 (not 401) for invalid API keys.
        """
        client = ClientV2(api_key=invalid_api_key)
        with pytest.raises(JQuantsForbiddenError) as exc_info:
            client._request("GET", "/equities/master")
        assert exc_info.value.status_code == 403

    def test_err_002_403_plan_restriction(self) -> None:
        """ERR-002: Plan restriction raises JQuantsForbiddenError (403).

        Note: Requires Free plan accessing Premium-only endpoint.
        Covered in unit tests for path coverage.
        """
        pytest.skip(
            "Plan restriction test requires specific account - covered in unit tests"
        )

    def test_err_003_invalid_path_error(self, client: ClientV2) -> None:
        """ERR-003: Invalid path raises JQuantsAPIError."""
        with pytest.raises(JQuantsAPIError) as exc_info:
            client._request("GET", "/nonexistent/path/404")
        # V2 API returns 403 for invalid paths (not 404)
        assert exc_info.value.status_code == 403

    def test_err_004_400_bad_request(self, client: ClientV2) -> None:
        """ERR-004: 400 Bad Request raises JQuantsAPIError."""
        with pytest.raises(JQuantsAPIError) as exc_info:
            client._request(
                "GET",
                "/equities/bars/daily",
                params={"date": "invalid-date-format"},
            )
        assert exc_info.value.status_code == 400

    def test_err_005_error_contains_response_body(self, invalid_api_key: str) -> None:
        """ERR-005: Error exception contains response_body attribute."""
        client = ClientV2(api_key=invalid_api_key)
        with pytest.raises(JQuantsForbiddenError) as exc_info:
            client._request("GET", "/equities/master")
        assert exc_info.value.response_body is not None

    def test_err_006_exception_inheritance(self, invalid_api_key: str) -> None:
        """ERR-006: JQuantsForbiddenError is caught by JQuantsAPIError."""
        client = ClientV2(api_key=invalid_api_key)

        # Can catch with base exception
        with pytest.raises(JQuantsAPIError):
            client._request("GET", "/equities/master")

    def test_err_007_json_error_message_extraction(self, invalid_api_key: str) -> None:
        """ERR-007: Error message is extracted from JSON response."""
        client = ClientV2(api_key=invalid_api_key)
        with pytest.raises(JQuantsForbiddenError) as exc_info:
            client._request("GET", "/equities/master")
        message = str(exc_info.value)
        assert message  # Not empty
        assert len(message) > 5


class TestErrorHandlingRare:
    """Rare/edge case error handling tests."""

    def test_err_008_non_json_error_response(self) -> None:
        """ERR-008: Non-JSON error response doesn't crash.

        Note: Hard to trigger with real API - covered in unit tests.
        """
        pytest.skip("Non-JSON response is rare from J-Quants API - unit tested")

    def test_err_009_large_response_truncation(self) -> None:
        """ERR-009: Large error response is truncated to 2048 chars.

        Note: Hard to trigger with real API - covered in unit tests.
        """
        assert ClientV2.RESPONSE_BODY_MAX_LENGTH == 2048
        pytest.skip("Large error response is rare from J-Quants API - unit tested")

    def test_err_010_large_message_truncation(self) -> None:
        """ERR-010: Large message field is truncated.

        Note: Hard to trigger with real API - covered in unit tests.
        """
        pytest.skip("Large message field is rare from J-Quants API - unit tested")

    def test_err_011_dict_message_serialization(self) -> None:
        """ERR-011: Non-string message (dict/list) is serialized.

        Note: Hard to trigger with real API - covered in unit tests.
        """
        pytest.skip("Dict message is rare from J-Quants API - unit tested")

    def test_err_012_empty_response_body(self) -> None:
        """ERR-012: Empty response body falls back to status code.

        Note: Hard to trigger with real API - covered in unit tests.
        """
        pytest.skip("Empty response is rare from J-Quants API - unit tested")

    def test_err_013_multiple_errors_session_state(self, invalid_api_key: str) -> None:
        """ERR-013: Multiple errors don't corrupt session state."""
        client = ClientV2(api_key=invalid_api_key)

        # First error
        with pytest.raises(JQuantsForbiddenError):
            client._request("GET", "/equities/master")

        # Second error - session should still work
        with pytest.raises(JQuantsForbiddenError):
            client._request("GET", "/equities/master")

        # Third error - same
        with pytest.raises(JQuantsForbiddenError):
            client._request("GET", "/equities/master")

        # Session is still valid (exists and is a Session object)
        assert client._session is not None
