"""Integration tests for ClientV2 Derivatives endpoints.

These tests require a valid J-Quants API key with Standard plan or higher.
Run with: poetry run pytest -m integration tests/test_integration/test_derivatives.py

"""

import pandas as pd
import pytest

from jquants import constants_v2 as constants

from .conftest import requires_api_key


@pytest.mark.integration
class TestDerivativesIntegration:
    """Integration tests for Derivatives endpoints."""

    @requires_api_key
    def test_get_options_225_daily(self, client):
        """Test get_options_225_daily returns valid DataFrame.

        Note: The endpoint returns Nikkei 225 option data for the specified date.
        """
        df = client.get_options_225_daily(date="2024-12-27")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.DERIVATIVES_OPTIONS_225_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check date columns are datetime
            for col in constants.DERIVATIVES_OPTIONS_225_DATE_COLUMNS:
                if col in df.columns:
                    assert pd.api.types.is_datetime64_any_dtype(df[col])

            # Check sorted by Code
            if len(df) > 1:
                assert df["Code"].is_monotonic_increasing

    @requires_api_key
    def test_get_options_225_daily_column_types(self, client):
        """Test get_options_225_daily returns correct column types."""
        df = client.get_options_225_daily(date="2024-12-27")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check numeric columns are numeric (or NaN for empty values)
            assert pd.api.types.is_numeric_dtype(df["Strike"])
            assert pd.api.types.is_numeric_dtype(df["Vo"])
            assert pd.api.types.is_numeric_dtype(df["OI"])

            # Check CM column format (YYYY-MM)
            if "CM" in df.columns:
                sample_cm = (
                    df["CM"].dropna().iloc[0] if not df["CM"].dropna().empty else None
                )
                if sample_cm:
                    assert len(sample_cm) == 7  # "YYYY-MM"
                    assert sample_cm[4] == "-"  # Separator

    @requires_api_key
    def test_get_options_225_daily_range(self, client):
        """Test get_options_225_daily_range returns valid DataFrame."""
        df = client.get_options_225_daily_range(
            start_dt="2024-12-26",
            end_dt="2024-12-27",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check date columns are datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check sorted by Code, Date
            if len(df) > 1:
                for i in range(len(df) - 1):
                    code_i = df.iloc[i]["Code"]
                    code_next = df.iloc[i + 1]["Code"]
                    date_i = df.iloc[i]["Date"]
                    date_next = df.iloc[i + 1]["Date"]
                    assert (code_i < code_next) or (
                        code_i == code_next and date_i <= date_next
                    )

    @requires_api_key
    def test_get_options_225_daily_empty_date(self, client):
        """Test get_options_225_daily with holiday returns empty DataFrame.

        Note: API returns empty list on holidays, not 404 error.
        """
        # 2024-01-01 is New Year's Day (holiday)
        df = client.get_options_225_daily(date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        # Should return empty DataFrame (not error)
        assert len(df) == 0
        # Should still have column definitions
        assert list(df.columns) == constants.DERIVATIVES_OPTIONS_225_COLUMNS

    @requires_api_key
    def test_column_order_matches_constants(self, client):
        """Test that returned DataFrame columns match constants definition order."""
        df = client.get_options_225_daily(date="2024-12-27")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = [
                c for c in constants.DERIVATIVES_OPTIONS_225_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols
