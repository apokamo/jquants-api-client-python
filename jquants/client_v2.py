"""J-Quants API V2 Client."""

import json
import os
import platform
import sys
import time
import tomllib
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import date as date_type
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from jquants import __version__, constants_v2
from jquants.exceptions import (
    JQuantsAPIError,
    JQuantsForbiddenError,
    JQuantsRateLimitError,
)
from jquants.pacer import Pacer


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

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit: Optional[int] = None,
        max_workers: int = 1,
        retry_on_429: bool = True,
        retry_wait_seconds: int = 310,
        retry_max_attempts: int = 3,
    ) -> None:
        """
        Initialize ClientV2 with API key authentication.

        Args:
            api_key: J-Quants API key (環境変数 JQUANTS_API_KEY / TOMLでも可)
            rate_limit: 1分あたりの最大リクエスト数 (req/min), None→5(Free)
            max_workers: 並列度, 1=直列
            retry_on_429: 429時リトライするか
            retry_wait_seconds: 429時の待機時間（秒）
            retry_max_attempts: 最大リトライ回数

        Raises:
            ValueError: api_keyが未設定または空文字の場合
            ValueError: rate_limit/max_workers/retry_wait_seconds <= 0 の場合
            ValueError: retry_max_attempts < 0 の場合
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

        # Validate and set rate limit parameters
        effective_rate_limit = rate_limit if rate_limit is not None else 5
        if effective_rate_limit <= 0:
            raise ValueError(f"rate_limit must be positive, got {effective_rate_limit}")
        self._rate_limit = effective_rate_limit

        if max_workers <= 0:
            raise ValueError(f"max_workers must be positive, got {max_workers}")
        self._max_workers = max_workers

        if retry_wait_seconds <= 0:
            raise ValueError(
                f"retry_wait_seconds must be positive, got {retry_wait_seconds}"
            )
        self._retry_wait_seconds = retry_wait_seconds

        if retry_max_attempts < 0:
            raise ValueError(
                f"retry_max_attempts must be non-negative, got {retry_max_attempts}"
            )
        self._retry_max_attempts = retry_max_attempts

        self._retry_on_429 = retry_on_429

        # Initialize Pacer for rate limiting
        self._pacer = Pacer(rate=self._rate_limit)

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
            429 is excluded from status_forcelist to use custom retry logic.
        """
        if self._session is None:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[500, 502, 503, 504],  # 429 excluded for custom retry
                allowed_methods=["HEAD", "GET", "OPTIONS"],  # POST excluded
                backoff_factor=0.5,  # Retry-After無しの場合のbackoff
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(
                pool_connections=self._max_workers + 10,
                pool_maxsize=self._max_workers + 10,
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

        # Close response to release connection back to pool before raising
        response.close()

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
        Send HTTP request with proper headers, timeout, and rate limiting.

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

        # 429 retry loop with rate limiting on each attempt
        for attempt in range(self._retry_max_attempts + 1):
            # Rate limiting: wait before each request (including retries)
            self._pacer.wait()

            response = session.request(
                method,
                url,
                params=params,
                json=json_data,
                headers=self._base_headers(),
                timeout=self.REQUEST_TIMEOUT,
            )

            if response.status_code == 429:
                # Check if retry is disabled or max attempts reached
                is_last_attempt = attempt >= self._retry_max_attempts
                if not self._retry_on_429 or is_last_attempt:
                    self._handle_error_response(response)
                # Close response to release connection back to pool
                response.close()
                # Wait and retry
                time.sleep(self._retry_wait_seconds)
                continue

            if not response.ok:
                self._handle_error_response(response)

            return response

        # Should not reach here, but handle edge case
        raise JQuantsAPIError(
            "Unexpected error: retry loop exited without response",
            status_code=None,
            response_body=None,
        )

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
        ensure_all_columns: bool = False,
    ) -> pd.DataFrame:
        """
        Convert list of dicts to DataFrame with proper formatting.

        Args:
            data: List of dictionaries from API response
            columns: Expected column order (superset; missing columns ignored unless
                     ensure_all_columns=True)
            date_columns: Columns to convert to pd.Timestamp (None = no conversion).
                         Empty strings and None values become pd.NaT.
            sort_columns: Columns to sort by (None = no sorting)
            ensure_all_columns: If True, add missing columns as NaN to ensure
                               all columns from definition are present.

        Returns:
            Formatted pandas DataFrame

        Note:
            Each endpoint wrapper SHOULD explicitly specify date_columns and
            sort_columns for clarity and maintainability.
        """
        if not data:
            # Return empty DataFrame with expected columns and proper dtypes
            df = pd.DataFrame(columns=columns)
            # Ensure date columns have datetime dtype even when empty
            if date_columns:
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            return df

        df = pd.DataFrame(data)

        # Add missing columns and reorder in one operation
        if ensure_all_columns:
            # Use reindex to add missing columns as NaN and reorder
            df = df.reindex(columns=columns)
        else:
            # Reorder columns (only include existing columns)
            existing_columns = [c for c in columns if c in df.columns]
            df = df[existing_columns]

        # Convert date columns (empty string/None/invalid -> NaT)
        if date_columns:
            for col in date_columns:
                if col in df.columns:
                    # Replace empty strings with None first for proper NaT conversion
                    df[col] = df[col].replace("", None)
                    # Use errors="coerce" to handle unexpected formats like "0000-00-00"
                    df[col] = pd.to_datetime(df[col], errors="coerce")

        # Sort
        if sort_columns:
            sort_cols_existing = [c for c in sort_columns if c in df.columns]
            if sort_cols_existing:
                df = df.sort_values(sort_cols_existing).reset_index(drop=True)

        return df

    # =========================================================================
    # Equities - Standard Endpoints
    # =========================================================================

    def get_listed_info(
        self,
        code: str = "",
        date: str = "",
    ) -> pd.DataFrame:
        """
        銘柄マスター情報を取得する。

        Args:
            code: 銘柄コード（省略時: 全銘柄）
            date: 基準日 YYYY-MM-DD or YYYYMMDD（省略時: 最新）

        Returns:
            pd.DataFrame: 銘柄マスター（Code昇順でソート）
        """
        params: dict = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date

        data = self._paginated_get("/equities/master", params)
        return self._to_dataframe(
            data,
            constants_v2.EQUITIES_MASTER_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Code"],
        )

    def get_prices_daily_quotes(
        self,
        code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        株価四本値を取得する。

        Args:
            code: 銘柄コード（4桁: 普通株式のみ）
            date: 日付 YYYY-MM-DD or YYYYMMDD（from/toなし時）
            from_date: 期間開始日
            to_date: 期間終了日

        Returns:
            pd.DataFrame: 株価四本値（Code, Date昇順でソート）

        Raises:
            ValueError: code または date のいずれも指定されていない場合
            ValueError: date と from_date/to_date を同時に指定した場合

        Note:
            code または date のいずれかは必須。
            date と from_date/to_date は排他（同時指定不可）。
        """
        if not code and not date:
            raise ValueError(
                "Either 'code' or 'date' is required for get_prices_daily_quotes()"
            )

        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/equities/bars/daily", params)
        return self._to_dataframe(
            data,
            constants_v2.EQUITIES_BARS_DAILY_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Code", "Date"],
        )

    def get_fins_announcement(self) -> pd.DataFrame:
        """
        決算発表日程を取得する。

        Returns:
            pd.DataFrame: 決算発表日程（Date, Code昇順でソート）
        """
        data = self._paginated_get("/equities/earnings-calendar", {})
        return self._to_dataframe(
            data,
            constants_v2.EQUITIES_EARNINGS_CALENDAR_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )

    def get_price_range(
        self,
        start_dt: Union[str, datetime, date_type],
        end_dt: Optional[Union[str, datetime, date_type]] = None,
    ) -> pd.DataFrame:
        """
        日付範囲で株価四本値を取得する。

        Args:
            start_dt: 開始日（YYYY-MM-DD文字列, date, または datetime）
            end_dt: 終了日（YYYY-MM-DD文字列, date, または datetime。省略時: 今日）

        Returns:
            pd.DataFrame: 株価四本値（Code, Date昇順でソート）

        Raises:
            ValueError: start_dt > end_dt の場合

        Note:
            - 日付文字列は YYYY-MM-DD 形式のみ対応（YYYYMMDD は ValueError）
            - max_workers == 1: 直列取得
            - max_workers > 1: 並列取得（Pacer制御下）
        """
        # Normalize dates to strings
        start_str = self._normalize_date(start_dt)
        if end_dt is None:
            end_str = date_type.today().isoformat()
        else:
            end_str = self._normalize_date(end_dt)

        # Validate date range
        if start_str > end_str:
            raise ValueError(
                f"start_dt ({start_str}) must not be after end_dt ({end_str})"
            )

        # Generate date list
        dates = self._generate_date_range(start_str, end_str)

        # Fetch data
        if self._max_workers == 1:
            # Sequential execution
            dfs = [self.get_prices_daily_quotes(date=d) for d in dates]
        else:
            # Parallel execution with ThreadPoolExecutor
            def fetch_date(d: str) -> pd.DataFrame:
                return self.get_prices_daily_quotes(date=d)

            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                dfs = list(executor.map(fetch_date, dates))

        # Combine results
        if not dfs or all(df.empty for df in dfs):
            return pd.DataFrame(columns=constants_v2.EQUITIES_BARS_DAILY_COLUMNS)

        result = pd.concat(dfs, ignore_index=True)

        # Sort by Code, Date
        sort_cols = [c for c in ["Code", "Date"] if c in result.columns]
        if sort_cols:
            result = result.sort_values(sort_cols).reset_index(drop=True)

        return result

    # =========================================================================
    # Markets endpoints
    # =========================================================================

    def get_markets_trading_calendar(
        self,
        holiday_division: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        取引カレンダーを取得する。

        Args:
            holiday_division: 休日区分（省略時: 全区分）
            from_date: 取得開始日 YYYY-MM-DD
            to_date: 取得終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 取引カレンダー（Date昇順でソート）
        """
        params: dict[str, str] = {}
        if holiday_division:
            params["hol_div"] = holiday_division
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/markets/calendar", params=params)

        return self._to_dataframe(
            data,
            constants_v2.MARKETS_CALENDAR_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date"],
        )

    def get_markets_weekly_margin_interest(
        self,
        code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        信用取引週末残高を取得する。

        Args:
            code: 銘柄コード（省略時: 全銘柄）
            date: 基準日 YYYY-MM-DD
            from_date: 期間開始日 YYYY-MM-DD
            to_date: 期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 信用取引週末残高（Date, Code昇順でソート）

        Raises:
            ValueError: date と from_date/to_date を同時に指定した場合
        """
        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/markets/margin-interest", params=params)

        return self._to_dataframe(
            data,
            constants_v2.MARKETS_MARGIN_INTEREST_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )

    def get_markets_short_selling(
        self,
        sector_33_code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        業種別空売り比率を取得する。

        Note:
            V2 API仕様では `date` または `sector_33_code` のいずれかが必須です。
            `from_date`/`to_date` 単独では使用できません。

        Args:
            sector_33_code: 33業種コード（省略時: 全業種）
            date: 基準日 YYYY-MM-DD
            from_date: 期間開始日 YYYY-MM-DD
            to_date: 期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 業種別空売り比率（Date, S33昇順でソート）

        Raises:
            ValueError: date と from_date/to_date を同時に指定した場合
        """
        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict[str, str] = {}
        if sector_33_code:
            params["s33"] = sector_33_code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/markets/short-ratio", params=params)

        return self._to_dataframe(
            data,
            constants_v2.MARKETS_SHORT_RATIO_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "S33"],
        )

    def get_markets_breakdown(
        self,
        code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        売買内訳データを取得する。

        Args:
            code: 銘柄コード（省略時: 全銘柄）
            date: 基準日 YYYY-MM-DD
            from_date: 期間開始日 YYYY-MM-DD
            to_date: 期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 売買内訳データ（Date, Code昇順でソート）

        Raises:
            ValueError: date と from_date/to_date を同時に指定した場合
        """
        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/markets/breakdown", params=params)

        return self._to_dataframe(
            data,
            constants_v2.MARKETS_BREAKDOWN_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )

    def get_markets_short_selling_positions(
        self,
        code: str = "",
        calc_date: str = "",
        disc_date: str = "",
        disc_date_from: str = "",
        disc_date_to: str = "",
    ) -> pd.DataFrame:
        """
        空売り残高報告を取得する。

        Note:
            V2 API仕様 (https://jpx-jquants.com/ja/spec/mkt-short-sale) では、
            他のMarkets系エンドポイントと異なるパラメータ名が定義されています:
            - calc_date: 算出日（他エンドポイントの date に相当）
            - disc_date: 公表日
            - disc_date_from/disc_date_to: 公表日範囲（他エンドポイントの from/to に相当）

            **重要**: `disc_date_from`/`disc_date_to` を使用する場合は `code` が必須です。

        Args:
            code: 銘柄コード（省略時: 全銘柄）
            calc_date: 算出日 YYYY-MM-DD
            disc_date: 公表日 YYYY-MM-DD
            disc_date_from: 公表日期間開始日 YYYY-MM-DD
            disc_date_to: 公表日期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 空売り残高報告（DiscDate, CalcDate, Code昇順でソート）

        Raises:
            ValueError: disc_date と disc_date_from/disc_date_to を同時に指定した場合
        """
        # disc_date と disc_date_from/disc_date_to は排他
        if disc_date and (disc_date_from or disc_date_to):
            raise ValueError(
                "'disc_date' and 'disc_date_from'/'disc_date_to' are mutually exclusive. "
                "Use 'disc_date' for single day, or 'disc_date_from'/'disc_date_to' for date range."
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if calc_date:
            params["calc_date"] = calc_date
        if disc_date:
            params["disc_date"] = disc_date
        if disc_date_from:
            params["disc_date_from"] = disc_date_from
        if disc_date_to:
            params["disc_date_to"] = disc_date_to

        data = self._paginated_get("/markets/short-sale-report", params=params)

        return self._to_dataframe(
            data,
            constants_v2.MARKETS_SHORT_SALE_REPORT_COLUMNS,
            date_columns=["DiscDate", "CalcDate", "PrevRptDate"],
            sort_columns=["DiscDate", "CalcDate", "Code"],
        )

    def get_markets_daily_margin_interest(
        self,
        code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        信用取引残高（日々公表分）を取得する。

        Note:
            V2 API仕様では `code` または `date` のいずれかが必須です。
            `from_date`/`to_date` を使用する場合は `code` が必須です。

        Args:
            code: 銘柄コード（省略時: 全銘柄）
            date: 基準日 YYYY-MM-DD
            from_date: 期間開始日 YYYY-MM-DD
            to_date: 期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: 信用取引残高（PubDate, Code昇順でソート）

        Raises:
            ValueError: date と from_date/to_date を同時に指定した場合
        """
        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/markets/margin-alert", params=params)

        # Use json_normalize for nested PubReason
        if not data:
            return pd.DataFrame(columns=constants_v2.MARKETS_MARGIN_ALERT_COLUMNS)

        df = pd.json_normalize(data)

        # Apply column order (filter to existing columns)
        cols = [c for c in constants_v2.MARKETS_MARGIN_ALERT_COLUMNS if c in df.columns]
        df = df[cols]

        # Convert date columns
        for col in ["PubDate", "AppDate"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        # Sort
        sort_cols = [c for c in ["PubDate", "Code"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols).reset_index(drop=True)

        return df

    def _normalize_date(
        self,
        dt: Union[str, datetime, date_type],
    ) -> str:
        """Convert date/datetime/string to YYYY-MM-DD string."""
        if isinstance(dt, datetime):
            return dt.date().isoformat()
        elif isinstance(dt, date_type):
            return dt.isoformat()
        else:
            return str(dt)

    def _generate_date_range(self, start: str, end: str) -> list[str]:
        """Generate list of YYYY-MM-DD strings from start to end (inclusive)."""
        from datetime import timedelta

        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current.isoformat())
            current += timedelta(days=1)

        return dates

    # =========================================================================
    # Indices endpoints
    # =========================================================================

    def get_indices(
        self,
        code: str = "",
        date: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        指数四本値を取得する。

        Args:
            code: 指数コード（省略時: 全指数）
            date: 基準日 YYYY-MM-DD or YYYYMMDD
            from_date: 期間開始日
            to_date: 期間終了日

        Returns:
            pd.DataFrame: 指数四本値（Date, Code昇順でソート）

        Raises:
            ValueError: code または date のいずれも指定されていない場合
            ValueError: date と from_date/to_date を同時に指定した場合

        Note:
            公式仕様 (https://jpx-jquants.com/ja/spec/idx-bars-daily) の
            「パラメータ及びレスポンス」セクションに以下の記載があります:
            「データの取得する際には、指数コード（code）または日付（date）の
            指定が必須となります。」
            from/to は code と組み合わせて使用し、単独では使用できません。
            date と from_date/to_date は排他（同時指定不可）。
        """
        if not code and not date:
            raise ValueError("Either 'code' or 'date' is required for get_indices()")

        # date と from_date/to_date は排他
        if date and (from_date or to_date):
            raise ValueError(
                "'date' and 'from_date'/'to_date' are mutually exclusive. "
                "Use 'date' for single day, or 'from_date'/'to_date' for date range."
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/indices/bars/daily", params=params)

        return self._to_dataframe(
            data,
            constants_v2.INDICES_BARS_DAILY_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )

    def get_indices_topix(
        self,
        from_date: str = "",
        to_date: str = "",
    ) -> pd.DataFrame:
        """
        TOPIX指数四本値を取得する。

        Args:
            from_date: 期間開始日 YYYY-MM-DD
            to_date: 期間終了日 YYYY-MM-DD

        Returns:
            pd.DataFrame: TOPIX指数四本値（Date, Code昇順でソート）

        Note:
            パラメータ省略時は全期間データを取得。
        """
        params: dict[str, str] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = self._paginated_get("/indices/bars/daily/topix", params=params)

        return self._to_dataframe(
            data,
            constants_v2.INDICES_BARS_DAILY_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )

    # =========================================================================
    # Financials endpoints
    # =========================================================================

    def get_fins_summary(
        self,
        code: str = "",
        date: str = "",
    ) -> pd.DataFrame:
        """
        決算短信サマリーを取得する。

        Args:
            code: 銘柄コード（4桁または5桁）
            date: 開示日 YYYY-MM-DD or YYYYMMDD

        Returns:
            pd.DataFrame: 決算短信サマリー（DiscDate, DiscTime, Code昇順でソート）

        Raises:
            ValueError: code も date も指定されていない場合

        Note:
            code または date のいずれかは必須（API仕様）。
            全カラムを常に返す（レスポンスに存在しないカラムは NaN）。
        """
        if not code and not date:
            raise ValueError(
                "Either 'code' or 'date' is required for get_fins_summary()"
            )

        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            params["date"] = date

        data = self._paginated_get("/fins/summary", params)
        return self._to_dataframe(
            data,
            constants_v2.FINS_SUMMARY_COLUMNS,
            date_columns=constants_v2.FINS_SUMMARY_DATE_COLUMNS,
            sort_columns=["DiscDate", "DiscTime", "Code"],
            ensure_all_columns=True,
        )

    def get_summary_range(
        self,
        start_dt: Union[str, datetime, date_type],
        end_dt: Optional[Union[str, datetime, date_type]] = None,
    ) -> pd.DataFrame:
        """
        日付範囲で決算短信サマリーを取得する。

        Args:
            start_dt: 開始日（YYYY-MM-DD文字列, date, または datetime）
            end_dt: 終了日（YYYY-MM-DD文字列, date, または datetime。省略時: 今日）

        Returns:
            pd.DataFrame: 決算短信サマリー（DiscDate, DiscTime, Code昇順でソート）

        Raises:
            ValueError: start_dt > end_dt の場合
            ValueError: 日付文字列が YYYYMMDD 形式の場合

        Note:
            - 日付文字列は YYYY-MM-DD 形式のみ対応（YYYYMMDD は ValueError）
            - max_workers == 1: 直列取得
            - max_workers > 1: 並列取得（Pacer制御下）
        """
        # Normalize dates to strings
        start_str = self._normalize_date(start_dt)
        if end_dt is None:
            end_str = date_type.today().isoformat()
        else:
            end_str = self._normalize_date(end_dt)

        # Validate date format FIRST (before range comparison)
        # _generate_date_range will raise ValueError for invalid format like YYYYMMDD
        try:
            dates = self._generate_date_range(start_str, end_str)
        except ValueError as e:
            # Re-raise with clearer message if it's a format error
            if "does not match format" in str(e):
                raise ValueError(
                    f"Invalid date format. Use YYYY-MM-DD, not YYYYMMDD: {e}"
                ) from e
            raise

        # Validate date range (after format validation)
        if start_str > end_str:
            raise ValueError(
                f"start_dt ({start_str}) must not be after end_dt ({end_str})"
            )

        # Fetch data
        if self._max_workers == 1:
            # Sequential execution
            dfs = [self.get_fins_summary(date=d) for d in dates]
        else:
            # Parallel execution with ThreadPoolExecutor
            def fetch_date(d: str) -> pd.DataFrame:
                return self.get_fins_summary(date=d)

            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                dfs = list(executor.map(fetch_date, dates))

        # Combine results (filter empty DataFrames to avoid FutureWarning)
        non_empty_dfs = [df for df in dfs if not df.empty]
        if not non_empty_dfs:
            # Use _to_dataframe to ensure consistent dtype for date columns
            return self._to_dataframe(
                [],
                constants_v2.FINS_SUMMARY_COLUMNS,
                date_columns=constants_v2.FINS_SUMMARY_DATE_COLUMNS,
                ensure_all_columns=True,
            )

        result = pd.concat(non_empty_dfs, ignore_index=True)

        # Ensure all columns are present after concat
        for col in constants_v2.FINS_SUMMARY_COLUMNS:
            if col not in result.columns:
                result[col] = pd.NA

        # Reorder columns
        result = result[constants_v2.FINS_SUMMARY_COLUMNS]

        # Sort by DiscDate, DiscTime, Code
        sort_cols = [c for c in ["DiscDate", "DiscTime", "Code"] if c in result.columns]
        if sort_cols:
            result = result.sort_values(sort_cols).reset_index(drop=True)

        return result
