"""J-Quants API V2 Client."""

import json
import os
import platform
import sys
import tomllib
import warnings
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from jquants import __version__
from jquants.exceptions import (
    JQuantsAPIError,
    JQuantsForbiddenError,
    JQuantsRateLimitError,
)


class ClientV2:
    """J-Quants API V2 Client using API key authentication."""

    JQUANTS_API_BASE = "https://api.jquants.com/v2"
    MAX_WORKERS = 5
    USER_AGENT = "jqapi-python"
    RAW_ENCODING = "utf-8"
    REQUEST_TIMEOUT = 30  # seconds

    # Response body truncation for exceptions
    RESPONSE_BODY_MAX_LENGTH = 2048
    RESPONSE_BODY_TRUNCATE_SUFFIX = "... (truncated)"

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

        Note:
            POST is excluded from allowed_methods to prevent
            duplicate side effects on retry.
        """
        if self._session is None:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],  # POST excluded
                backoff_factor=0.5,  # Retry-After無しの場合のbackoff
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

    def _truncate_response_body(self, text: str) -> str:
        """
        Truncate response body for exception.

        Ensures the result is strictly <= RESPONSE_BODY_MAX_LENGTH.

        Args:
            text: Response body text

        Returns:
            Original text if under limit, truncated with suffix otherwise
        """
        if len(text) <= self.RESPONSE_BODY_MAX_LENGTH:
            return text
        max_prefix = self.RESPONSE_BODY_MAX_LENGTH - len(
            self.RESPONSE_BODY_TRUNCATE_SUFFIX
        )
        if max_prefix <= 0:
            # Edge case: suffix alone exceeds MAX - truncate suffix itself
            return self.RESPONSE_BODY_TRUNCATE_SUFFIX[: self.RESPONSE_BODY_MAX_LENGTH]
        return text[:max_prefix] + self.RESPONSE_BODY_TRUNCATE_SUFFIX

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Parse error response and raise appropriate exception.

        V2 API error format: {"message": "エラー詳細"}

        Args:
            response: HTTP response with error status

        Raises:
            JQuantsForbiddenError: 403 Forbidden (invalid API key, plan limit, etc.)
            JQuantsRateLimitError: 429 Too Many Requests
            JQuantsAPIError: Other 4xx/5xx errors
        """
        status_code = response.status_code
        response_body = self._truncate_response_body(response.text)

        # Try to extract error message from JSON response
        try:
            error_body = response.json()
            if isinstance(error_body, dict):
                raw_message = error_body.get("message")
                if isinstance(raw_message, str):
                    message = self._truncate_response_body(raw_message)
                elif raw_message is not None:
                    # Non-string message (dict/list/int): serialize to preserve info
                    try:
                        message = self._truncate_response_body(
                            json.dumps(raw_message, ensure_ascii=False)
                        )
                    except (TypeError, ValueError):
                        # Fallback if json.dumps fails (e.g., non-serializable type)
                        message = response_body or f"HTTP {status_code}"
                else:
                    message = response_body or f"HTTP {status_code}"
            else:
                message = response_body or f"HTTP {status_code}"
        except (ValueError, TypeError):
            message = response_body or f"HTTP {status_code}"

        if status_code == 403:
            raise JQuantsForbiddenError(message, status_code, response_body)
        elif status_code == 429:
            raise JQuantsRateLimitError(message, status_code, response_body)
        else:
            raise JQuantsAPIError(message, status_code, response_body)

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
            JQuantsForbiddenError: 403 Forbidden (invalid API key, plan limit, etc.)
            JQuantsRateLimitError: 429 Too Many Requests (after retries exhausted)
            JQuantsAPIError: Other 4xx/5xx errors (after retries exhausted)
            requests.Timeout: Timeout (not wrapped)
            requests.ConnectionError: Connection error (not wrapped)
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

        if not response.ok:
            self._handle_error_response(response)

        return response

    def _get_raw(
        self,
        path: str,
        params: Optional[dict] = None,
    ) -> str:
        """
        Execute GET request and return raw JSON string.

        Args:
            path: API path (e.g., "/equities/master")
            params: Query parameters

        Returns:
            Raw JSON string (UTF-8 encoded)
        """
        response = self._request("GET", path, params=params)
        return response.content.decode(self.RAW_ENCODING)

    def _paginated_get(
        self,
        path: str,
        params: Optional[dict] = None,
        *,
        max_pages: int = 1000,
    ) -> list[dict]:
        """
        Execute GET request with pagination handling.

        V2 API pagination format:
        {"data": [...], "pagination_key": "next_key"}

        Args:
            path: API path
            params: Query parameters (pagination_key will be auto-managed)
            max_pages: Maximum pages to fetch (default: 1000, safety guard)

        Returns:
            Combined data list from all pages

        Raises:
            JQuantsAPIError: If max_pages exceeded, pagination_key repeated,
                            or response shape is invalid (all with status_code=None)
        """
        all_data: list[dict] = []
        current_params = dict(params) if params else {}
        seen_keys: set[str] = set()

        for page in range(max_pages):
            response = self._request("GET", path, params=current_params)

            # Parse JSON (status_code=None: client-side error)
            try:
                result = response.json()
            except (ValueError, TypeError) as e:
                raise JQuantsAPIError(
                    f"JSON decode error: {e} (path={path}, page={page})",
                    status_code=None,
                    response_body=self._truncate_response_body(response.text),
                ) from e

            # Validate response shape (status_code=None: contract violation)
            if not isinstance(result, dict):
                raise JQuantsAPIError(
                    f"Unexpected response type: expected dict, "
                    f"got {type(result).__name__} (path={path}, page={page})",
                    status_code=None,
                    response_body=self._truncate_response_body(response.text),
                )

            # V2 format: data is always in "data" key (required)
            if "data" not in result:
                raise JQuantsAPIError(
                    f"Missing 'data' key in response (path={path}, page={page})",
                    status_code=None,
                    response_body=self._truncate_response_body(response.text),
                )
            data = result["data"]
            if not isinstance(data, list):
                raise JQuantsAPIError(
                    f"Unexpected data type: expected list, "
                    f"got {type(data).__name__} (path={path}, page={page})",
                    status_code=None,
                    response_body=self._truncate_response_body(response.text),
                )
            all_data.extend(data)

            # Check for pagination
            pagination_key = result.get("pagination_key")
            if not pagination_key:
                break

            # Guard against infinite loop (same key returned)
            if pagination_key in seen_keys:
                raise JQuantsAPIError(
                    f"pagination_key repeated: {pagination_key} "
                    f"(path={path}, page={page}). This may indicate an API issue.",
                    status_code=None,
                    response_body=None,
                )
            seen_keys.add(pagination_key)

            current_params["pagination_key"] = pagination_key
        else:
            # page == max_pages - 1 at this point (loop exhausted)
            last_page = max_pages - 1
            raise JQuantsAPIError(
                f"Pagination exceeded max_pages={max_pages} "
                f"(path={path}, page={last_page}). "
                "This may indicate an API issue or infinite loop.",
                status_code=None,
                response_body=None,
            )

        return all_data

    def _to_dataframe(
        self,
        data: list[dict],
        columns: list[str],
        *,
        date_columns: list[str] | None = None,
        sort_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Convert list of dicts to DataFrame with proper formatting.

        Args:
            data: List of dictionaries from API response
            columns: Expected column order (superset; missing columns ignored)
            date_columns: Columns to convert to pd.Timestamp (None = no conversion)
            sort_columns: Columns to sort by (None = no sorting)

        Returns:
            Formatted pandas DataFrame

        Note:
            Each endpoint wrapper SHOULD explicitly specify date_columns and
            sort_columns for clarity and maintainability.
        """
        if not data:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data)

        # Reorder columns (only include existing columns)
        existing_columns = [c for c in columns if c in df.columns]
        df = df[existing_columns]

        # Convert date columns
        if date_columns:
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

        # Sort
        if sort_columns:
            sort_cols_existing = [c for c in sort_columns if c in df.columns]
            if sort_cols_existing:
                df = df.sort_values(sort_cols_existing).reset_index(drop=True)

        return df
