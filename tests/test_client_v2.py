"""Phase 2 & 3.1 TDD tests: ClientV2 authentication, configuration, and error handling."""

import os
import platform
import sys
import tempfile
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from jquants import __version__
from jquants.exceptions import (
    JQuantsAPIError,
    JQuantsForbiddenError,
    JQuantsRateLimitError,
)


class TestClientV2Instantiation:
    """Test ClientV2 instantiation with various inputs."""

    def test_instantiation_with_valid_api_key(self):
        """ClientV2(api_key="valid_key") should create instance successfully."""
        from jquants import ClientV2

        client = ClientV2(api_key="valid_api_key")
        assert client._api_key == "valid_api_key"

    def test_instantiation_with_env_variable(self):
        """ClientV2() with JQUANTS_API_KEY env should create instance."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "env_api_key"}, clear=False):
            client = ClientV2()
            assert client._api_key == "env_api_key"

    def test_instantiation_with_toml_config(self):
        """ClientV2() with TOML config should create instance."""
        from jquants import ClientV2

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "jquants-api.toml"
            config_path.write_text('[jquants-api-client]\napi_key = "toml_api_key"\n')
            # Clear env vars and patch cwd
            with patch.dict(os.environ, {}, clear=True):
                with patch("os.path.isfile") as mock_isfile:
                    with patch("builtins.open", create=True) as mock_open:
                        # Mock file reading
                        mock_isfile.side_effect = lambda p: p == "jquants-api.toml"
                        mock_open.return_value.__enter__.return_value.read.return_value = (
                            b'[jquants-api-client]\napi_key = "toml_api_key"\n'
                        )
                        # Use simpler approach: patch _load_config
                        with patch.object(
                            ClientV2,
                            "_load_config",
                            return_value={"api_key": "toml_api_key"},
                        ):
                            client = ClientV2()
                            assert client._api_key == "toml_api_key"

    def test_instantiation_without_config_raises_valueerror(self):
        """ClientV2() without any config should raise ValueError."""
        from jquants import ClientV2

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(ClientV2, "_load_config", return_value={}):
                with pytest.raises(ValueError) as exc_info:
                    ClientV2()
                assert "api_key is required" in str(exc_info.value)

    def test_instantiation_with_empty_string_raises_valueerror(self):
        """ClientV2(api_key="") should raise ValueError."""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="")
        assert "api_key is required" in str(exc_info.value)

    def test_instantiation_with_whitespace_only_raises_valueerror(self):
        """ClientV2(api_key="   ") should raise ValueError after strip."""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="   ")
        assert "api_key is required" in str(exc_info.value)

    def test_instantiation_with_newline_strips_it(self):
        """ClientV2(api_key="key\\n") should strip newline."""
        from jquants import ClientV2

        client = ClientV2(api_key="valid_key\n")
        assert client._api_key == "valid_key"

    def test_instantiation_with_none_and_no_env_raises_valueerror(self):
        """ClientV2(api_key=None) without env should raise ValueError."""
        from jquants import ClientV2

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(ClientV2, "_load_config", return_value={}):
                with pytest.raises(ValueError):
                    ClientV2(api_key=None)

    def test_instantiation_with_env_empty_string_raises_valueerror(self):
        """ClientV2() with JQUANTS_API_KEY="" should raise ValueError."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": ""}, clear=True):
            with patch.object(ClientV2, "_load_config", return_value={}):
                with pytest.raises(ValueError):
                    ClientV2()

    def test_instantiation_with_integer_raises_typeerror(self):
        """ClientV2(api_key=123) should raise TypeError."""
        from jquants import ClientV2

        with pytest.raises(TypeError) as exc_info:
            ClientV2(api_key=123)
        assert "api_key must be a string" in str(exc_info.value)
        assert "int" in str(exc_info.value)


