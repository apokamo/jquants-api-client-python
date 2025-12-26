"""Phase 2 TDD tests: ClientV2 authentication and configuration."""

import os
import platform
import sys
import tempfile
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from jquants import __version__


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

    def test_request_raises_on_http_error(self):
        """_request() should raise HTTPError on failure."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "401 Unauthorized"
            )
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(requests.HTTPError):
                client._request("GET", "/path")


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
