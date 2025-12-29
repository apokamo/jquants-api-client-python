"""Fixtures and configuration for integration tests.

These tests require a valid J-Quants API key.
Set JQUANTS_API_KEY environment variable or use jquants-api.toml config file.

Run integration tests:
    poetry run pytest -m integration tests/

Run only unit tests (exclude integration):
    poetry run pytest -m "not integration" tests/
"""

import os

import pytest

from jquants import ClientV2


def _get_api_key() -> str | None:
    """Get API key from environment variable or TOML config.

    Priority: environment variable > jquants-api.toml
    """
    # 1. Environment variable
    env_key = os.environ.get("JQUANTS_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. TOML config file (same logic as ClientV2)
    try:
        import tomllib

        config_path = "jquants-api.toml"
        if os.path.isfile(config_path):
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            section = config.get("jquants-api-client", {})
            api_key = section.get("api_key")
            if isinstance(api_key, str) and api_key.strip():
                return api_key.strip()
    except Exception:
        pass

    return None


def _has_api_key() -> bool:
    """Check if API key is available."""
    return _get_api_key() is not None


# Skip marker for tests requiring API key
requires_api_key = pytest.mark.skipif(
    not _has_api_key(),
    reason="JQUANTS_API_KEY not set and jquants-api.toml not found",
)


@pytest.fixture(scope="module")
def api_key() -> str:
    """Get API key for tests.

    Raises:
        pytest.skip: If API key is not available
    """
    key = _get_api_key()
    if not key:
        pytest.skip("JQUANTS_API_KEY not set and jquants-api.toml not found")
    return key


@pytest.fixture(scope="module")
def client(api_key: str) -> ClientV2:
    """Create ClientV2 instance with valid API key.

    This fixture creates a single client instance per test module,
    reusing the same session for efficiency.

    Args:
        api_key: Valid J-Quants API key

    Returns:
        ClientV2: Configured client instance
    """
    return ClientV2(api_key=api_key)


@pytest.fixture
def fresh_client(api_key: str) -> ClientV2:
    """Create a fresh ClientV2 instance for each test.

    Use this fixture when testing session state or initialization.

    Args:
        api_key: Valid J-Quants API key

    Returns:
        ClientV2: New client instance
    """
    return ClientV2(api_key=api_key)


@pytest.fixture
def invalid_api_key() -> str:
    """Return an invalid API key for error testing."""
    return "invalid-api-key-for-testing-12345"


@pytest.fixture
def empty_api_key() -> str:
    """Return an empty API key for validation testing."""
    return ""


@pytest.fixture
def whitespace_api_key() -> str:
    """Return a whitespace-only API key for validation testing."""
    return "   \n\t  "
