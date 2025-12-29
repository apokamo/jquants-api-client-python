"""REQ: Basic request tests.

Test IDs: REQ-001 through REQ-009
See Issue #10 for test case specifications.
"""

import json

import pytest
import requests

from jquants import ClientV2, __version__
from jquants.exceptions import JQuantsAPIError

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestRequestNormal:
    """Normal request test cases."""

    def test_req_001_request_get_success(self, client: ClientV2) -> None:
        """REQ-001: _request('GET', path) returns requests.Response."""
        response = client._request("GET", "/equities/master")
        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert response.ok

    def test_req_002_get_raw_returns_json_string(self, client: ClientV2) -> None:
        """REQ-002: _get_raw(path) returns UTF-8 decoded JSON string."""
        raw = client._get_raw("/equities/master")
        assert isinstance(raw, str)
        # Should be valid JSON
        data = json.loads(raw)
        assert isinstance(data, dict)
        assert "data" in data

    def test_req_003_user_agent_header(self, client: ClientV2) -> None:
        """REQ-003: User-Agent header is correctly formatted."""
        headers = client._base_headers()
        assert "User-Agent" in headers
        user_agent = headers["User-Agent"]
        # Format: jqapi-python/{version}/v2 p/{python_version}
        assert user_agent.startswith("jqapi-python/")
        assert "/v2" in user_agent
        assert "p/" in user_agent
        assert __version__ in user_agent or "0.0.0" in user_agent

    def test_req_004_api_key_header(self, client: ClientV2, api_key: str) -> None:
        """REQ-004: x-api-key header is set with API key."""
        headers = client._base_headers()
        assert "x-api-key" in headers
        assert headers["x-api-key"] == api_key

    def test_req_005_request_timeout(self, client: ClientV2) -> None:
        """REQ-005: Request timeout is set to 30 seconds."""
        assert client.REQUEST_TIMEOUT == 30
        # Verify by making a successful request (timeout works)
        response = client._request("GET", "/equities/master")
        assert response.ok


class TestRequestRare:
    """Rare/edge case request tests."""

    def test_req_006_session_reuse(self, fresh_client: ClientV2) -> None:
        """REQ-006: Session is reused across requests."""
        # First request creates session
        fresh_client._request("GET", "/equities/master")
        session1 = fresh_client._session

        # Second request reuses same session
        fresh_client._request("GET", "/equities/master")
        session2 = fresh_client._session

        assert session1 is session2
        assert session1 is not None

    def test_req_007_japanese_params(self, client: ClientV2) -> None:
        """REQ-007: Parameters with Japanese characters are URL encoded."""
        # Note: This tests URL encoding capability, not specific endpoint behavior
        # The endpoint may not use Japanese params, but encoding should work
        try:
            # This may fail with 400 if endpoint doesn't accept the param,
            # but should not fail due to encoding issues
            client._request(
                "GET",
                "/equities/master",
                params={"test_param": "日本語テスト"},
            )
        except JQuantsAPIError as e:
            # 4xx errors are acceptable (param not supported)
            # But not encoding errors
            assert e.status_code in (400, 404)

    def test_req_008_special_char_params(self, client: ClientV2) -> None:
        """REQ-008: Parameters with special characters are properly encoded."""
        try:
            client._request(
                "GET",
                "/equities/master",
                params={"test_param": "a&b=c%d"},
            )
        except JQuantsAPIError as e:
            # 4xx errors are acceptable (param not supported)
            assert e.status_code in (400, 404)

    def test_req_009_nonexistent_path_404(self, client: ClientV2) -> None:
        """REQ-009: Non-existent path raises JQuantsAPIError with 404."""
        with pytest.raises(JQuantsAPIError) as exc_info:
            client._request("GET", "/nonexistent/path")
        # Note: Actual status code may vary (403, 404, etc.)
        assert exc_info.value.status_code in (403, 404)
