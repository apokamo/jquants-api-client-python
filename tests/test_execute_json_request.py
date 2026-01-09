"""Tests for _execute_json_request() method.

This module tests the new request pipeline method that encapsulates
JSON parsing and validation on top of _request().

Test categories:
- EJSON-001 ~ EJSON-003: Normal cases
- EJSON-004 ~ EJSON-007: Error cases (JSON parse, response shape)
- EJSON-008 ~ EJSON-010: Edge cases (empty response, etc.)
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from jquants import ClientV2
from jquants.exceptions import JQuantsAPIError


@pytest.fixture
def client() -> ClientV2:
    """Create a ClientV2 instance with mocked API key."""
    with patch.dict("os.environ", {"JQUANTS_API_KEY": "test-api-key"}):
        return ClientV2()


class TestExecuteJsonRequestNormal:
    """Normal cases for _execute_json_request()."""

    def test_ejson_001_returns_dict(self, client: ClientV2) -> None:
        """EJSON-001: _execute_json_request returns parsed dict."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"data": [{"Code": "7203"}]}

        with patch.object(client, "_request", return_value=mock_response):
            result = client._execute_json_request("GET", "/test/path")

        assert result == {"data": [{"Code": "7203"}]}

    def test_ejson_002_passes_params(self, client: ClientV2) -> None:
        """EJSON-002: _execute_json_request passes params to _request."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"data": []}

        with patch.object(client, "_request", return_value=mock_response) as mock_req:
            client._execute_json_request(
                "GET", "/test/path", params={"code": "7203", "date": "2024-01-01"}
            )

        mock_req.assert_called_once_with(
            "GET",
            "/test/path",
            params={"code": "7203", "date": "2024-01-01"},
            json_data=None,
        )

    def test_ejson_003_passes_json_data(self, client: ClientV2) -> None:
        """EJSON-003: _execute_json_request passes json_data to _request."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"data": []}

        with patch.object(client, "_request", return_value=mock_response) as mock_req:
            client._execute_json_request(
                "POST", "/test/path", json_data={"key": "value"}
            )

        mock_req.assert_called_once_with(
            "POST", "/test/path", params=None, json_data={"key": "value"}
        )


class TestExecuteJsonRequestError:
    """Error cases for _execute_json_request()."""

    def test_ejson_004_json_parse_error_raises_api_error(
        self, client: ClientV2
    ) -> None:
        """EJSON-004: JSON parse error raises JQuantsAPIError with preview."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.side_effect = ValueError("Expecting value")
        mock_response.text = "Invalid JSON content here"

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(JQuantsAPIError) as exc_info:
                client._execute_json_request("GET", "/test/path")

        error = exc_info.value
        assert error.status_code is None
        assert "Failed to parse JSON response" in str(error)
        assert "Invalid JSON content here" in str(error)

    def test_ejson_005_json_type_error_raises_api_error(self, client: ClientV2) -> None:
        """EJSON-005: JSON TypeError raises JQuantsAPIError."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.side_effect = TypeError("unexpected type")
        mock_response.text = "some text"

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(JQuantsAPIError) as exc_info:
                client._execute_json_request("GET", "/test/path")

        error = exc_info.value
        assert error.status_code is None
        assert "Failed to parse JSON response" in str(error)

    def test_ejson_006_empty_text_in_error_preview(self, client: ClientV2) -> None:
        """EJSON-006: Empty response text shows '(empty)' in preview."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.side_effect = ValueError("No data")
        mock_response.text = ""

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(JQuantsAPIError) as exc_info:
                client._execute_json_request("GET", "/test/path")

        assert "(empty)" in str(exc_info.value)

    def test_ejson_007_long_text_truncated_in_preview(self, client: ClientV2) -> None:
        """EJSON-007: Long response text is truncated in preview (~200 chars)."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.side_effect = ValueError("Parse error")
        mock_response.text = "X" * 500  # 500 chars

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(JQuantsAPIError) as exc_info:
                client._execute_json_request("GET", "/test/path")

        error_message = str(exc_info.value)
        # Should be truncated (not all 500 X's)
        assert error_message.count("X") <= 200
        assert "X" in error_message


class TestExecuteJsonRequestEdge:
    """Edge cases for _execute_json_request()."""

    def test_ejson_008_empty_dict_response(self, client: ClientV2) -> None:
        """EJSON-008: Empty dict {} is valid response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {}

        with patch.object(client, "_request", return_value=mock_response):
            result = client._execute_json_request("GET", "/test/path")

        assert result == {}

    def test_ejson_009_empty_data_list(self, client: ClientV2) -> None:
        """EJSON-009: {"data": []} is valid response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"data": []}

        with patch.object(client, "_request", return_value=mock_response):
            result = client._execute_json_request("GET", "/test/path")

        assert result == {"data": []}

    def test_ejson_010_none_params_and_json_data(self, client: ClientV2) -> None:
        """EJSON-010: None params and json_data are handled."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"data": []}

        with patch.object(client, "_request", return_value=mock_response) as mock_req:
            client._execute_json_request("GET", "/test/path")

        mock_req.assert_called_once_with(
            "GET", "/test/path", params=None, json_data=None
        )
