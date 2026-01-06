"""Tests for ClientV2._fetch_date_range() - common date range fetch logic.

Issue #40: Phase 3.7 Section 4 - 日付範囲取得ロジックの共通化
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from jquants import ClientV2


class TestFetchDateRangeBasic:
    """Basic functionality tests for _fetch_date_range."""

    def test_single_day_calls_fetch_func_once(self):
        """Single day range should call fetch_func exactly once."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        mock_fetch.assert_called_once_with("2024-01-15")

    def test_multi_day_calls_fetch_func_for_each_date(self):
        """Multi-day range should call fetch_func for each date."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-17",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        assert mock_fetch.call_count == 3

    def test_returns_dataframe(self):
        """Should always return a DataFrame."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        assert isinstance(result, pd.DataFrame)


class TestFetchDateRangeEndDtDefault:
    """Test end_dt default behavior (None = today)."""

    def test_end_dt_none_defaults_to_today(self):
        """end_dt=None should default to today's date."""
        client = ClientV2(api_key="test_api_key")
        today_str = date.today().isoformat()
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        client._fetch_date_range(
            start_dt=today_str,
            end_dt=None,
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        mock_fetch.assert_called_once_with(today_str)


class TestFetchDateRangeValidation:
    """Date validation tests."""

    def test_start_after_end_raises_valueerror(self):
        """start_dt > end_dt should raise ValueError."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            client._fetch_date_range(
                start_dt="2024-01-20",
                end_dt="2024-01-15",
                fetch_func=mock_fetch,
                sort_columns=["Code", "Date"],
                empty_columns=["Code", "Date"],
            )

        assert "start_dt" in str(exc_info.value)
        assert "2024-01-20" in str(exc_info.value)
        assert "2024-01-15" in str(exc_info.value)

    def test_yyyymmdd_format_raises_friendly_error(self):
        """YYYYMMDD format should raise ValueError with friendly message."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            client._fetch_date_range(
                start_dt="20240115",
                end_dt="20240116",
                fetch_func=mock_fetch,
                sort_columns=["Code", "Date"],
                empty_columns=["Code", "Date"],
            )

        error_msg = str(exc_info.value)
        assert "YYYY-MM-DD" in error_msg or "YYYYMMDD" in error_msg


class TestFetchDateRangeEmptyResults:
    """Empty result handling tests."""

    def test_empty_result_returns_empty_dataframe_with_columns(self):
        """All empty results should return DataFrame with expected columns."""
        client = ClientV2(api_key="test_api_key")
        empty_columns = ["Code", "Date", "Open", "Close"]
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=empty_columns))

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=empty_columns,
        )

        assert len(result) == 0
        assert list(result.columns) == empty_columns

    def test_empty_result_date_columns_have_datetime_dtype(self):
        """Empty DataFrame should have datetime64 dtype for date_columns."""
        client = ClientV2(api_key="test_api_key")
        empty_columns = ["Code", "Date", "DiscDate"]
        date_columns = ["Date", "DiscDate"]
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=empty_columns))

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code"],
            empty_columns=empty_columns,
            date_columns=date_columns,
        )

        for col in date_columns:
            assert pd.api.types.is_datetime64_any_dtype(
                result[col]
            ), f"Empty DataFrame column {col} should have datetime dtype"

    def test_empty_result_date_columns_support_dt_accessor(self):
        """Empty DataFrame date columns should support .dt accessor."""
        client = ClientV2(api_key="test_api_key")
        empty_columns = ["Code", "Date"]
        date_columns = ["Date"]
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=empty_columns))

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code"],
            empty_columns=empty_columns,
            date_columns=date_columns,
        )

        # Should not raise AttributeError
        _ = result["Date"].dt.year


class TestFetchDateRangeColumnHandling:
    """Column completeness and ordering tests."""

    def test_ensure_all_columns_fills_missing(self):
        """ensure_all_columns=True should fill missing columns with NA."""
        client = ClientV2(api_key="test_api_key")
        empty_columns = ["Code", "Date", "Extra"]

        # Return DataFrame missing "Extra" column
        incomplete_df = pd.DataFrame({"Code": ["1301"], "Date": ["2024-01-15"]})
        mock_fetch = MagicMock(return_value=incomplete_df)

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code"],
            empty_columns=empty_columns,
            ensure_all_columns=True,
        )

        assert "Extra" in result.columns
        assert pd.isna(result["Extra"].iloc[0])

    def test_ensure_all_columns_reorders_columns(self):
        """ensure_all_columns=True should reorder columns to match empty_columns."""
        client = ClientV2(api_key="test_api_key")
        empty_columns = ["Code", "Date", "Value"]

        # Return DataFrame with columns in wrong order
        wrong_order_df = pd.DataFrame(
            {
                "Value": [100],
                "Code": ["1301"],
                "Date": ["2024-01-15"],
            }
        )
        mock_fetch = MagicMock(return_value=wrong_order_df)

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code"],
            empty_columns=empty_columns,
            ensure_all_columns=True,
        )

        assert list(result.columns) == empty_columns


