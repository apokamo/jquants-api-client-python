"""Integration tests for ClientV2 Financials endpoints.

These tests require a valid J-Quants API key.
Run with: poetry run pytest -m integration tests/test_integration/test_fins.py
"""

import pandas as pd
import pytest

from jquants import constants_v2 as constants

from .conftest import requires_api_key


@pytest.mark.integration
class TestFinsSummaryIntegration:
    """Integration tests for fins/summary endpoint."""

    @requires_api_key
    def test_get_fins_summary_with_code(self, client):
        """Test get_fins_summary with code parameter returns valid DataFrame."""
        df = client.get_fins_summary(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check all expected columns are present
            assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

            # Check date columns are datetime
            for col in constants.FINS_SUMMARY_DATE_COLUMNS:
                if col in df.columns:
                    assert pd.api.types.is_datetime64_any_dtype(df[col])

            # Check sorted by DiscDate, DiscTime, Code
            if len(df) > 1:
                is_sorted = True
                for i in range(len(df) - 1):
                    curr = (
                        df.iloc[i]["DiscDate"],
                        df.iloc[i]["DiscTime"],
                        df.iloc[i]["Code"],
                    )
                    next_ = (
                        df.iloc[i + 1]["DiscDate"],
                        df.iloc[i + 1]["DiscTime"],
                        df.iloc[i + 1]["Code"],
                    )
                    if curr > next_:
                        is_sorted = False
                        break
                assert (
                    is_sorted
                ), "DataFrame should be sorted by DiscDate, DiscTime, Code"

    @requires_api_key
    def test_get_fins_summary_with_date(self, client):
        """Test get_fins_summary with date parameter returns valid DataFrame."""
        df = client.get_fins_summary(date="2024-11-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check all expected columns are present
            assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

            # Check DiscDate is the specified date
            assert all(df["DiscDate"] == pd.Timestamp("2024-11-01"))

    @requires_api_key
    def test_get_fins_summary_with_code_and_date(self, client):
        """Test get_fins_summary with both code and date parameters."""
        df = client.get_fins_summary(code="72030", date="2024-11-01")

        assert isinstance(df, pd.DataFrame)
        # Result may be empty if no data for this combination
        assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

    @requires_api_key
    def test_get_fins_summary_column_completeness(self, client):
        """Test that all FINS_SUMMARY_COLUMNS are present even with partial data."""
        df = client.get_fins_summary(code="72030")

        assert isinstance(df, pd.DataFrame)
        # All columns should be present regardless of API response content
        assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

    @requires_api_key
    def test_get_fins_summary_date_column_types(self, client):
        """Test that date columns are properly converted to datetime."""
        df = client.get_fins_summary(date="2024-11-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            for col in constants.FINS_SUMMARY_DATE_COLUMNS:
                assert pd.api.types.is_datetime64_any_dtype(
                    df[col]
                ), f"Column {col} should be datetime type"

    @requires_api_key
    def test_get_fins_summary_empty_date_becomes_nat(self, client):
        """Test that empty/missing date values become NaT, not error."""
        # This tests that the API response with missing date fields
        # is properly handled
        df = client.get_fins_summary(code="72030")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # NxtFYSt/NxtFYEn are often missing (empty) for many records
            for col in ["NxtFYSt", "NxtFYEn"]:
                if col in df.columns:
                    # Should contain NaT for missing values, not raise error
                    # Just verify the column exists and is datetime
                    assert pd.api.types.is_datetime64_any_dtype(df[col])


@pytest.mark.integration
class TestSummaryRangeIntegration:
    """Integration tests for get_summary_range method."""

    @requires_api_key
    def test_get_summary_range_single_day(self, client):
        """Test get_summary_range for a single day."""
        df = client.get_summary_range("2024-11-01", "2024-11-01")

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

    @requires_api_key
    def test_get_summary_range_multiple_days(self, client):
        """Test get_summary_range for multiple days."""
        df = client.get_summary_range("2024-11-01", "2024-11-03")

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS
        if not df.empty:
            # Check sorted by DiscDate, DiscTime, Code
            if len(df) > 1:
                for i in range(len(df) - 1):
                    curr = (
                        df.iloc[i]["DiscDate"],
                        df.iloc[i]["DiscTime"],
                        df.iloc[i]["Code"],
                    )
                    next_ = (
                        df.iloc[i + 1]["DiscDate"],
                        df.iloc[i + 1]["DiscTime"],
                        df.iloc[i + 1]["Code"],
                    )
                    assert curr <= next_, "Should be sorted by DiscDate, DiscTime, Code"

    @requires_api_key
    def test_get_summary_range_column_completeness(self, client):
        """Test that combined result has all expected columns."""
        df = client.get_summary_range("2024-11-01", "2024-11-02")

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == constants.FINS_SUMMARY_COLUMNS

    @requires_api_key
    def test_get_summary_range_date_types(self, client):
        """Test that date columns are datetime in combined result."""
        df = client.get_summary_range("2024-11-01", "2024-11-02")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            for col in constants.FINS_SUMMARY_DATE_COLUMNS:
                assert pd.api.types.is_datetime64_any_dtype(df[col])


@pytest.mark.integration
class TestFinsSummaryErrorHandling:
    """Integration tests for error handling in fins/summary endpoint."""

    @requires_api_key
    def test_no_parameters_raises_valueerror(self, client):
        """Test that calling without code or date raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            client.get_fins_summary()

        assert (
            "code" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        )

    @requires_api_key
    def test_summary_range_invalid_date_format(self, client):
        """Test that YYYYMMDD format raises ValueError."""
        with pytest.raises(ValueError):
            client.get_summary_range("20241101", "20241102")

    @requires_api_key
    def test_summary_range_start_after_end(self, client):
        """Test that start_dt > end_dt raises ValueError."""
        with pytest.raises(ValueError):
            client.get_summary_range("2024-11-05", "2024-11-01")
