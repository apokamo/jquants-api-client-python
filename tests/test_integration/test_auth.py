"""AUTH: Authentication and configuration loading tests.

Test IDs: AUTH-001 through AUTH-011
See Issue #10 for test case specifications.
"""

import os
import tempfile
from pathlib import Path

import pytest

from jquants import ClientV2

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAuthNormal:
    """Normal authentication test cases."""

    def test_auth_001_valid_api_key_init(self, api_key: str) -> None:
        """AUTH-001: Valid API key initialization succeeds without exception."""
        client = ClientV2(api_key=api_key)
        assert client is not None
        assert client._api_key == api_key

    def test_auth_002_env_var_api_key(self, api_key: str) -> None:
        """AUTH-002: API key from JQUANTS_API_KEY environment variable."""
        # Temporarily set environment variable
        original = os.environ.get("JQUANTS_API_KEY")
        try:
            os.environ["JQUANTS_API_KEY"] = api_key
            client = ClientV2()
            assert client._api_key == api_key
        finally:
            if original is not None:
                os.environ["JQUANTS_API_KEY"] = original
            elif "JQUANTS_API_KEY" in os.environ:
                del os.environ["JQUANTS_API_KEY"]

    def test_auth_003_toml_file_api_key(self, api_key: str) -> None:
        """AUTH-003: API key from jquants-api.toml config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "jquants-api.toml"
            config_path.write_text(
                f'[jquants-api-client]\napi_key = "{api_key}"\n',
                encoding="utf-8",
            )

            # Remove env var to test TOML loading
            original = os.environ.get("JQUANTS_API_KEY")
            original_config = os.environ.get("JQUANTS_API_CLIENT_CONFIG_FILE")
            try:
                if "JQUANTS_API_KEY" in os.environ:
                    del os.environ["JQUANTS_API_KEY"]
                os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = str(config_path)
                client = ClientV2()
                assert client._api_key == api_key
            finally:
                if original is not None:
                    os.environ["JQUANTS_API_KEY"] = original
                elif "JQUANTS_API_KEY" in os.environ:
                    del os.environ["JQUANTS_API_KEY"]
                if original_config is not None:
                    os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = original_config
                elif "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
                    del os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]

    def test_auth_004_invalid_api_key_403(self, invalid_api_key: str) -> None:
        """AUTH-004: Invalid API key raises JQuantsForbiddenError.

        Note: V2 API returns 403 (not 401) for invalid API keys.
        See: https://jpx-jquants.com/ja/spec/response-status
        """
        from jquants.exceptions import JQuantsForbiddenError

        client = ClientV2(api_key=invalid_api_key)
        with pytest.raises(JQuantsForbiddenError) as exc_info:
            client._request("GET", "/equities/master")
        assert exc_info.value.status_code == 403

    def test_auth_005_empty_api_key_value_error(self, empty_api_key: str) -> None:
        """AUTH-005: Empty API key raises ValueError."""
        original = os.environ.get("JQUANTS_API_KEY")
        try:
            if "JQUANTS_API_KEY" in os.environ:
                del os.environ["JQUANTS_API_KEY"]
            with pytest.raises(ValueError) as exc_info:
                ClientV2(api_key=empty_api_key)
            assert "api_key is required" in str(exc_info.value)
        finally:
            if original is not None:
                os.environ["JQUANTS_API_KEY"] = original


class TestAuthRare:
    """Rare/edge case authentication tests."""

    def test_auth_006_whitespace_api_key_stripped(self, api_key: str) -> None:
        """AUTH-006: Leading/trailing whitespace is stripped from API key."""
        padded_key = f"  {api_key}  "
        client = ClientV2(api_key=padded_key)
        assert client._api_key == api_key
        assert client._api_key == api_key.strip()

    def test_auth_007_newline_api_key_stripped(self, api_key: str) -> None:
        """AUTH-007: Newlines are stripped from API key (TOML trailing newline)."""
        newline_key = f"{api_key}\n"
        client = ClientV2(api_key=newline_key)
        assert client._api_key == api_key
        assert "\n" not in client._api_key

    def test_auth_008_env_var_overrides_toml(self, api_key: str) -> None:
        """AUTH-008: Environment variable takes priority over TOML config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "jquants-api.toml"
            config_path.write_text(
                '[jquants-api-client]\napi_key = "toml-key-should-be-overridden"\n',
                encoding="utf-8",
            )

            original = os.environ.get("JQUANTS_API_KEY")
            original_config = os.environ.get("JQUANTS_API_CLIENT_CONFIG_FILE")
            try:
                os.environ["JQUANTS_API_KEY"] = api_key
                os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = str(config_path)
                client = ClientV2()
                # Environment variable should win
                assert client._api_key == api_key
                assert client._api_key != "toml-key-should-be-overridden"
            finally:
                if original is not None:
                    os.environ["JQUANTS_API_KEY"] = original
                elif "JQUANTS_API_KEY" in os.environ:
                    del os.environ["JQUANTS_API_KEY"]
                if original_config is not None:
                    os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = original_config
                elif "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
                    del os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]

    def test_auth_009_explicit_config_file_not_found(self) -> None:
        """AUTH-009: Explicit config path raises FileNotFoundError when missing."""
        original = os.environ.get("JQUANTS_API_KEY")
        original_config = os.environ.get("JQUANTS_API_CLIENT_CONFIG_FILE")
        try:
            if "JQUANTS_API_KEY" in os.environ:
                del os.environ["JQUANTS_API_KEY"]
            os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = "/nonexistent/path.toml"
            with pytest.raises(FileNotFoundError):
                ClientV2()
        finally:
            if original is not None:
                os.environ["JQUANTS_API_KEY"] = original
            elif "JQUANTS_API_KEY" in os.environ:
                del os.environ["JQUANTS_API_KEY"]
            if original_config is not None:
                os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = original_config
            elif "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
                del os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]

    def test_auth_010_toml_syntax_error_warning(self, api_key: str) -> None:
        """AUTH-010: TOML syntax error in implicit path triggers warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create malformed TOML
            config_path = Path(tmpdir) / "jquants-api.toml"
            config_path.write_text("invalid toml syntax [[[", encoding="utf-8")

            original = os.environ.get("JQUANTS_API_KEY")
            original_config = os.environ.get("JQUANTS_API_CLIENT_CONFIG_FILE")
            original_cwd = os.getcwd()
            try:
                os.environ["JQUANTS_API_KEY"] = api_key
                if "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
                    del os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]
                os.chdir(tmpdir)

                # Should warn but not fail (env var provides key)
                with pytest.warns(UserWarning, match="Failed to read config file"):
                    client = ClientV2()
                assert client._api_key == api_key
            finally:
                os.chdir(original_cwd)
                if original is not None:
                    os.environ["JQUANTS_API_KEY"] = original
                elif "JQUANTS_API_KEY" in os.environ:
                    del os.environ["JQUANTS_API_KEY"]
                if original_config is not None:
                    os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = original_config

    def test_auth_011_non_string_api_key_warning(self, api_key: str) -> None:
        """AUTH-011: Non-string api_key in TOML triggers warning and is ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TOML with integer api_key
            config_path = Path(tmpdir) / "jquants-api.toml"
            config_path.write_text(
                "[jquants-api-client]\napi_key = 12345\n",
                encoding="utf-8",
            )

            original = os.environ.get("JQUANTS_API_KEY")
            original_config = os.environ.get("JQUANTS_API_CLIENT_CONFIG_FILE")
            original_cwd = os.getcwd()
            try:
                os.environ["JQUANTS_API_KEY"] = api_key
                if "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
                    del os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]
                os.chdir(tmpdir)

                # Should warn about non-string type but use env var
                with pytest.warns(UserWarning, match="must be a string"):
                    client = ClientV2()
                assert client._api_key == api_key
            finally:
                os.chdir(original_cwd)
                if original is not None:
                    os.environ["JQUANTS_API_KEY"] = original
                elif "JQUANTS_API_KEY" in os.environ:
                    del os.environ["JQUANTS_API_KEY"]
                if original_config is not None:
                    os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"] = original_config