class TestFetchDateRangeSorting:
    """Sorting tests."""

    def test_result_sorted_by_sort_columns(self):
        """Result should be sorted by sort_columns."""
        client = ClientV2(api_key="test_api_key")

        df1 = pd.DataFrame({"Code": ["1302"], "Date": ["2024-01-15"]})
        df2 = pd.DataFrame({"Code": ["1301"], "Date": ["2024-01-16"]})
        mock_fetch = MagicMock(side_effect=[df1, df2])

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-16",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        # Should be sorted by Code first
        assert result.iloc[0]["Code"] == "1301"
        assert result.iloc[1]["Code"] == "1302"

    def test_sort_columns_not_in_result_are_skipped(self):
        """Sort columns not present in result should be skipped without error."""
        client = ClientV2(api_key="test_api_key")

        df = pd.DataFrame({"Code": ["1301"]})
        mock_fetch = MagicMock(return_value=df)

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code", "NonExistent"],
            empty_columns=["Code"],
        )

        assert len(result) == 1
        assert result.iloc[0]["Code"] == "1301"


class TestFetchDateRangeExecutionMode:
    """Execution mode (sequential vs parallel) tests."""

    def test_max_workers_1_executes_sequentially(self):
        """max_workers=1 should execute fetch_func sequentially."""
        client = ClientV2(api_key="test_api_key", max_workers=1)
        call_order = []

        def track_calls(d):
            call_order.append(d)
            return pd.DataFrame(columns=["Code", "Date"])

        client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-17",
            fetch_func=track_calls,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        # Calls should be in date order
        assert call_order == ["2024-01-15", "2024-01-16", "2024-01-17"]

    def test_max_workers_greater_than_1_uses_threadpool(self):
        """max_workers > 1 should use ThreadPoolExecutor."""
        from concurrent.futures import ThreadPoolExecutor

        client = ClientV2(api_key="test_api_key", max_workers=3)
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        with patch(
            "jquants.client_v2.ThreadPoolExecutor", wraps=ThreadPoolExecutor
        ) as mock_pool:
            client._fetch_date_range(
                start_dt="2024-01-15",
                end_dt="2024-01-17",
                fetch_func=mock_fetch,
                sort_columns=["Code", "Date"],
                empty_columns=["Code", "Date"],
            )

            mock_pool.assert_called_once_with(max_workers=3)

    def test_parallel_and_sequential_produce_same_result(self):
        """Sequential and parallel execution should produce identical results."""
        df1 = pd.DataFrame({"Code": ["1301"], "Date": ["2024-01-15"]})
        df2 = pd.DataFrame({"Code": ["1302"], "Date": ["2024-01-16"]})

        # Sequential
        client_seq = ClientV2(api_key="test_api_key", max_workers=1)
        mock_fetch_seq = MagicMock(side_effect=[df1.copy(), df2.copy()])
        result_seq = client_seq._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-16",
            fetch_func=mock_fetch_seq,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        # Parallel
        client_par = ClientV2(api_key="test_api_key", max_workers=2)
        mock_fetch_par = MagicMock(side_effect=[df1.copy(), df2.copy()])
        result_par = client_par._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-16",
            fetch_func=mock_fetch_par,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        pd.testing.assert_frame_equal(result_seq, result_par)


class TestFetchDateRangeBoundaryConditions:
    """Boundary condition tests."""

    def test_single_day_start_equals_end(self):
        """start_dt == end_dt should fetch exactly one day."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock(
            return_value=pd.DataFrame({"Code": ["1301"], "Date": ["2024-01-15"]})
        )

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-15",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        mock_fetch.assert_called_once()
        assert len(result) == 1

    def test_partial_data_some_days_empty(self):
        """Some days returning empty should still combine non-empty results."""
        client = ClientV2(api_key="test_api_key")
        df1 = pd.DataFrame({"Code": ["1301"], "Date": ["2024-01-15"]})
        empty_df = pd.DataFrame(columns=["Code", "Date"])
        df3 = pd.DataFrame({"Code": ["1302"], "Date": ["2024-01-17"]})
        mock_fetch = MagicMock(side_effect=[df1, empty_df, df3])

        result = client._fetch_date_range(
            start_dt="2024-01-15",
            end_dt="2024-01-17",
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        assert len(result) == 2
        assert "1301" in result["Code"].values
        assert "1302" in result["Code"].values

    def test_date_input_accepts_date_object(self):
        """Should accept date object as start_dt/end_dt."""
        client = ClientV2(api_key="test_api_key")
        mock_fetch = MagicMock(return_value=pd.DataFrame(columns=["Code", "Date"]))

        start = date(2024, 1, 15)
        end = date(2024, 1, 15)

        client._fetch_date_range(
            start_dt=start,
            end_dt=end,
            fetch_func=mock_fetch,
            sort_columns=["Code", "Date"],
            empty_columns=["Code", "Date"],
        )

        mock_fetch.assert_called_once_with("2024-01-15")


class TestFetchDateRangeFutureWarning:
    """Test that FutureWarning from pd.concat with empty DataFrames is avoided."""

    def test_no_futurewarning_on_concat_empty_dataframes(self):
        """Should filter empty DataFrames before concat to avoid FutureWarning."""
        import warnings

        client = ClientV2(api_key="test_api_key")
        empty_df = pd.DataFrame(columns=["Code", "Date"])
        mock_fetch = MagicMock(return_value=empty_df)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            client._fetch_date_range(
                start_dt="2024-01-15",
                end_dt="2024-01-16",
                fetch_func=mock_fetch,
                sort_columns=["Code", "Date"],
                empty_columns=["Code", "Date"],
            )

            # Check no FutureWarning about concatenating DataFrames with columns of all-NA
            future_warnings = [
                warning for warning in w if issubclass(warning.category, FutureWarning)
            ]
            assert (
                len(future_warnings) == 0
            ), f"Unexpected FutureWarning: {[str(fw.message) for fw in future_warnings]}"
