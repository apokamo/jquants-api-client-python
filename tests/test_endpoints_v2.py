"""Sub-Phase 3.2 TDD tests: Equities-Standard endpoints.

Tests for:
- get_listed_info()
- get_prices_daily_quotes()
- get_fins_announcement()
- get_price_range()
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from jquants import ClientV2
from jquants.constants_v2 import (
    EQUITIES_BARS_DAILY_COLUMNS,
    EQUITIES_EARNINGS_CALENDAR_COLUMNS,
    EQUITIES_MASTER_COLUMNS,
)


class TestGetListedInfo:
    """Test get_listed_info() - /v2/equities/master."""

    def test_returns_dataframe(self):
        """EP-LI-001: get_listed_info() should return pd.DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-15", "Code": "1301", "CoName": "Test Corp"}
            ]

            result = client.get_listed_info()

            assert isinstance(result, pd.DataFrame)

    def test_no_params_calls_api_without_query(self):
        """EP-LI-002: get_listed_info() without args should call API without params."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_listed_info()

            mock_get.assert_called_once_with("/equities/master", {})

    def test_code_param_passed_to_api(self):
        """EP-LI-003: get_listed_info(code='1301') should pass code param."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_listed_info(code="1301")

            mock_get.assert_called_once_with("/equities/master", {"code": "1301"})

    def test_date_param_passed_to_api(self):
        """EP-LI-004: get_listed_info(date='2024-01-15') should pass date param."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_listed_info(date="2024-01-15")

            mock_get.assert_called_once_with("/equities/master", {"date": "2024-01-15"})

    def test_code_and_date_params_passed_to_api(self):
        """EP-LI-005: Both code and date params should be passed."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_listed_info(code="1301", date="2024-01-15")

            mock_get.assert_called_once_with(
                "/equities/master", {"code": "1301", "date": "2024-01-15"}
            )

    def test_date_column_converted_to_timestamp(self):
        """EP-LI-006: Date column should be pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Date": "2024-01-15", "Code": "1301"}]

            result = client.get_listed_info()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_code(self):
        """EP-LI-007: Result should be sorted by Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-15", "Code": "1302"},
                {"Date": "2024-01-15", "Code": "1301"},
                {"Date": "2024-01-15", "Code": "1303"},
            ]

            result = client.get_listed_info()

            assert result.iloc[0]["Code"] == "1301"
            assert result.iloc[1]["Code"] == "1302"
            assert result.iloc[2]["Code"] == "1303"

    def test_empty_response_returns_empty_dataframe(self):
        """EP-LI-008: Empty response should return empty DataFrame with columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_listed_info()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == EQUITIES_MASTER_COLUMNS

    def test_column_order_matches_constants(self):
        """EP-LI-009: Column order should match EQUITIES_MASTER_COLUMNS."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Response with columns in different order
            mock_get.return_value = [
                {
                    "Code": "1301",
                    "Date": "2024-01-15",
                    "CoName": "Test",
                    "CoNameEn": "Test En",
                    "S17": "01",
                    "S17Nm": "S17 Name",
                    "S33": "01",
                    "S33Nm": "S33 Name",
                    "ScaleCat": "1",
                    "Mkt": "1",
                    "MktNm": "Market",
                    "Mrgn": "1",
                    "MrgnNm": "Credit",
                }
            ]

            result = client.get_listed_info()

            # Only check existing columns (Premium columns may be absent)
            expected_cols = [c for c in EQUITIES_MASTER_COLUMNS if c in result.columns]
            assert list(result.columns) == expected_cols

    def test_premium_columns_optional(self):
        """EP-LI-010: Premium columns (Mrgn, MrgnNm) should be optional."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Response without Mrgn and MrgnNm
            mock_get.return_value = [
                {
                    "Date": "2024-01-15",
                    "Code": "1301",
                    "CoName": "Test",
                    "CoNameEn": "Test En",
                    "S17": "01",
                    "S17Nm": "S17 Name",
                    "S33": "01",
                    "S33Nm": "S33 Name",
                    "ScaleCat": "1",
                    "Mkt": "1",
                    "MktNm": "Market",
                }
            ]

            result = client.get_listed_info()

            # Should succeed without Premium columns
            assert "Code" in result.columns
            assert "Mrgn" not in result.columns
            assert "MrgnNm" not in result.columns


class TestGetPricesDailyQuotes:
    """Test get_prices_daily_quotes() - /v2/equities/bars/daily."""

    def test_returns_dataframe(self):
        """EP-PD-001: get_prices_daily_quotes() should return pd.DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Date": "2024-01-15", "Code": "1301", "O": 100}]

            result = client.get_prices_daily_quotes(code="1301")

            assert isinstance(result, pd.DataFrame)

    def test_code_param_passed_to_api(self):
        """EP-PD-002: code param should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_prices_daily_quotes(code="1301")

            mock_get.assert_called_once_with("/equities/bars/daily", {"code": "1301"})

    def test_date_param_passed_to_api(self):
        """EP-PD-003: date param should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_prices_daily_quotes(date="2024-01-15")

            mock_get.assert_called_once_with(
                "/equities/bars/daily", {"date": "2024-01-15"}
            )

    def test_from_to_params_passed_to_api(self):
        """EP-PD-004: from/to params should be passed as from/to."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_prices_daily_quotes(
                code="1301", from_date="2024-01-01", to_date="2024-01-31"
            )

            mock_get.assert_called_once_with(
                "/equities/bars/daily",
                {"code": "1301", "from": "2024-01-01", "to": "2024-01-31"},
            )

    def test_no_params_raises_valueerror(self):
        """EP-PD-005: No params should raise ValueError (API requires code or date)."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_prices_daily_quotes()

        assert (
            "code" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        )

    def test_date_and_from_date_mutually_exclusive(self):
        """EP-PD-005b: date and from_date are mutually exclusive."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_prices_daily_quotes(
                code="1301", date="2024-01-15", from_date="2024-01-01"
            )

        assert "mutually exclusive" in str(exc_info.value).lower()

    def test_date_and_to_date_mutually_exclusive(self):
        """EP-PD-005c: date and to_date are mutually exclusive."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_prices_daily_quotes(
                code="1301", date="2024-01-15", to_date="2024-01-31"
            )

        assert "mutually exclusive" in str(exc_info.value).lower()

    def test_date_column_converted_to_timestamp(self):
        """EP-PD-006: Date column should be pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Date": "2024-01-15", "Code": "1301", "O": 100}]

            result = client.get_prices_daily_quotes(code="1301")

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_code_and_date(self):
        """EP-PD-007: Result should be sorted by Code, Date ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-16", "Code": "1301", "O": 100},
                {"Date": "2024-01-15", "Code": "1302", "O": 100},
                {"Date": "2024-01-15", "Code": "1301", "O": 100},
            ]

            result = client.get_prices_daily_quotes(date="2024-01-15")

            assert result.iloc[0]["Code"] == "1301"
            assert result.iloc[0]["Date"] == pd.Timestamp("2024-01-15")
            assert result.iloc[1]["Code"] == "1301"
            assert result.iloc[1]["Date"] == pd.Timestamp("2024-01-16")
            assert result.iloc[2]["Code"] == "1302"

    def test_empty_response_returns_empty_dataframe(self):
        """EP-PD-008: Empty response should return empty DataFrame with columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_prices_daily_quotes(code="1301")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == EQUITIES_BARS_DAILY_COLUMNS

    def test_column_order_matches_constants(self):
        """EP-PD-009: Column order should match EQUITIES_BARS_DAILY_COLUMNS."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Standard columns only
            mock_get.return_value = [
                {
                    "Code": "1301",
                    "Date": "2024-01-15",
                    "O": 100,
                    "H": 110,
                    "L": 90,
                    "C": 105,
                    "UL": 0,
                    "LL": 0,
                    "Vo": 1000,
                    "Va": 100000,
                    "AdjFactor": 1.0,
                    "AdjO": 100,
                    "AdjH": 110,
                    "AdjL": 90,
                    "AdjC": 105,
                    "AdjVo": 1000,
                }
            ]

            result = client.get_prices_daily_quotes(code="1301")

            # Only check existing columns
            expected_cols = [
                c for c in EQUITIES_BARS_DAILY_COLUMNS if c in result.columns
            ]
            assert list(result.columns) == expected_cols

    def test_premium_columns_optional(self):
        """EP-PD-010: Premium columns (MO, MH, etc.) should be optional."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Standard columns only, no Premium columns
            mock_get.return_value = [
                {
                    "Date": "2024-01-15",
                    "Code": "1301",
                    "O": 100,
                    "H": 110,
                    "L": 90,
                    "C": 105,
                }
            ]

            result = client.get_prices_daily_quotes(code="1301")

            # Should succeed without Premium columns
            assert "Code" in result.columns
            assert "MO" not in result.columns
            assert "AO" not in result.columns


class TestGetFinsAnnouncement:
    """Test get_fins_announcement() - /v2/equities/earnings-calendar."""

    def test_returns_dataframe(self):
        """EP-FA-001: get_fins_announcement() should return pd.DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Date": "2024-01-15", "Code": "1301"}]

            result = client.get_fins_announcement()

            assert isinstance(result, pd.DataFrame)

    def test_no_params_calls_api(self):
        """EP-FA-002: get_fins_announcement() should call API without params."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_fins_announcement()

            mock_get.assert_called_once_with("/equities/earnings-calendar", {})

    def test_date_column_converted_to_timestamp(self):
        """EP-FA-003: Date column should be pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Date": "2024-01-15", "Code": "1301"}]

            result = client.get_fins_announcement()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_and_code(self):
        """EP-FA-004: Result should be sorted by Date, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-16", "Code": "1301"},
                {"Date": "2024-01-15", "Code": "1302"},
                {"Date": "2024-01-15", "Code": "1301"},
            ]

            result = client.get_fins_announcement()

            assert result.iloc[0]["Date"] == pd.Timestamp("2024-01-15")
            assert result.iloc[0]["Code"] == "1301"
            assert result.iloc[1]["Date"] == pd.Timestamp("2024-01-15")
            assert result.iloc[1]["Code"] == "1302"
            assert result.iloc[2]["Date"] == pd.Timestamp("2024-01-16")
            assert result.iloc[2]["Code"] == "1301"

    def test_empty_response_returns_empty_dataframe(self):
        """EP-FA-005: Empty response should return empty DataFrame with columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_fins_announcement()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == EQUITIES_EARNINGS_CALENDAR_COLUMNS

    def test_column_order_matches_constants(self):
        """EP-FA-006: Column order should match EQUITIES_EARNINGS_CALENDAR_COLUMNS."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Code": "1301",
                    "Date": "2024-01-15",
                    "CoName": "Test Corp",
                    "FY": "2024",
                    "SectorNm": "Foods",
                    "FQ": "1Q",
                    "Section": "TSE Prime",
                }
            ]

            result = client.get_fins_announcement()

            expected_cols = [
                c for c in EQUITIES_EARNINGS_CALENDAR_COLUMNS if c in result.columns
            ]
            assert list(result.columns) == expected_cols


class TestGetPriceRange:
    """Test get_price_range() - parallel daily quotes fetcher."""

    def test_returns_dataframe(self):
        """EP-PR-001: get_price_range() should return pd.DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame(
                {"Date": [pd.Timestamp("2024-01-15")], "Code": ["1301"], "O": [100]}
            )

            result = client.get_price_range(start_dt="2024-01-15")

            assert isinstance(result, pd.DataFrame)

    def test_single_day_calls_get_prices_daily_quotes(self):
        """EP-PR-002: Single day range should call get_prices_daily_quotes once."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame()

            client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-15")

            mock_get.assert_called_once_with(date="2024-01-15")

    def test_multi_day_calls_for_each_day(self):
        """EP-PR-003: Multi-day range should call for each day."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame()

            client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-17")

            # Should be called for 15, 16, 17
            assert mock_get.call_count == 3

    def test_default_end_dt_is_today(self):
        """EP-PR-004: end_dt=None should default to today."""
        client = ClientV2(api_key="test_api_key")
        today = date.today().isoformat()

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame()

            client.get_price_range(start_dt=today)

            mock_get.assert_called_once_with(date=today)

    def test_sorted_by_code_and_date(self):
        """EP-PR-005: Result should be sorted by Code, Date ascending."""
        client = ClientV2(api_key="test_api_key")

        df1 = pd.DataFrame(
            {"Date": [pd.Timestamp("2024-01-15")], "Code": ["1302"], "O": [100]}
        )
        df2 = pd.DataFrame(
            {"Date": [pd.Timestamp("2024-01-16")], "Code": ["1301"], "O": [100]}
        )

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.side_effect = [df1, df2]

            result = client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-16")

            assert result.iloc[0]["Code"] == "1301"
            assert result.iloc[1]["Code"] == "1302"

    def test_empty_range_returns_empty_dataframe(self):
        """EP-PR-006: Empty range should return empty DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame(columns=EQUITIES_BARS_DAILY_COLUMNS)

            result = client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-15")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_accepts_datetime_objects(self):
        """EP-PR-007: Should accept datetime objects for start_dt/end_dt."""
        client = ClientV2(api_key="test_api_key")
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 15)

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame()

            client.get_price_range(start_dt=start, end_dt=end)

            mock_get.assert_called_once_with(date="2024-01-15")

    def test_accepts_date_objects(self):
        """EP-PR-008: Should accept date objects for start_dt/end_dt."""
        client = ClientV2(api_key="test_api_key")
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.return_value = pd.DataFrame()

            client.get_price_range(start_dt=start, end_dt=end)

            mock_get.assert_called_once_with(date="2024-01-15")

    def test_max_workers_1_is_sequential(self):
        """EP-PR-009: max_workers=1 (default) should be sequential."""
        client = ClientV2(api_key="test_api_key", max_workers=1)

        call_times = []

        def mock_get(date):
            call_times.append(date)
            return pd.DataFrame()

        with patch.object(client, "get_prices_daily_quotes", side_effect=mock_get):
            client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-17")

            # Should be called sequentially
            assert call_times == ["2024-01-15", "2024-01-16", "2024-01-17"]

    def test_max_workers_gt_1_uses_thread_pool(self):
        """EP-PR-010: max_workers > 1 should use ThreadPoolExecutor and call fetch function."""
        client = ClientV2(api_key="test_api_key", max_workers=3)

        call_dates = []

        def mock_get(date):
            call_dates.append(date)
            return pd.DataFrame(
                {"Date": [pd.Timestamp(date)], "Code": ["1301"], "O": [100]}
            )

        with patch.object(client, "get_prices_daily_quotes", side_effect=mock_get):
            with patch("jquants.client_v2.ThreadPoolExecutor") as mock_executor_class:
                # Make map actually call the function
                def real_map(func, iterable):
                    return [func(item) for item in iterable]

                mock_executor = MagicMock()
                mock_executor.__enter__ = MagicMock(return_value=mock_executor)
                mock_executor.__exit__ = MagicMock(return_value=False)
                mock_executor.map.side_effect = real_map
                mock_executor_class.return_value = mock_executor

                result = client.get_price_range(
                    start_dt="2024-01-15", end_dt="2024-01-16"
                )

                # Verify ThreadPoolExecutor was used with correct max_workers
                mock_executor_class.assert_called_once_with(max_workers=3)

                # Verify get_prices_daily_quotes was actually called for each date
                assert sorted(call_dates) == ["2024-01-15", "2024-01-16"]

                # Verify results were combined
                assert len(result) == 2

    def test_pacer_rate_limiting_with_parallel(self):
        """EP-PR-011: Parallel execution should respect Pacer rate limiting."""
        # This is an integration test; we just verify the pacer is used
        client = ClientV2(api_key="test_api_key", max_workers=3, rate_limit=60)

        # Pacer should be configured
        assert client._pacer.interval == pytest.approx(1.0, rel=1e-6)

    def test_combines_multiple_dataframes(self):
        """EP-PR-012: Should combine DataFrames from multiple days."""
        client = ClientV2(api_key="test_api_key")

        df1 = pd.DataFrame(
            {
                "Date": [pd.Timestamp("2024-01-15")],
                "Code": ["1301"],
                "O": [100],
            }
        )
        df2 = pd.DataFrame(
            {
                "Date": [pd.Timestamp("2024-01-16")],
                "Code": ["1301"],
                "O": [105],
            }
        )

        with patch.object(client, "get_prices_daily_quotes") as mock_get:
            mock_get.side_effect = [df1, df2]

            result = client.get_price_range(start_dt="2024-01-15", end_dt="2024-01-16")

            assert len(result) == 2
            assert result.iloc[0]["O"] == 100
            assert result.iloc[1]["O"] == 105

    def test_start_after_end_raises_valueerror(self):
        """EP-PR-013: start_dt > end_dt should raise ValueError."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_price_range(start_dt="2024-01-20", end_dt="2024-01-15")

        assert (
            "start" in str(exc_info.value).lower()
            or "end" in str(exc_info.value).lower()
        )

    def test_yyyymmdd_format_raises_valueerror(self):
        """EP-PR-014: YYYYMMDD format should raise ValueError (YYYY-MM-DD only)."""
        client = ClientV2(api_key="test_api_key")

        # YYYYMMDD format is not supported for get_price_range
        # because _generate_date_range uses strptime with %Y-%m-%d
        with pytest.raises(ValueError):
            client.get_price_range(start_dt="20240115", end_dt="20240116")

    def test_yyyymmdd_end_dt_raises_valueerror(self):
        """EP-PR-015: YYYYMMDD end_dt should also raise ValueError."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError):
            client.get_price_range(start_dt="2024-01-15", end_dt="20240116")


class TestGetEquitiesInvestorTypes:
    """Test get_equities_investor_types() - /v2/equities/investor-types."""

    def test_returns_dataframe(self):
        """EP-IT-001: get_equities_investor_types() should return pd.DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Section": "TSEPrime",
                    "PubDate": "2024-01-15",
                    "StDate": "2024-01-09",
                    "EnDate": "2024-01-12",
                    "PropSell": 100000,
                    "PropBuy": 200000,
                    "PropTot": 300000,
                    "PropBal": 100000,
                }
            ]

            result = client.get_equities_investor_types()

            assert isinstance(result, pd.DataFrame)

    def test_no_params_calls_api_without_query(self):
        """EP-IT-002: get_equities_investor_types() without args should call API without params."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_equities_investor_types()

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"] == {}

    def test_section_param_passed_to_api(self):
        """EP-IT-003: get_equities_investor_types(section='TSEPrime') should pass section param."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_equities_investor_types(section="TSEPrime")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["section"] == "TSEPrime"

    def test_from_to_date_params_passed_to_api(self):
        """EP-IT-004: from_date and to_date params should be passed."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_equities_investor_types(
                from_date="2024-01-01",
                to_date="2024-12-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-12-31"

    def test_all_params_combined(self):
        """EP-IT-005: All params combined should be passed correctly."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_equities_investor_types(
                section="TSEPrime",
                from_date="2024-01-01",
                to_date="2024-12-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["section"] == "TSEPrime"
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-12-31"

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """EP-IT-006: Empty response should return empty DataFrame with correct columns."""
        from jquants.constants_v2 import EQUITIES_INVESTOR_TYPES_COLUMNS

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_equities_investor_types()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == EQUITIES_INVESTOR_TYPES_COLUMNS

    def test_date_columns_converted_to_timestamp(self):
        """EP-IT-007: PubDate, StDate, EnDate columns should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Section": "TSEPrime",
                    "PubDate": "2024-01-15",
                    "StDate": "2024-01-09",
                    "EnDate": "2024-01-12",
                    "PropSell": 100000,
                    "PropBuy": 200000,
                    "PropTot": 300000,
                    "PropBal": 100000,
                }
            ]

            result = client.get_equities_investor_types()

            assert pd.api.types.is_datetime64_any_dtype(result["PubDate"])
            assert pd.api.types.is_datetime64_any_dtype(result["StDate"])
            assert pd.api.types.is_datetime64_any_dtype(result["EnDate"])

    def test_sorted_by_pubdate_and_section_ascending(self):
        """EP-IT-008: Result should be sorted by PubDate, Section ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Section": "TSEStandard",
                    "PubDate": "2024-01-15",
                    "StDate": "2024-01-09",
                    "EnDate": "2024-01-12",
                    "PropSell": 0,
                },
                {
                    "Section": "TSEPrime",
                    "PubDate": "2024-01-15",
                    "StDate": "2024-01-09",
                    "EnDate": "2024-01-12",
                    "PropSell": 0,
                },
                {
                    "Section": "TSEPrime",
                    "PubDate": "2024-01-08",
                    "StDate": "2024-01-02",
                    "EnDate": "2024-01-05",
                    "PropSell": 0,
                },
            ]

            result = client.get_equities_investor_types()

            # First row: 2024-01-08, TSEPrime
            assert result.iloc[0]["PubDate"] == pd.Timestamp("2024-01-08")
            assert result.iloc[0]["Section"] == "TSEPrime"
            # Second row: 2024-01-15, TSEPrime
            assert result.iloc[1]["PubDate"] == pd.Timestamp("2024-01-15")
            assert result.iloc[1]["Section"] == "TSEPrime"
            # Third row: 2024-01-15, TSEStandard
            assert result.iloc[2]["PubDate"] == pd.Timestamp("2024-01-15")
            assert result.iloc[2]["Section"] == "TSEStandard"

    def test_column_order_matches_constants(self):
        """EP-IT-009: Column order should match EQUITIES_INVESTOR_TYPES_COLUMNS."""
        from jquants.constants_v2 import EQUITIES_INVESTOR_TYPES_COLUMNS

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Return data with columns in different order
            mock_get.return_value = [
                {
                    "PropBuy": 200000,
                    "Section": "TSEPrime",
                    "EnDate": "2024-01-12",
                    "PubDate": "2024-01-15",
                    "StDate": "2024-01-09",
                    "PropSell": 100000,
                    "PropTot": 300000,
                    "PropBal": 100000,
                }
            ]

            result = client.get_equities_investor_types()

            # Columns should be reordered to match constants
            expected_cols = [
                c for c in EQUITIES_INVESTOR_TYPES_COLUMNS if c in result.columns
            ]
            assert list(result.columns) == expected_cols

    def test_endpoint_path_is_correct(self):
        """EP-IT-010: Should call correct API endpoint path."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_equities_investor_types()

            mock_get.assert_called_once()
            call_args = mock_get.call_args[0]
            assert call_args[0] == "/equities/investor-types"
