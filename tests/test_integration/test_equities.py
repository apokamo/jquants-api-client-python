"""Integration tests for ClientV2 Equities-Standard endpoints.

These tests require a valid J-Quants API key.
Run with: poetry run pytest -m integration tests/test_integration/test_equities.py

Sub-Phase 3.2 endpoints:
- get_listed_info() - /v2/equities/master
- get_prices_daily_quotes() - /v2/equities/bars/daily
- get_fins_announcement() - /v2/equities/earnings-calendar
- get_price_range() - date range helper
- get_equities_investor_types() - /v2/equities/investor-types
"""

import pandas as pd
import pytest

from jquants import constants_v2 as constants

from .conftest import requires_api_key


@pytest.mark.integration
class TestEquitiesIntegration:
    """Integration tests for Equities-Standard endpoints."""

    # ========================================
    # get_listed_info() tests
    # ========================================

    @requires_api_key
    def test_get_listed_info_all(self, client):
        """Test get_listed_info returns valid DataFrame for all stocks."""
        df = client.get_listed_info()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "Expected non-empty DataFrame for all stocks"

        # Check column order matches constants
        expected_cols = [
            c for c in constants.EQUITIES_MASTER_COLUMNS if c in df.columns
        ]
        assert list(df.columns) == expected_cols

        # Check Date is datetime
        assert pd.api.types.is_datetime64_any_dtype(df["Date"])

        # Check sorted by Code
        assert df["Code"].is_monotonic_increasing

    @requires_api_key
    def test_get_listed_info_with_code(self, client):
        """Test get_listed_info with code filter."""
        df = client.get_listed_info(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Should filter by code
            assert all(df["Code"] == "72030")

    @requires_api_key
    def test_get_listed_info_with_date(self, client):
        """Test get_listed_info with date filter."""
        df = client.get_listed_info(date="2024-01-04")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check Date is datetime and matches filter
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])
            assert all(df["Date"] == pd.Timestamp("2024-01-04"))

    # ========================================
    # get_prices_daily_quotes() tests
    # ========================================

    @requires_api_key
    def test_get_prices_daily_quotes_by_code(self, client):
        """Test get_prices_daily_quotes with code filter."""
        df = client.get_prices_daily_quotes(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.EQUITIES_BARS_DAILY_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check sorted by Code, Date
            assert all(df["Code"] == "72030")
            assert df["Date"].is_monotonic_increasing

    @requires_api_key
    def test_get_prices_daily_quotes_by_date(self, client):
        """Test get_prices_daily_quotes with single date."""
        df = client.get_prices_daily_quotes(date="2024-01-04")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check Date is datetime and matches filter
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])
            assert all(df["Date"] == pd.Timestamp("2024-01-04"))

            # Check sorted by Code
            assert df["Code"].is_monotonic_increasing

    @requires_api_key
    def test_get_prices_daily_quotes_with_date_range(self, client):
        """Test get_prices_daily_quotes with date range."""
        df = client.get_prices_daily_quotes(
            code="72030",
            from_date="2024-01-04",
            to_date="2024-01-10",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check date range
            min_date = pd.Timestamp("2024-01-04")
            max_date = pd.Timestamp("2024-01-10")
            assert df["Date"].min() >= min_date
            assert df["Date"].max() <= max_date

            # Check sorted by Date
            assert df["Date"].is_monotonic_increasing

    @requires_api_key
    def test_get_prices_daily_quotes_empty_result(self, client):
        """Test get_prices_daily_quotes returns empty DataFrame with columns for future date."""
        # Use a far future date that won't have data
        df = client.get_prices_daily_quotes(date="2099-01-01")

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        # Empty DataFrame should still have column definitions
        assert len(df.columns) > 0

    # ========================================
    # get_fins_announcement() tests
    # ========================================

    @requires_api_key
    def test_get_fins_announcement(self, client):
        """Test get_fins_announcement returns valid DataFrame."""
        df = client.get_fins_announcement()

        assert isinstance(df, pd.DataFrame)
        # This endpoint returns upcoming announcements, may be empty
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c
                for c in constants.EQUITIES_EARNINGS_CALENDAR_COLUMNS
                if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check sorted by Date, Code
            if len(df) > 1:
                for i in range(len(df) - 1):
                    assert (
                        df.iloc[i]["Date"] < df.iloc[i + 1]["Date"]
                        or df.iloc[i]["Date"] == df.iloc[i + 1]["Date"]
                        and df.iloc[i]["Code"] <= df.iloc[i + 1]["Code"]
                    )

    # ========================================
    # get_price_range() tests
    # ========================================

    @requires_api_key
    def test_get_price_range_basic(self, client):
        """Test get_price_range returns valid DataFrame for date range."""
        df = client.get_price_range(
            start_dt="2024-01-04",
            end_dt="2024-01-05",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check date range
            min_date = pd.Timestamp("2024-01-04")
            max_date = pd.Timestamp("2024-01-05")
            assert df["Date"].min() >= min_date
            assert df["Date"].max() <= max_date

            # Check sorted by Code, Date
            # (sorted by Code first, then Date within each Code)
            prev_code = None
            prev_date = None
            for _, row in df.iterrows():
                if prev_code is not None:
                    if row["Code"] == prev_code:
                        assert row["Date"] >= prev_date
                    else:
                        assert row["Code"] >= prev_code
                prev_code = row["Code"]
                prev_date = row["Date"]

    @requires_api_key
    def test_get_price_range_single_day(self, client):
        """Test get_price_range with single day range."""
        df = client.get_price_range(
            start_dt="2024-01-04",
            end_dt="2024-01-04",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # All dates should be the same
            assert all(df["Date"] == pd.Timestamp("2024-01-04"))

    @requires_api_key
    def test_get_price_range_invalid_date_order(self, client):
        """Test get_price_range raises ValueError for invalid date order."""
        with pytest.raises(ValueError, match="start_dt.*end_dt"):
            client.get_price_range(
                start_dt="2024-01-10",
                end_dt="2024-01-04",
            )

    # ========================================
    # Column order validation tests
    # ========================================

    @requires_api_key
    def test_listed_info_column_order(self, client):
        """Test that get_listed_info columns match constants definition order."""
        df = client.get_listed_info(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = [
                c for c in constants.EQUITIES_MASTER_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

    @requires_api_key
    def test_prices_daily_quotes_column_order(self, client):
        """Test that get_prices_daily_quotes columns match constants definition order."""
        df = client.get_prices_daily_quotes(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = [
                c for c in constants.EQUITIES_BARS_DAILY_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

    # ========================================
    # get_equities_investor_types() tests
    # ========================================

    @requires_api_key
    def test_get_equities_investor_types_all(self, client):
        """Test get_equities_investor_types returns valid DataFrame for all sections."""
        df = client.get_equities_investor_types()

        assert isinstance(df, pd.DataFrame)
        # This endpoint may return empty if no recent data
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.EQUITIES_INVESTOR_TYPES_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check date columns are datetime
            assert pd.api.types.is_datetime64_any_dtype(df["PubDate"])
            assert pd.api.types.is_datetime64_any_dtype(df["StDate"])
            assert pd.api.types.is_datetime64_any_dtype(df["EnDate"])

            # Check sorted by PubDate, Section
            if len(df) > 1:
                for i in range(len(df) - 1):
                    curr_date = df.iloc[i]["PubDate"]
                    next_date = df.iloc[i + 1]["PubDate"]
                    assert (
                        curr_date < next_date
                        or curr_date == next_date
                        and df.iloc[i]["Section"] <= df.iloc[i + 1]["Section"]
                    )

    @requires_api_key
    def test_get_equities_investor_types_with_section(self, client):
        """Test get_equities_investor_types with section filter."""
        df = client.get_equities_investor_types(section="TSEPrime")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Should filter by section
            assert all(df["Section"] == "TSEPrime")

    @requires_api_key
    def test_get_equities_investor_types_with_date_range(self, client):
        """Test get_equities_investor_types with date range."""
        df = client.get_equities_investor_types(
            from_date="2024-01-01",
            to_date="2024-03-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check date range (PubDate should be within range)
            min_date = pd.Timestamp("2024-01-01")
            max_date = pd.Timestamp("2024-03-31")
            assert df["PubDate"].min() >= min_date
            assert df["PubDate"].max() <= max_date

    @requires_api_key
    def test_get_equities_investor_types_column_order(self, client):
        """Test that get_equities_investor_types columns match constants definition order."""
        df = client.get_equities_investor_types(section="TSEPrime")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = [
                c for c in constants.EQUITIES_INVESTOR_TYPES_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

    @requires_api_key
    def test_get_equities_investor_types_nonexistent_section(self, client):
        """Test get_equities_investor_types returns empty DataFrame for nonexistent section."""
        df = client.get_equities_investor_types(section="NonExistentSection")

        assert isinstance(df, pd.DataFrame)
        # Should return empty DataFrame, not raise error
        assert df.empty
        # Empty DataFrame should still have column definitions
        assert list(df.columns) == constants.EQUITIES_INVESTOR_TYPES_COLUMNS
