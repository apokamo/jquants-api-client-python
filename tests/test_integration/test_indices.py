"""Integration tests for ClientV2 Indices endpoints.

These tests require a valid J-Quants API key.
Run with: poetry run pytest -m integration tests/test_integration/test_indices.py
"""

import pandas as pd
import pytest

from jquants import constants_v2 as constants

from .conftest import requires_api_key


@pytest.mark.integration
class TestIndicesIntegration:
    """Integration tests for Indices endpoints."""

    @requires_api_key
    def test_get_indices(self, client):
        """Test get_indices returns valid DataFrame."""
        df = client.get_indices(
            code="0000",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.INDICES_BARS_DAILY_COLUMNS if c in df.columns
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

    @requires_api_key
    def test_get_indices_with_date(self, client):
        """Test get_indices with date parameter."""
        df = client.get_indices(date="2024-01-04")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # All rows should have same date
            assert df["Date"].nunique() == 1

            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

    @requires_api_key
    def test_get_indices_with_code_filter(self, client):
        """Test get_indices with code filter."""
        df = client.get_indices(
            code="0000",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        # Should filter by code
        if not df.empty:
            assert all(df["Code"] == "0000")

    @requires_api_key
    def test_get_indices_empty_result(self, client):
        """Test get_indices with non-existent date returns empty DataFrame."""
        # Use a date that definitely has no data (e.g., far future)
        df = client.get_indices(date="2099-01-01")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        # Even empty DataFrame should have correct columns
        assert list(df.columns) == constants.INDICES_BARS_DAILY_COLUMNS

    @requires_api_key
    def test_get_indices_topix(self, client):
        """Test get_indices_topix returns valid DataFrame."""
        df = client.get_indices_topix(
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check column order matches constants
            expected_cols = [
                c for c in constants.INDICES_BARS_DAILY_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols

            # Check Date is datetime
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

            # Check sorted by Date
            assert df["Date"].is_monotonic_increasing or len(df) == 1

    @requires_api_key
    def test_get_indices_topix_no_params(self, client):
        """Test get_indices_topix works without parameters (full data)."""
        # This may return a large dataset, just verify it works
        df = client.get_indices_topix()

        assert isinstance(df, pd.DataFrame)
        # Should return data (TOPIX has historical data)
        # Note: This test may take longer due to full data retrieval

    @requires_api_key
    def test_column_order_matches_constants(self, client):
        """Test that returned DataFrame columns match constants definition order."""
        df = client.get_indices(
            code="0000",
            from_date="2024-01-01",
            to_date="2024-01-31",
        )

        assert isinstance(df, pd.DataFrame)
        # If data exists, verify column order matches constants
        if not df.empty:
            expected_cols = [
                c for c in constants.INDICES_BARS_DAILY_COLUMNS if c in df.columns
            ]
            assert list(df.columns) == expected_cols