class TestClientV2Priority:
    """Test api_key resolution priority."""

    def test_argument_overrides_env_variable(self):
        """Argument api_key should override JQUANTS_API_KEY env."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "env_key"}, clear=False):
            client = ClientV2(api_key="arg_key")
            assert client._api_key == "arg_key"

    def test_env_variable_overrides_toml(self):
        """JQUANTS_API_KEY should override TOML config."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "env_key"}, clear=False):
            with patch.object(
                ClientV2, "_read_config", return_value={"api_key": "toml_key"}
            ):
                client = ClientV2()
                assert client._api_key == "env_key"

    def test_argument_overrides_all(self):
        """Argument should override both env and TOML."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "env_key"}, clear=False):
            with patch.object(
                ClientV2, "_read_config", return_value={"api_key": "toml_key"}
            ):
                client = ClientV2(api_key="arg_key")
                assert client._api_key == "arg_key"

    def test_cwd_toml_overrides_user_default_toml(self):
        """Current dir TOML should override user default TOML."""
        from jquants import ClientV2

        # Create mock that returns different values based on path
        def mock_read_config(self, path, *, explicit=False):
            if "/.jquants-api/" in path:
                return {"api_key": "user_key"}
            elif path == "jquants-api.toml":
                return {"api_key": "cwd_key"}
            return {}

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(ClientV2, "_read_config", mock_read_config):
                client = ClientV2()
                assert client._api_key == "cwd_key"

    def test_env_file_overrides_cwd_toml(self):
        """JQUANTS_API_CLIENT_CONFIG_FILE should override cwd TOML."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[jquants-api-client]\napi_key = "explicit_key"\n')
            explicit_path = f.name

        try:
            with patch.dict(
                os.environ,
                {"JQUANTS_API_CLIENT_CONFIG_FILE": explicit_path},
                clear=True,
            ):
                # Mock cwd toml to return different key
                original_read_config = ClientV2._read_config

                def mock_read_config(self, path, *, explicit=False):
                    if path == "jquants-api.toml":
                        return {"api_key": "cwd_key"}
                    return original_read_config(self, path, explicit=explicit)

                with patch.object(ClientV2, "_read_config", mock_read_config):
                    client = ClientV2()
                    assert client._api_key == "explicit_key"
        finally:
            os.unlink(explicit_path)

    def test_env_empty_string_overrides_toml(self):
        """Empty JQUANTS_API_KEY should override TOML config and cause ValueError."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": ""}, clear=True):
            with patch.object(
                ClientV2, "_read_config", return_value={"api_key": "toml_key"}
            ):
                # Empty env should override toml, resulting in ValueError
                with pytest.raises(ValueError) as exc_info:
                    ClientV2()
                assert "api_key is required" in str(exc_info.value)


class TestClientV2TOMLImplicit:
    """Test TOML reading in implicit mode (warnings, not errors)."""

    def test_toml_file_not_found_is_ignored(self):
        """Non-existent TOML file should be silently ignored."""
        from jquants import ClientV2

        # Should not raise, just return empty config
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(
                ClientV2, "_load_config", return_value={"api_key": "fallback_key"}
            ):
                client = ClientV2()
                assert client._api_key == "fallback_key"

    def test_invalid_toml_format_warns_and_ignores(self):
        """Invalid TOML format should warn and continue."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid toml {{{")
            invalid_path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = client._read_config(invalid_path, explicit=False)

                # Should return empty dict
                assert result == {}
                # Should have warned
                assert len(w) == 1
                assert "Failed to read config file" in str(w[0].message)
                assert invalid_path in str(w[0].message)
        finally:
            os.unlink(invalid_path)

    def test_permission_error_warns_and_ignores(self):
        """Permission error should warn and continue."""
        from jquants import ClientV2

        client = ClientV2.__new__(ClientV2)
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("os.path.isfile", return_value=True):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    result = client._read_config("/some/path.toml", explicit=False)

                    assert result == {}
                    assert len(w) == 1
                    assert "Failed to read config file" in str(w[0].message)

    def test_missing_section_is_ignored(self):
        """Missing [jquants-api-client] section should return empty dict."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[other-section]\nkey = "value"\n')
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            result = client._read_config(path, explicit=False)
            assert result == {}
        finally:
            os.unlink(path)

    def test_missing_api_key_is_ignored(self):
        """Missing api_key in section should return section without api_key."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[jquants-api-client]\nother_key = "value"\n')
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            result = client._read_config(path, explicit=False)
            # Section exists but no api_key
            assert "api_key" not in result
        finally:
            os.unlink(path)

    def test_api_key_not_string_implicit_warns_and_ignores(self):
        """api_key in implicit TOML that is not string should warn and ignore."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("[jquants-api-client]\napi_key = 12345\n")
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = client._read_config(path, explicit=False)

                # Should return section without api_key (ignored)
                assert "api_key" not in result
                # Should have warned
                assert len(w) == 1
                assert "api_key in config file" in str(w[0].message)
                assert "must be a string" in str(w[0].message)
        finally:
            os.unlink(path)

    def test_api_key_not_string_explicit_raises_typeerror(self):
        """api_key in explicit TOML that is not string should raise TypeError."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("[jquants-api-client]\napi_key = 12345\n")
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            with pytest.raises(TypeError) as exc_info:
                client._read_config(path, explicit=True)
            assert "api_key in config file" in str(exc_info.value)
            assert "must be a string" in str(exc_info.value)
            assert path in str(exc_info.value)  # config_path should be in message
        finally:
            os.unlink(path)

    def test_warning_message_includes_file_path(self):
        """Warning message should include the file path."""
        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid {{{")
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                client._read_config(path, explicit=False)

                assert len(w) == 1
                assert path in str(w[0].message)
        finally:
            os.unlink(path)


class TestClientV2TOMLExplicit:
    """Test TOML reading in explicit mode (fail-fast with errors)."""

    def test_explicit_file_not_found_raises(self):
        """Explicit config file not found should raise FileNotFoundError."""
        from jquants import ClientV2

        client = ClientV2.__new__(ClientV2)
        with pytest.raises(FileNotFoundError):
            client._read_config("/nonexistent/path.toml", explicit=True)

    def test_explicit_permission_error_raises(self):
        """Explicit config with permission error should raise PermissionError."""
        from jquants import ClientV2

        client = ClientV2.__new__(ClientV2)
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("os.path.isfile", return_value=True):
                with pytest.raises(PermissionError):
                    client._read_config("/some/path.toml", explicit=True)

    def test_explicit_invalid_toml_raises(self):
        """Explicit config with invalid TOML should raise TOMLDecodeError."""
        import tomllib

        from jquants import ClientV2

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid {{{")
            path = f.name

        try:
            client = ClientV2.__new__(ClientV2)
            with pytest.raises(tomllib.TOMLDecodeError):
                client._read_config(path, explicit=True)
        finally:
            os.unlink(path)


class TestClientV2Colab:
    """Test Colab environment detection."""

    def test_is_colab_returns_false_normally(self):
        """_is_colab() should return False in normal environment."""
        from jquants import ClientV2

        client = ClientV2.__new__(ClientV2)
        # Ensure google.colab is not in modules
        with patch.dict(sys.modules, {}, clear=False):
            if "google.colab" in sys.modules:
                del sys.modules["google.colab"]
            assert client._is_colab() is False

    def test_is_colab_returns_true_when_colab_module_present(self):
        """_is_colab() should return True when google.colab is in modules."""
        from jquants import ClientV2

        client = ClientV2.__new__(ClientV2)
        mock_colab = MagicMock()
        with patch.dict(sys.modules, {"google.colab": mock_colab}):
            assert client._is_colab() is True

    def test_colab_path_not_read_in_non_colab_env(self):
        """Colab config path should not be read in non-Colab environment."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "test_key"}, clear=True):
            with patch.object(ClientV2, "_read_config") as mock_read:
                mock_read.return_value = {}
                with patch.object(ClientV2, "_is_colab", return_value=False):
                    ClientV2()  # noqa: F841
                    # Check _read_config was not called with Colab path
                    colab_path = (
                        "/content/drive/MyDrive/drive_ws/secret/jquants-api.toml"
                    )
                    for call in mock_read.call_args_list:
                        assert call[0][0] != colab_path


class TestClientV2Headers:
    """Test HTTP header generation."""

    def test_base_headers_contains_api_key(self):
        """_base_headers() should include x-api-key header."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        headers = client._base_headers()
        assert headers["x-api-key"] == "test_api_key"

    def test_base_headers_user_agent_contains_v2(self):
        """_base_headers() User-Agent should contain /v2."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        headers = client._base_headers()
        assert "/v2" in headers["User-Agent"]

    def test_base_headers_user_agent_format(self):
        """_base_headers() User-Agent should follow expected format."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        headers = client._base_headers()
        expected_ua = f"jqapi-python/{__version__}/v2 p/{platform.python_version()}"
        assert headers["User-Agent"] == expected_ua


class TestClientV2HTTPSession:
    """Test HTTP session management."""

    def test_request_session_returns_same_session(self):
        """_request_session() should return the same session on multiple calls."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session1 = client._request_session()
        session2 = client._request_session()
        assert session1 is session2

    def test_retry_strategy_settings(self):
        """Retry strategy should have correct settings."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()

        # Get the adapter for https
        adapter = session.get_adapter("https://example.com")
        retry = adapter.max_retries

        assert retry.total == 3
        assert 429 in retry.status_forcelist
        assert 500 in retry.status_forcelist
        assert 502 in retry.status_forcelist
        assert 503 in retry.status_forcelist
        assert 504 in retry.status_forcelist

    def test_respect_retry_after_header(self):
        """Retry strategy should respect Retry-After header."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")
        retry = adapter.max_retries

        assert retry.respect_retry_after_header is True


class TestClientV2Request:
    """Test HTTP request method."""

    def test_request_constructs_correct_url(self):
        """_request() should construct correct URL."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            client._request("GET", "/equities/bars/daily")

            # Verify URL construction
            call_args = mock_session.request.call_args
            assert call_args[0][1] == "https://api.jquants.com/v2/equities/bars/daily"

    def test_request_includes_timeout(self):
        """_request() should include timeout."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            client._request("GET", "/path")

            call_kwargs = mock_session.request.call_args[1]
            assert call_kwargs["timeout"] == 30

    def test_request_includes_headers(self):
        """_request() should include proper headers."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            client._request("GET", "/path")

            call_kwargs = mock_session.request.call_args[1]
            headers = call_kwargs["headers"]
            assert "x-api-key" in headers
            assert "User-Agent" in headers

    def test_request_returns_response_on_success(self):
        """R001: 200 OK response should not raise exception."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            result = client._request("GET", "/path")
            assert result is mock_response


class TestClientV2Strip:
    """Test strip processing for api_key from all sources."""

    def test_strip_from_argument(self):
        """api_key from argument should be stripped."""
        from jquants import ClientV2

        client = ClientV2(api_key="  key_with_spaces  ")
        assert client._api_key == "key_with_spaces"

    def test_strip_from_env_variable(self):
        """api_key from env variable should be stripped."""
        from jquants import ClientV2

        with patch.dict(os.environ, {"JQUANTS_API_KEY": "  env_key  "}, clear=False):
            with patch.object(ClientV2, "_read_config", return_value={}):
                client = ClientV2()
                assert client._api_key == "env_key"

    def test_strip_from_toml(self):
        """api_key from TOML should be stripped."""
        from jquants import ClientV2

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(
                ClientV2, "_load_config", return_value={"api_key": "  toml_key  "}
            ):
                client = ClientV2()
                assert client._api_key == "toml_key"


class TestClientV2ClassConstants:
    """Test class-level constants."""

    def test_jquants_api_base(self):
        """JQUANTS_API_BASE should be correct."""
        from jquants import ClientV2

        assert ClientV2.JQUANTS_API_BASE == "https://api.jquants.com/v2"

    def test_max_workers(self):
        """MAX_WORKERS should be 5."""
        from jquants import ClientV2

        assert ClientV2.MAX_WORKERS == 5

    def test_user_agent(self):
        """USER_AGENT should be correct."""
        from jquants import ClientV2

        assert ClientV2.USER_AGENT == "jqapi-python"

    def test_raw_encoding(self):
        """RAW_ENCODING should be utf-8."""
        from jquants import ClientV2

        assert ClientV2.RAW_ENCODING == "utf-8"

    def test_request_timeout(self):
        """REQUEST_TIMEOUT should be 30."""
        from jquants import ClientV2

        assert ClientV2.REQUEST_TIMEOUT == 30


class TestClientV2ErrorHandling:
    """Test HTTP error handling and custom exceptions."""

    def _create_mock_response(
        self, status_code: int, text: str = "", json_data: dict | None = None
    ):
        """Helper to create mock response."""
        mock_response = MagicMock()
        mock_response.ok = status_code < 400
        mock_response.status_code = status_code
        mock_response.text = text
        if json_data is not None:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = ValueError("No JSON")
        return mock_response

    def test_403_raises_forbidden_error(self):
        """R003: 403 should raise JQuantsForbiddenError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                403, json_data={"message": "Forbidden"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsForbiddenError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 403

    def test_429_raises_rate_limit_error(self):
        """R004: 429 should raise JQuantsRateLimitError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                429, json_data={"message": "Rate limit exceeded"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsRateLimitError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 429

    def test_400_raises_api_error(self):
        """R005: 400 should raise JQuantsAPIError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                400, json_data={"message": "Bad request"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 400

    def test_500_raises_api_error(self):
        """R006: 500 should raise JQuantsAPIError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                500, json_data={"message": "Internal server error"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 500

    def test_error_extracts_message_from_json(self):
        """R007: Error response JSON message should be extracted."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                400, json_data={"message": "Custom error message"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert "Custom error message" in str(exc_info.value)

    def test_error_handles_non_json_response(self):
        """R008: Non-JSON error response (HTML etc) should still raise exception."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                500, text="<html>Error</html>", json_data=None
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 500

    def test_error_handles_json_list_response(self):
        """R009: JSON list response (not dict) should still raise exception."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 400
            mock_response.text = '["error1", "error2"]'
            mock_response.json.return_value = ["error1", "error2"]
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 400

    def test_non_string_message_field_does_not_crash(self):
        """R019: Non-string message field should not crash error handling."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 400
            # message is a dict, not a string
            mock_response.text = '{"message": {"error": "detail"}}'
            mock_response.json.return_value = {"message": {"error": "detail"}}
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            # Should serialize non-string message to preserve info
            assert exc_info.value.status_code == 400
            assert exc_info.value.response_body == '{"message": {"error": "detail"}}'
            # Exception message should contain serialized message content
            assert "error" in str(exc_info.value)
            assert "detail" in str(exc_info.value)

    def test_error_contains_status_code_and_response_body(self):
        """R010: Exception should contain status_code and response_body."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                400, text='{"message": "Bad"}', json_data={"message": "Bad"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 400
            assert exc_info.value.response_body == '{"message": "Bad"}'

    def test_response_body_truncated_if_too_long(self):
        """R011: response_body should be truncated if exceeds 2048 chars."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        long_text = "x" * 3000

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(500, text=long_text)
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            assert len(exc_info.value.response_body) <= 2048
            assert "truncated" in exc_info.value.response_body

    def test_truncated_response_body_is_exactly_max_length(self):
        """R012: Truncated response_body should be exactly 2048 chars or less."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        # Test with various lengths
        for length in [2048, 2049, 3000, 10000]:
            long_text = "x" * length

            with patch.object(client, "_request_session") as mock_session_method:
                mock_session = MagicMock()
                mock_response = self._create_mock_response(500, text=long_text)
                mock_session.request.return_value = mock_response
                mock_session_method.return_value = mock_session

                with pytest.raises(JQuantsAPIError) as exc_info:
                    client._request("GET", "/path")

                assert len(exc_info.value.response_body) <= 2048

    def test_message_fallback_uses_response_body(self):
        """R013: When message is None, fallback should be response_body (truncated)."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                400, text="Error text", json_data={"other_field": "value"}
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            # Message should fall back to response_body
            assert "Error text" in str(exc_info.value)

    def test_api_message_field_truncated_if_huge(self):
        """R014: API message field should be truncated if huge."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        huge_message = "y" * 5000

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = self._create_mock_response(
                400,
                text=f'{{"message": "{huge_message}"}}',
                json_data={"message": huge_message},
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._request("GET", "/path")

            # The exception message should be truncated
            assert len(str(exc_info.value)) <= 2048


class TestClientV2TruncateResponseBody:
    """Test _truncate_response_body method."""

    def test_short_text_unchanged(self):
        """Text under 2048 chars should be returned unchanged."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        text = "Short text"
        result = client._truncate_response_body(text)
        assert result == text

    def test_exactly_max_length_unchanged(self):
        """Text exactly 2048 chars should be returned unchanged."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        text = "x" * 2048
        result = client._truncate_response_body(text)
        assert result == text
        assert len(result) == 2048

    def test_over_max_length_truncated(self):
        """Text over 2048 chars should be truncated with suffix."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        text = "x" * 3000
        result = client._truncate_response_body(text)
        assert len(result) <= 2048
        assert result.endswith("... (truncated)")

    def test_result_always_under_max_length(self):
        """R015: Result should always be <= 2048 chars even with extreme suffix."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        # Test various lengths
        for length in [2049, 3000, 10000]:
            text = "x" * length
            result = client._truncate_response_body(text)
            assert len(result) <= 2048


class TestClientV2RetrySettings:
    """Test _request_session() retry configuration (S001-S004)."""

    def test_retry_total_is_3(self):
        """S001: Retry.total should be 3."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")

        assert adapter.max_retries.total == 3

    def test_status_forcelist_contains_required_codes(self):
        """S002: status_forcelist should contain 429, 500, 502, 503, 504."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")
        forcelist = adapter.max_retries.status_forcelist

        assert 429 in forcelist
        assert 500 in forcelist
        assert 502 in forcelist
        assert 503 in forcelist
        assert 504 in forcelist

    def test_allowed_methods_includes_get_excludes_post(self):
        """S003: allowed_methods should include GET but exclude POST."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")
        methods = adapter.max_retries.allowed_methods

        assert "GET" in methods
        assert "POST" not in methods

    def test_respect_retry_after_header_is_true(self):
        """S004: respect_retry_after_header should be True."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")

        assert adapter.max_retries.respect_retry_after_header is True

    def test_backoff_factor_is_set(self):
        """S005: backoff_factor should be set for Retry-After fallback."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        session = client._request_session()
        adapter = session.get_adapter("https://example.com")

        # backoff_factor > 0 for exponential backoff when Retry-After is absent
        assert adapter.max_retries.backoff_factor == 0.5


class TestClientV2GetRaw:
    """Test _get_raw() helper method (H001-H002)."""

    def test_returns_raw_json_string(self):
        """H001: _get_raw() should return raw JSON string."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.content = b'{"data": []}'
            mock_request.return_value = mock_response

            result = client._get_raw("/path")

            assert result == '{"data": []}'
            assert isinstance(result, str)

    def test_decodes_as_utf8(self):
        """H002: _get_raw() should decode as UTF-8."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            # Japanese text in UTF-8
            mock_response.content = '{"data": "日本語"}'.encode("utf-8")
            mock_request.return_value = mock_response

            result = client._get_raw("/path")

            assert "日本語" in result


class TestClientV2PaginatedGet:
    """Test _paginated_get() helper method (H003-H011)."""

    def test_single_page_processing(self):
        """H003: _paginated_get() should correctly process single page."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [{"Code": "1301"}],
            }
            mock_request.return_value = mock_response

            result = client._paginated_get("/path")

            assert result == [{"Code": "1301"}]

    def test_multiple_pages_combined(self):
        """H004: _paginated_get() should combine multiple pages."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        responses = [
            {"data": [{"Code": "1301"}], "pagination_key": "key1"},
            {"data": [{"Code": "1302"}], "pagination_key": "key2"},
            {"data": [{"Code": "1303"}]},  # No pagination_key = last page
        ]

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.side_effect = responses
            mock_request.return_value = mock_response

            result = client._paginated_get("/path")

            assert result == [{"Code": "1301"}, {"Code": "1302"}, {"Code": "1303"}]

    def test_stops_when_no_pagination_key(self):
        """H005: _paginated_get() should stop when pagination_key is absent."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"data": [{"Code": "1301"}]}
            mock_request.return_value = mock_response

            client._paginated_get("/path")

            # Should only be called once
            assert mock_request.call_count == 1

    def test_repeated_pagination_key_raises_error(self):
        """H006: _paginated_get() should raise JQuantsAPIError on repeated pagination_key."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        responses = [
            {"data": [{"Code": "1301"}], "pagination_key": "same_key"},
            {"data": [{"Code": "1302"}], "pagination_key": "same_key"},  # Repeated!
        ]

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.side_effect = responses
            mock_response.text = '{"data": []}'
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert "pagination_key repeated" in str(exc_info.value)
            assert exc_info.value.status_code is None

    def test_max_pages_exceeded_raises_error(self):
        """H007: _paginated_get() should raise JQuantsAPIError when max_pages exceeded."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        call_count = 0

        def make_response():
            nonlocal call_count
            call_count += 1
            return {
                "data": [{"Code": str(call_count)}],
                "pagination_key": f"key{call_count}",
            }

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.side_effect = lambda: make_response()
            mock_response.text = '{"data": []}'
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path", max_pages=3)

            assert "max_pages" in str(exc_info.value)
            assert exc_info.value.status_code is None

    def test_non_dict_response_raises_error(self):
        """H008: _paginated_get() should raise JQuantsAPIError when response is not dict."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = ["unexpected", "list"]
            mock_response.text = '["unexpected", "list"]'
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert "expected dict" in str(exc_info.value)
            assert exc_info.value.status_code is None

    def test_non_list_data_raises_error(self):
        """H009: _paginated_get() should raise JQuantsAPIError when data is not list."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"data": "not a list"}
            mock_response.text = '{"data": "not a list"}'
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert "expected list" in str(exc_info.value)
            assert exc_info.value.status_code is None

    def test_all_errors_have_status_code_none(self):
        """H010: All _paginated_get() errors should have status_code=None."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        # Test non-dict response
        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.text = "[]"
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert exc_info.value.status_code is None

    def test_error_message_contains_path(self):
        """H011: Error message should contain the path for debugging."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.text = "[]"
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/equities/master")

            assert "/equities/master" in str(exc_info.value)


class TestClientV2ToDataframe:
    """Test _to_dataframe() helper method (H012-H018)."""

    def test_empty_list_returns_empty_dataframe(self):
        """H012: _to_dataframe() should return empty DataFrame from empty list."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        columns = ["Code", "Date", "Value"]

        result = client._to_dataframe([], columns)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == columns

    def test_column_order_applied(self):
        """H013: _to_dataframe() should apply correct column order."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Value": 100, "Code": "1301", "Date": "2024-01-01"}]
        columns = ["Code", "Date", "Value"]

        result = client._to_dataframe(data, columns)

        assert list(result.columns) == columns

    def test_date_columns_converted_to_timestamp(self):
        """H014: _to_dataframe() should convert date_columns to pd.Timestamp."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "Date": "2024-01-15"}]
        columns = ["Code", "Date"]

        result = client._to_dataframe(data, columns, date_columns=["Date"])

        assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorting_applied(self):
        """H015: _to_dataframe() should apply sorting correctly."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [
            {"Code": "1302", "Date": "2024-01-02"},
            {"Code": "1301", "Date": "2024-01-01"},
        ]
        columns = ["Code", "Date"]

        result = client._to_dataframe(data, columns, sort_columns=["Code", "Date"])

        assert result.iloc[0]["Code"] == "1301"
        assert result.iloc[1]["Code"] == "1302"

    def test_missing_columns_ignored(self):
        """H016: _to_dataframe() should ignore columns not in API response."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "Date": "2024-01-01"}]
        columns = ["Code", "Date", "ExtraColumn"]  # ExtraColumn not in data

        result = client._to_dataframe(data, columns)

        assert "Code" in result.columns
        assert "Date" in result.columns
        assert "ExtraColumn" not in result.columns

    def test_date_columns_none_skips_conversion(self):
        """H017: _to_dataframe() should skip date conversion when date_columns=None."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "Date": "2024-01-15"}]
        columns = ["Code", "Date"]

        result = client._to_dataframe(data, columns, date_columns=None)

        # Date should remain as string
        assert result["Date"].iloc[0] == "2024-01-15"

    def test_sort_columns_none_skips_sorting(self):
        """H018: _to_dataframe() should skip sorting when sort_columns=None."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [
            {"Code": "1302", "Date": "2024-01-02"},
            {"Code": "1301", "Date": "2024-01-01"},
        ]
        columns = ["Code", "Date"]

        result = client._to_dataframe(data, columns, sort_columns=None)

        # Original order should be preserved
        assert result.iloc[0]["Code"] == "1302"
        assert result.iloc[1]["Code"] == "1301"

    def test_date_conversion_failure_raises_exception(self):
        """H019: _to_dataframe() should raise exception on invalid date format."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "Date": "invalid-date-format"}]
        columns = ["Code", "Date"]

        # 方針: pd.to_datetime() の例外をそのまま素通しする
        # pandasのDatetimeParserは ValueError または DateParseError を発生させる
        # （DateParseError は pandas 2.0+ で ValueError のサブクラス）
        with pytest.raises(ValueError):
            client._to_dataframe(data, columns, date_columns=["Date"])


class TestClientV2PaginatedGetJSONDecode:
    """Test _paginated_get() JSON decode failure (H020-H021)."""

    def test_json_decode_failure_raises_jquants_api_error(self):
        """H020: _paginated_get() should raise JQuantsAPIError on JSON decode failure."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Not valid JSON"
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert exc_info.value.status_code is None
            assert (
                "JSON" in str(exc_info.value) or "decode" in str(exc_info.value).lower()
            )

    def test_json_decode_failure_includes_response_body(self):
        """H021: JSON decode failure should include truncated response body."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        long_response = "x" * 3000  # Exceeds RESPONSE_BODY_MAX_LENGTH

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = long_response
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            # response_body should be truncated
            assert exc_info.value.response_body is not None
            assert (
                len(exc_info.value.response_body) <= ClientV2.RESPONSE_BODY_MAX_LENGTH
            )


class TestClientV2PaginatedGetDataKeyMissing:
    """Test _paginated_get() data key missing (H022)."""

    def test_missing_data_key_raises_error(self):
        """H022: _paginated_get() should raise JQuantsAPIError when 'data' key is missing."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            # Valid JSON dict, but no 'data' key
            mock_response.json.return_value = {"other_key": "value"}
            mock_response.text = '{"other_key": "value"}'
            mock_request.return_value = mock_response

            with pytest.raises(JQuantsAPIError) as exc_info:
                client._paginated_get("/path")

            assert exc_info.value.status_code is None
            assert "data" in str(exc_info.value).lower()


class TestClientV2NetworkExceptionsPassthrough:
    """Test that network exceptions are NOT wrapped (R016-R018)."""

    def test_timeout_exception_not_wrapped(self):
        """R016: requests.Timeout should NOT be wrapped in JQuantsAPIError."""
        import requests

        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_session.request.side_effect = requests.Timeout("Connection timed out")
            mock_session_method.return_value = mock_session

            with pytest.raises(requests.Timeout):
                client._request("GET", "/path")

    def test_connection_error_not_wrapped(self):
        """R017: requests.ConnectionError should NOT be wrapped in JQuantsAPIError."""
        import requests

        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_session.request.side_effect = requests.ConnectionError(
                "Connection failed"
            )
            mock_session_method.return_value = mock_session

            with pytest.raises(requests.ConnectionError):
                client._request("GET", "/path")

    def test_ssl_error_not_wrapped(self):
        """R018: requests.SSLError should NOT be wrapped in JQuantsAPIError."""
        import requests

        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_session.request.side_effect = requests.exceptions.SSLError("SSL error")
            mock_session_method.return_value = mock_session

            with pytest.raises(requests.exceptions.SSLError):
                client._request("GET", "/path")


class TestClientV2RateLimitParameters:
    """Test ClientV2 rate limit parameters (CV2-RATE-001~009)."""

    def test_rate_limit_none_defaults_to_5(self):
        """CV2-RATE-001: rate_limit=None → デフォルト5"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=None)
        assert client._rate_limit == 5
        assert client._pacer.interval == pytest.approx(12.0, rel=1e-6)

    def test_rate_limit_120_reflects_setting(self):
        """CV2-RATE-002: rate_limit=120 → 設定反映"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=120)
        assert client._rate_limit == 120
        assert client._pacer.interval == pytest.approx(0.5, rel=1e-6)

    def test_max_workers_default_is_1(self):
        """CV2-RATE-003: max_workers=1 → 直列"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        assert client._max_workers == 1

    def test_max_workers_3_reflects_setting(self):
        """CV2-RATE-004: max_workers=3 → 設定反映"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=3)
        assert client._max_workers == 3

    def test_retry_on_429_default_is_true(self):
        """CV2-RATE-005: retry_on_429=True → リトライ有効"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        assert client._retry_on_429 is True

    def test_retry_on_429_false_reflects_setting(self):
        """CV2-RATE-006: retry_on_429=False → 即例外"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", retry_on_429=False)
        assert client._retry_on_429 is False

    def test_retry_wait_seconds_default_is_310(self):
        """CV2-RATE-007: retry_wait_seconds=310 → デフォルト"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        assert client._retry_wait_seconds == 310

    def test_retry_wait_seconds_600_reflects_setting(self):
        """CV2-RATE-007: retry_wait_seconds=600 → 設定反映"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", retry_wait_seconds=600)
        assert client._retry_wait_seconds == 600

    def test_retry_max_attempts_default_is_3(self):
        """CV2-RATE-008: retry_max_attempts=3 → デフォルト"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        assert client._retry_max_attempts == 3

    def test_retry_max_attempts_5_reflects_setting(self):
        """CV2-RATE-008: retry_max_attempts=5 → 設定反映"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", retry_max_attempts=5)
        assert client._retry_max_attempts == 5

    def test_rate_limit_zero_raises_valueerror(self):
        """CV2-RATE-009: rate_limit=0 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", rate_limit=0)
        assert "rate_limit" in str(exc_info.value).lower()

    def test_rate_limit_negative_raises_valueerror(self):
        """CV2-RATE-009: rate_limit=-1 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", rate_limit=-1)
        assert "rate_limit" in str(exc_info.value).lower()

    def test_max_workers_zero_raises_valueerror(self):
        """CV2-RATE-009: max_workers=0 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", max_workers=0)
        assert "max_workers" in str(exc_info.value).lower()

    def test_max_workers_negative_raises_valueerror(self):
        """CV2-RATE-009: max_workers=-1 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", max_workers=-1)
        assert "max_workers" in str(exc_info.value).lower()

    def test_retry_wait_seconds_zero_raises_valueerror(self):
        """CV2-RATE-009: retry_wait_seconds=0 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", retry_wait_seconds=0)
        assert "retry_wait_seconds" in str(exc_info.value).lower()

    def test_retry_wait_seconds_negative_raises_valueerror(self):
        """CV2-RATE-009: retry_wait_seconds=-1 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", retry_wait_seconds=-1)
        assert "retry_wait_seconds" in str(exc_info.value).lower()

    def test_retry_max_attempts_negative_raises_valueerror(self):
        """CV2-RATE-009: retry_max_attempts=-1 → ValueError"""
        from jquants import ClientV2

        with pytest.raises(ValueError) as exc_info:
            ClientV2(api_key="test_api_key", retry_max_attempts=-1)
        assert "retry_max_attempts" in str(exc_info.value).lower()

    def test_retry_max_attempts_zero_is_valid(self):
        """CV2-RATE-009: retry_max_attempts=0 → 有効（リトライ無効化）"""
        from jquants import ClientV2

        # retry_max_attempts=0 は「リトライしない」を意味するので有効
        client = ClientV2(api_key="test_api_key", retry_max_attempts=0)
        assert client._retry_max_attempts == 0
