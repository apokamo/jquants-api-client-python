"""Integration tests for ClientV2 Markets endpoints.

These tests require a valid J-Quants API key.
Run with: poetry run pytest -m integration tests/test_integration/test_markets.py
"""

import pandas as pd
import pytest

from jquants import constants_v2 as constants

from .conftest import requires_api_key, requires_premium


@pytest.mark.integration
class TestMarketsIntegration:
    """Integration tests for Markets endpoints."""

    @requires_api_key
    def test_get_markets_trading_calendar(self, client):
        """Test get_markets_trading_calendar returns valid DataFrame."""
        df = client.get_markets_trading_calendar(
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.MARKETS_CALENDAR_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check sorted by Date
            assert df["Date"].is_monotonic_increasing

    @requires_api_key
    def test_get_markets_trading_calendar_with_holiday_division(self, client):
        """Test get_markets_trading_calendar with holiday_division filter."""
        df = client.get_markets_trading_calendar(
            holiday_division="1",
            from_date="2024-01-01",
            to_date="2024-12-31",
        )

        assert isinstance(df, pd.DataFrame)
        # Should filter by holiday division
        if not df.empty:
            assert all(df["HolDiv"] == "1")

    @requires_api_key
    def test_get_markets_weekly_margin_interest(self, client):
        """Test get_markets_weekly_margin_interest returns valid DataFrame."""
        df = client.get_markets_weekly_margin_interest(
            code="72030",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
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

    @requires_api_key
    def test_get_markets_short_selling(self, client):
        """Test get_markets_short_selling returns valid DataFrame.

        Note: V2 API requires 'date' or 's33' parameter.
        """
        df = client.get_markets_short_selling(
            sector_33_code="0050",
            from_date="2024-01-01",
            to_date="2024-01-05",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check columns
            for col in ["Date", "S33"]:
                assert col in df.columns

    @requires_api_key
    def test_get_markets_short_selling_with_sector(self, client):
        """Test get_markets_short_selling with sector_33_code filter."""
        df = client.get_markets_short_selling(
            sector_33_code="0050",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        # Should filter by sector
        if not df.empty:
            assert all(df["S33"] == "0050")

    @requires_api_key
    @pytest.mark.premium
    @requires_premium
    def test_get_markets_breakdown(self, client):
        """Test get_markets_breakdown returns valid DataFrame.

        Note: This endpoint requires Premium or higher subscription plan.
        """
        df = client.get_markets_breakdown(
            code="72030",
            from_date="2024-01-01",
            to_date="2024-01-05",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check key columns exist
            assert "Date" in df.columns
            assert "Code" in df.columns

    @requires_api_key
    def test_get_markets_short_selling_positions(self, client):
        """Test get_markets_short_selling_positions returns valid DataFrame.

        Note: V2 API requires 'code' when using disc_date_from/disc_date_to.
        """
        df = client.get_markets_short_selling_positions(
            code="72030",
            disc_date_from="2024-01-01",
            disc_date_to="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check date columns are datetime
            for col in ["DiscDate", "CalcDate"]:
                if col in df.columns:
                    assert pd.api.types.is_datetime64_any_dtype(df[col])

            # Verify DiscDate is within specified range (filter validation)
            if "DiscDate" in df.columns:
                min_date = pd.Timestamp("2024-01-01")
                max_date = pd.Timestamp("2024-01-31")
                assert df["DiscDate"].min() >= min_date, "DiscDate below range"
                assert df["DiscDate"].max() <= max_date, "DiscDate above range"

    @requires_api_key
    def test_get_markets_daily_margin_interest(self, client):
        """Test get_markets_daily_margin_interest returns valid DataFrame.

        Note: V2 API requires 'code' when using from_date/to_date.
        """
        df = client.get_markets_daily_margin_interest(
            code="72030",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check date columns are datetime
            for col in ["PubDate", "AppDate"]:
                if col in df.columns:
                    assert pd.api.types.is_datetime64_any_dtype(df[col])

            # Check nested PubReason is flattened
            assert "PubReason.DailyPublication" in df.columns or df.empty

    @requires_api_key
    def test_get_markets_daily_margin_interest_with_code(self, client):
        """Test get_markets_daily_margin_interest with code filter."""
        df = client.get_markets_daily_margin_interest(
            code="72030",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        # Should filter by code
        if not df.empty:
            assert all(df["Code"] == "72030")

    @requires_api_key
    def test_column_order_matches_constants(self, client):
        """Test that returned DataFrame columns match constants definition order."""
        # Use a known date range with data
        df = client.get_markets_trading_calendar(
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        # If data exists, verify column order matches constants
        if not df.empty:
            expected_cols = [
                c for c in constants.MARKETS_CALENDAR_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols
