"""RETRY: Retry and resilience tests.

Test IDs: RETRY-001 through RETRY-004
See Issue #10 for test case specifications.
"""

import pytest
import requests
from requests.adapters import HTTPAdapter

from jquants import ClientV2

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestRetryNormal:
    """Normal retry/resilience test cases."""

    def test_retry_001_session_reuse(self, fresh_client: ClientV2) -> None:
        """RETRY-001: Session and connection pool are reused."""
        # Make multiple requests
        fresh_client._request("GET", "/equities/master")
        session1 = fresh_client._session

        fresh_client._request("GET", "/equities/master")
        session2 = fresh_client._session

        # Same session object should be reused
        assert session1 is session2
        assert isinstance(session1, requests.Session)

    def test_retry_002_retry_config_values(self, fresh_client: ClientV2) -> None:
        """RETRY-002: Retry strategy configuration is correct.

        429 is handled by custom retry logic in _request(), not by urllib3 Retry.
        Custom 429 retry defaults are tested in test_client_v2.py unit tests.
        """
        # Access the session to trigger creation
        session = fresh_client._request_session()

        # Get the adapter for HTTPS
        adapter = session.get_adapter("https://")
        assert isinstance(adapter, HTTPAdapter)

        # Verify urllib3 Retry configuration
        retry = adapter.max_retries
        assert retry.total == 3
        assert retry.backoff_factor == 0.5
        assert retry.respect_retry_after_header is True

        # 429 is excluded from status_forcelist (handled by custom retry logic)
        assert 429 not in retry.status_forcelist

        # Server errors are in status_forcelist (handled by urllib3 Retry)
        # Use set() for type/order-independent comparison (urllib3 may use frozenset)
        assert set(retry.status_forcelist) == {500, 502, 503, 504}


class TestRetryRare:
    """Rare/edge case retry tests."""

    def test_retry_003_network_error_not_wrapped(self) -> None:
        """RETRY-003: Network errors are not wrapped in JQuantsAPIError.

        requests.ConnectionError should propagate directly.
        """
        # Create client with invalid base URL to trigger connection error
        client = ClientV2(api_key="test-key")
        # Temporarily change base URL
        original_base = client.JQUANTS_API_BASE
        try:
            ClientV2.JQUANTS_API_BASE = "https://invalid.nonexistent.domain.test"
            # Should raise ConnectionError, not JQuantsAPIError
            with pytest.raises(requests.exceptions.ConnectionError):
                client._request("GET", "/test")
        finally:
            ClientV2.JQUANTS_API_BASE = original_base

    def test_retry_004_invalid_host_dns_error(self) -> None:
        """RETRY-004: Invalid host triggers DNS resolution error."""
        client = ClientV2(api_key="test-key")
        original_base = client.JQUANTS_API_BASE
        try:
            ClientV2.JQUANTS_API_BASE = "https://this-host-does-not-exist.invalid"
            with pytest.raises(requests.exceptions.ConnectionError):
                client._request("GET", "/test")
        finally:
            ClientV2.JQUANTS_API_BASE = original_base
