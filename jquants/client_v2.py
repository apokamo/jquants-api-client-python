"""J-Quants API V2 Client."""

import os
import platform
import sys
import tomllib
import warnings
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from jquants import __version__


class ClientV2:
    """J-Quants API V2 Client using API key authentication."""

    JQUANTS_API_BASE = "https://api.jquants.com/v2"
    MAX_WORKERS = 5
    USER_AGENT = "jqapi-python"
    RAW_ENCODING = "utf-8"
    REQUEST_TIMEOUT = 30  # seconds

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize ClientV2 with API key authentication.

        Args:
            api_key: J-Quants API key (環境変数 JQUANTS_API_KEY / TOMLでも可)

        Raises:
            ValueError: api_keyが未設定または空文字の場合
            TypeError: api_keyが文字列以外の場合
        """
        config = self._load_config()

        # Get api_key from config or argument
        self._api_key = config.get("api_key", "")

        if api_key is not None:
            if not isinstance(api_key, str):
                raise TypeError(
                    f"api_key must be a string, got {type(api_key).__name__}"
                )
            self._api_key = api_key

        # Strip whitespace and newlines from all sources
        if isinstance(self._api_key, str):
            self._api_key = self._api_key.strip()

        if not self._api_key:
            raise ValueError(
                "api_key is required. Set api_key parameter, "
                "JQUANTS_API_KEY environment variable, or api_key in config file."
            )

        self._session: Optional[requests.Session] = None

    def _is_colab(self) -> bool:
        """Return True if running in Google Colab."""
        return "google.colab" in sys.modules

    def _read_config(self, config_path: str, *, explicit: bool = False) -> dict:
        """
        Read config from TOML file.

        Args:
            config_path: Path to TOML file
            explicit: If True, raise on any error (fail-fast for explicit paths)

        Returns:
            dict: Config section or empty dict if not found/invalid
        """
        try:
            if not os.path.isfile(config_path):
                if explicit:
                    raise FileNotFoundError(f"Config file not found: {config_path}")
                return {}

            with open(config_path, mode="rb") as f:
                ret = tomllib.load(f)

        except FileNotFoundError:
            if explicit:
                raise
            return {}
        except (PermissionError, OSError, tomllib.TOMLDecodeError) as e:
            if explicit:
                raise
            warnings.warn(
                f"Failed to read config file '{config_path}': {e}. Ignoring this file.",
                UserWarning,
                stacklevel=3,
            )
            return {}

        if "jquants-api-client" not in ret:
            return {}

        section = ret["jquants-api-client"]
        if "api_key" in section:
            if not isinstance(section["api_key"], str):
                if explicit:
                    raise TypeError(
                        f"api_key in config file '{config_path}' must be a string, "
                        f"got {type(section['api_key']).__name__}"
                    )
                # implicit: warn and ignore invalid type
                warnings.warn(
                    f"api_key in config file '{config_path}' must be a string, "
                    f"got {type(section['api_key']).__name__}. Ignoring this value.",
                    UserWarning,
                    stacklevel=3,
                )
                del section["api_key"]
        return section

    def _load_config(self) -> dict:
        """
        Load configuration from multiple sources with priority.

        Priority (later wins): Colab -> user -> cwd -> env_file -> env

        Returns:
            dict: Merged configuration
        """
        config: dict = {}

        # 1. Colab config (implicit)
        if self._is_colab():
            colab_path = "/content/drive/MyDrive/drive_ws/secret/jquants-api.toml"
            config = {**config, **self._read_config(colab_path, explicit=False)}

        # 2. User default config (implicit)
        user_path = f"{Path.home()}/.jquants-api/jquants-api.toml"
        config = {**config, **self._read_config(user_path, explicit=False)}

        # 3. Current dir config (implicit)
        config = {**config, **self._read_config("jquants-api.toml", explicit=False)}

        # 4. Env specified config (explicit - fail-fast on error)
        if "JQUANTS_API_CLIENT_CONFIG_FILE" in os.environ:
            env_path = os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]
            config = {**config, **self._read_config(env_path, explicit=True)}

        # 5. Environment variable (overrides lower priority sources, even if empty)
        if "JQUANTS_API_KEY" in os.environ:
            config["api_key"] = os.environ["JQUANTS_API_KEY"]

        return config

    def _base_headers(self) -> dict:
        """
        Generate base headers for API requests.

        Returns:
            dict: Headers including x-api-key and User-Agent
        """
        return {
            "x-api-key": self._api_key,
            "User-Agent": (
                f"{self.USER_AGENT}/{__version__}/v2 p/{platform.python_version()}"
            ),
        }

    def _request_session(self) -> requests.Session:
        """
        Get or create HTTP session with retry strategy.

        Returns:
            requests.Session: Configured session with retry
        """
        if self._session is None:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(
                pool_connections=self.MAX_WORKERS + 10,
                pool_maxsize=self.MAX_WORKERS + 10,
                max_retries=retry_strategy,
            )
            self._session = requests.Session()
            self._session.mount("https://", adapter)
        return self._session

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> requests.Response:
        """
        Send HTTP request with proper headers and timeout.

        Args:
            method: HTTP method ("GET" or "POST")
            path: API path (e.g., "/equities/bars/daily")
            params: Query parameters
            json_data: JSON body for POST requests

        Returns:
            requests.Response

        Raises:
            requests.HTTPError: On 4xx/5xx responses (after retries)
        """
        url = f"{self.JQUANTS_API_BASE}{path}"
        session = self._request_session()

        response = session.request(
            method,
            url,
            params=params,
            json=json_data,
            headers=self._base_headers(),
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response
