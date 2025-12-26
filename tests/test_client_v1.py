"""Phase 1 TDD tests: ClientV1 import and deprecation warning."""

import warnings
from unittest.mock import patch


class TestClientV1Import:
    """Test that ClientV1 can be imported from jquants package."""

    def test_import_clientv1_from_jquants(self):
        """from jquants import ClientV1 should work."""
        from jquants import ClientV1

        assert ClientV1 is not None

    def test_import_clientv2_from_jquants(self):
        """from jquants import ClientV2 should work (placeholder for Phase 2)."""
        from jquants import ClientV2

        assert ClientV2 is not None

    def test_jquants_package_has_version(self):
        """jquants package should have __version__ attribute."""
        import jquants

        assert hasattr(jquants, "__version__")


class TestClientV1DeprecationWarning:
    """Test that ClientV1 emits deprecation warning."""

    def test_clientv1_instantiation_emits_deprecation_warning(self):
        """ClientV1 should emit DeprecationWarning when instantiated."""
        from jquants import ClientV1

        # Mock config loading to avoid actual file/env access
        config = {
            "mail_address": "",
            "password": "",
            "refresh_token": "dummy_token",
        }

        with patch.object(ClientV1, "_load_config", return_value=config):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                _client = ClientV1(refresh_token="dummy_token")  # noqa: F841

                # Check that exactly one deprecation warning was raised
                deprecation_warnings = [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                assert len(deprecation_warnings) == 1

                # Check the warning message
                assert "ClientV1" in str(deprecation_warnings[0].message)
                assert "ClientV2" in str(deprecation_warnings[0].message)

    def test_deprecation_warning_message_content(self):
        """Deprecation warning should recommend using ClientV2."""
        from jquants import ClientV1

        config = {
            "mail_address": "",
            "password": "",
            "refresh_token": "dummy_token",
        }

        with patch.object(ClientV1, "_load_config", return_value=config):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                ClientV1(refresh_token="dummy_token")

                warning_message = str(w[0].message)
                assert "deprecated" in warning_message.lower()


class TestBackwardCompatibility:
    """Test backward compatibility with jquantsapi package."""

    def test_jquantsapi_import_still_works(self):
        """import jquantsapi should still work for backward compatibility."""
        import jquantsapi

        assert hasattr(jquantsapi, "Client")
        assert hasattr(jquantsapi, "MARKET_API_SECTIONS")
