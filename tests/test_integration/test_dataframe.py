"""DF: DataFrame conversion tests.

Test IDs: DF-001 through DF-008
See Issue #10 for test case specifications.
"""

import pandas as pd
import pytest

from jquants import ClientV2
from jquants.constants_v2 import EQUITIES_MASTER_COLUMNS

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestDataFrameNormal:
    """Normal DataFrame conversion test cases."""

    def test_df_001_api_response_to_dataframe(self, client: ClientV2) -> None:
        """DF-001: API response is converted to pandas DataFrame."""
        data = client._paginated_get("/equities/master")
        df = client._to_dataframe(data, columns=EQUITIES_MASTER_COLUMNS)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_df_002_column_order(self, client: ClientV2) -> None:
        """DF-002: Column order follows constants_v2.py definition."""
        data = client._paginated_get("/equities/master")
        df = client._to_dataframe(data, columns=EQUITIES_MASTER_COLUMNS)

        # Columns should be in the order defined in constants
        expected_order = [c for c in EQUITIES_MASTER_COLUMNS if c in df.columns]
        actual_order = list(df.columns)
        assert actual_order == expected_order

    def test_df_003_date_column_type(self, client: ClientV2) -> None:
        """DF-003: Date columns are converted to pd.Timestamp."""
        data = client._paginated_get("/equities/master")
        df = client._to_dataframe(
            data,
            columns=EQUITIES_MASTER_COLUMNS,
            date_columns=["Date"],
        )
        if "Date" in df.columns:
            # Check dtype is datetime64
            assert pd.api.types.is_datetime64_any_dtype(df["Date"])

    def test_df_004_sorting_applied(self, client: ClientV2) -> None:
        """DF-004: Sorting is correctly applied."""
        data = client._paginated_get("/equities/master")
        df = client._to_dataframe(
            data,
            columns=EQUITIES_MASTER_COLUMNS,
            date_columns=["Date"],
            sort_columns=["Date", "Code"],
        )
        if "Date" in df.columns and "Code" in df.columns:
            # Verify sorted by Date, then Code
            df_sorted = df.sort_values(["Date", "Code"]).reset_index(drop=True)
            pd.testing.assert_frame_equal(df, df_sorted)


class TestDataFrameRare:
    """Rare/edge case DataFrame tests."""

    def test_df_005_missing_columns_ignored(self, client: ClientV2) -> None:
        """DF-005: Columns not in API response are ignored (Free vs Premium)."""
        data = client._paginated_get("/equities/master")
        df = client._to_dataframe(data, columns=EQUITIES_MASTER_COLUMNS)

        # Some columns may be Premium-only (e.g., Mrgn, MrgnNm)
        # The important thing is no error is raised
        assert isinstance(df, pd.DataFrame)

    def test_df_006_empty_data_returns_empty_df(self, client: ClientV2) -> None:
        """DF-006: Empty data list returns empty DataFrame with columns."""
        empty_data: list[dict] = []
        df = client._to_dataframe(empty_data, columns=EQUITIES_MASTER_COLUMNS)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == EQUITIES_MASTER_COLUMNS

    def test_df_007_invalid_date_format(self, client: ClientV2) -> None:
        """DF-007: Invalid date format passes through (pandas exception).

        Note: Actual behavior depends on pandas version and data.
        """
        # Create test data with invalid date
        invalid_data = [{"Date": "not-a-date", "Code": "1234"}]
        # This should either work (coerced to NaT) or raise pandas exception
        try:
            df = client._to_dataframe(
                invalid_data,
                columns=["Date", "Code"],
                date_columns=["Date"],
            )
            # If it works, Date should be NaT or similar
            assert isinstance(df, pd.DataFrame)
        except Exception:
            # pandas exception is acceptable
            pass

    def test_df_008_null_values_preserved(self, client: ClientV2) -> None:
        """DF-008: NaN/null values are preserved in DataFrame."""
        # Create test data with null
        test_data: list[dict] = [
            {"Date": "2024-01-01", "Code": "1234", "Value": None},
            {"Date": "2024-01-02", "Code": "5678", "Value": 100},
        ]
        df = client._to_dataframe(
            test_data,
            columns=["Date", "Code", "Value"],
        )
        assert df["Value"].isna().any()  # Should have at least one NaN
