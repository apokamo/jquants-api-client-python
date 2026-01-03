"""TDD tests for get_fins_summary() and get_summary_range()."""

from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from jquants import constants_v2


class TestToDataframeEnsureAllColumns:
    """Test _to_dataframe ensure_all_columns parameter."""

    def test_ensure_all_columns_false_ignores_missing(self):
        """ensure_all_columns=False should ignore missing columns (default behavior)."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": "2024-01-01"}]
        columns = ["Code", "DiscDate", "MissingColumn"]

        result = client._to_dataframe(data, columns, ensure_all_columns=False)

        assert "Code" in result.columns
        assert "DiscDate" in result.columns
        assert "MissingColumn" not in result.columns

    def test_ensure_all_columns_true_fills_missing_with_nan(self):
        """ensure_all_columns=True should add missing columns with NaN."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": "2024-01-01"}]
        columns = ["Code", "DiscDate", "MissingColumn"]

        result = client._to_dataframe(data, columns, ensure_all_columns=True)

        assert "Code" in result.columns
        assert "DiscDate" in result.columns
        assert "MissingColumn" in result.columns
        assert pd.isna(result["MissingColumn"].iloc[0])

    def test_ensure_all_columns_preserves_column_order(self):
        """ensure_all_columns=True should preserve column order from definition."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"B": 2, "A": 1}]
        columns = ["A", "B", "C"]

        result = client._to_dataframe(data, columns, ensure_all_columns=True)

        assert list(result.columns) == ["A", "B", "C"]

    def test_empty_data_with_ensure_all_columns(self):
        """Empty data with ensure_all_columns=True should return DataFrame with all columns."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        columns = ["A", "B", "C"]

        result = client._to_dataframe([], columns, ensure_all_columns=True)

        assert len(result) == 0
        assert list(result.columns) == columns


class TestToDataframeDateNaT:
    """Test _to_dataframe date column NaT conversion."""

    def test_empty_string_date_becomes_nat(self):
        """Empty string in date column should become NaT."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": ""}]
        columns = ["Code", "DiscDate"]

        result = client._to_dataframe(
            data, columns, date_columns=["DiscDate"], ensure_all_columns=True
        )

        assert pd.isna(result["DiscDate"].iloc[0])

    def test_none_date_becomes_nat(self):
        """None in date column should become NaT."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": None}]
        columns = ["Code", "DiscDate"]

        result = client._to_dataframe(
            data, columns, date_columns=["DiscDate"], ensure_all_columns=True
        )

        assert pd.isna(result["DiscDate"].iloc[0])

    def test_valid_date_converted(self):
        """Valid date string should be converted to Timestamp."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": "2024-01-15"}]
        columns = ["Code", "DiscDate"]

        result = client._to_dataframe(
            data, columns, date_columns=["DiscDate"], ensure_all_columns=True
        )

        assert result["DiscDate"].iloc[0] == pd.Timestamp("2024-01-15")

    def test_invalid_date_coerced_to_nat(self):
        """Invalid date like '0000-00-00' should become NaT with errors='coerce'."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        data = [{"Code": "1301", "DiscDate": "0000-00-00"}]
        columns = ["Code", "DiscDate"]

        result = client._to_dataframe(
            data, columns, date_columns=["DiscDate"], ensure_all_columns=True
        )

        assert pd.isna(result["DiscDate"].iloc[0])


class TestFinsSummaryColumnsSpec:
    """Test FINS_SUMMARY_COLUMNS against fixed specification.

    These tests use fixed expected values to detect accidental column omissions
    that would otherwise go unnoticed if only self-referencing constants.
    """

    # Core columns that MUST exist (fixed specification, not from constants)
    REQUIRED_CORE_COLUMNS = [
        "DiscDate",
        "DiscTime",
        "Code",
        "DiscNo",
        "DocType",
        "CurPerType",
        "CurPerSt",
        "CurPerEn",
    ]

    REQUIRED_CONSOLIDATED_COLUMNS = [
        "Sales",
        "OP",
        "OdP",
        "NP",
        "EPS",
        "DEPS",
        "TA",
        "Eq",
        "EqAR",
        "BPS",
    ]

    REQUIRED_NON_CONSOLIDATED_COLUMNS = [
        "NCSales",
        "NCOP",
        "NCOdP",
        "NCNP",
        "NCEPS",
        "NCTA",
        "NCEq",
        "NCEqAR",
        "NCBPS",
    ]

    def test_core_columns_in_definition(self):
        """Core columns must be present in FINS_SUMMARY_COLUMNS."""
        for col in self.REQUIRED_CORE_COLUMNS:
            assert (
                col in constants_v2.FINS_SUMMARY_COLUMNS
            ), f"Core column '{col}' missing from FINS_SUMMARY_COLUMNS"

    def test_consolidated_columns_in_definition(self):
        """Consolidated performance columns must be present."""
        for col in self.REQUIRED_CONSOLIDATED_COLUMNS:
            assert (
                col in constants_v2.FINS_SUMMARY_COLUMNS
            ), f"Consolidated column '{col}' missing from FINS_SUMMARY_COLUMNS"

    def test_non_consolidated_columns_in_definition(self):
        """Non-consolidated performance columns must be present (per official spec)."""
        for col in self.REQUIRED_NON_CONSOLIDATED_COLUMNS:
            assert (
                col in constants_v2.FINS_SUMMARY_COLUMNS
            ), f"Non-consolidated column '{col}' missing from FINS_SUMMARY_COLUMNS"

    def test_ncdeps_not_in_official_spec(self):
        """NCDEPS is NOT in official API spec (unlike Issue#21 description).

        The official J-Quants API does not return NCDEPS for non-consolidated data.
        This test documents that our implementation correctly follows the official spec,
        not the erroneous Issue description.
        """
        # NCDEPS should NOT be in the columns (it's not in official API spec)
        assert "NCDEPS" not in constants_v2.FINS_SUMMARY_COLUMNS

    def test_nxfdivtotalann_not_in_official_spec(self):
        """NxFDivTotalAnn is NOT in official API spec.

        While FDivTotalAnn exists, NxFDivTotalAnn does not exist in the official spec.
        """
        assert "NxFDivTotalAnn" not in constants_v2.FINS_SUMMARY_COLUMNS
        # But FDivTotalAnn should exist
        assert "FDivTotalAnn" in constants_v2.FINS_SUMMARY_COLUMNS


class TestGetFinsSummary:
    """Test get_fins_summary() method."""

    def test_code_parameter_passed_to_api(self):
        """code parameter should be passed to API."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []
            client.get_fins_summary(code="1301")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/fins/summary"
            assert call_args[0][1]["code"] == "1301"

    def test_date_parameter_passed_to_api(self):
        """date parameter should be passed to API."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []
            client.get_fins_summary(date="2024-01-15")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/fins/summary"
            assert call_args[0][1]["date"] == "2024-01-15"

    def test_code_and_date_both_passed(self):
        """Both code and date parameters should be passed to API."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []
            client.get_fins_summary(code="1301", date="2024-01-15")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][1]["code"] == "1301"
            assert call_args[0][1]["date"] == "2024-01-15"

    def test_no_parameters_raises_valueerror(self):
        """get_fins_summary() without code or date should raise ValueError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_fins_summary()

        assert (
            "code" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        )

    def test_returns_dataframe(self):
        """get_fins_summary() should return pandas DataFrame."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Code": "13010", "DiscDate": "2024-01-15", "DiscTime": "15:30:00"}
            ]
            result = client.get_fins_summary(code="1301")

            assert isinstance(result, pd.DataFrame)

    def test_all_columns_present_even_if_missing_from_response(self):
        """All FINS_SUMMARY_COLUMNS should be present even if missing from API response."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        # API response with only a few columns
        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Code": "13010", "DiscDate": "2024-01-15", "DiscTime": "15:30:00"}
            ]
            result = client.get_fins_summary(code="1301")

            # All columns from constants should be present
            for col in constants_v2.FINS_SUMMARY_COLUMNS:
                assert col in result.columns, f"Column {col} missing"

    def test_column_order_matches_definition(self):
        """Column order should match FINS_SUMMARY_COLUMNS definition."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [{"Code": "13010", "DiscDate": "2024-01-15"}]
            result = client.get_fins_summary(code="1301")

            assert list(result.columns) == constants_v2.FINS_SUMMARY_COLUMNS

    def test_date_columns_converted_to_timestamp(self):
        """All date columns should be converted to pd.Timestamp."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Code": "13010",
                    "DiscDate": "2024-01-15",
                    "CurPerSt": "2024-01-01",
                    "CurPerEn": "2024-03-31",
                }
            ]
            result = client.get_fins_summary(code="1301")

            for col in constants_v2.FINS_SUMMARY_DATE_COLUMNS:
                if col in result.columns:
                    assert pd.api.types.is_datetime64_any_dtype(
                        result[col]
                    ), f"Column {col} should be datetime type"

    def test_empty_date_becomes_nat(self):
        """Empty string or None in date columns should become NaT."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Code": "13010",
                    "DiscDate": "2024-01-15",
                    "NxtFYSt": "",  # Empty string
                    "NxtFYEn": None,  # None
                }
            ]
            result = client.get_fins_summary(code="1301")

            assert pd.isna(result["NxtFYSt"].iloc[0])
            assert pd.isna(result["NxtFYEn"].iloc[0])

    def test_sorted_by_discdate_disctime_code(self):
        """Result should be sorted by DiscDate, DiscTime, Code."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Code": "13020", "DiscDate": "2024-01-15", "DiscTime": "15:30:00"},
                {"Code": "13010", "DiscDate": "2024-01-15", "DiscTime": "15:30:00"},
                {"Code": "13010", "DiscDate": "2024-01-14", "DiscTime": "16:00:00"},
            ]
            result = client.get_fins_summary(date="2024-01-15")

            # Should be sorted: 2024-01-14 first, then 2024-01-15 with Code order
            assert result.iloc[0]["DiscDate"] == pd.Timestamp("2024-01-14")
            assert result.iloc[1]["Code"] == "13010"
            assert result.iloc[2]["Code"] == "13020"

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty API response should return empty DataFrame with all columns."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []
            result = client.get_fins_summary(code="1301")

            assert len(result) == 0
            assert list(result.columns) == constants_v2.FINS_SUMMARY_COLUMNS


class TestGetSummaryRange:
    """Test get_summary_range() method."""

    def test_calls_get_fins_summary_for_each_date(self):
        """get_summary_range() should call get_fins_summary for each date."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            client.get_summary_range("2024-01-01", "2024-01-03")

            # Should be called 3 times (Jan 1, 2, 3)
            assert mock_get.call_count == 3

    def test_default_end_date_is_today(self):
        """end_dt=None should default to today."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")
        today = date.today().isoformat()

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            # Use today as start to make test deterministic
            client.get_summary_range(today, None)

            # Should be called once for today
            assert mock_get.call_count == 1

    def test_start_after_end_raises_valueerror(self):
        """start_dt > end_dt should raise ValueError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_summary_range("2024-01-15", "2024-01-10")

        assert (
            "start" in str(exc_info.value).lower()
            or "end" in str(exc_info.value).lower()
        )

    def test_yyyymmdd_format_raises_valueerror(self):
        """YYYYMMDD format should raise ValueError."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError):
            client.get_summary_range("20240115", "20240120")

    def test_accepts_date_object(self):
        """Should accept date objects as parameters."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            client.get_summary_range(date(2024, 1, 1), date(2024, 1, 1))

            assert mock_get.call_count == 1

    def test_accepts_datetime_object(self):
        """Should accept datetime objects as parameters."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            client.get_summary_range(datetime(2024, 1, 1), datetime(2024, 1, 1))

            assert mock_get.call_count == 1

    def test_combined_result_has_all_columns(self):
        """Combined result should have all columns from FINS_SUMMARY_COLUMNS."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        def make_df(date):
            return pd.DataFrame(
                [{"Code": "13010", "DiscDate": date}],
                columns=constants_v2.FINS_SUMMARY_COLUMNS,
            )

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.side_effect = [make_df("2024-01-01"), make_df("2024-01-02")]
            result = client.get_summary_range("2024-01-01", "2024-01-02")

            assert list(result.columns) == constants_v2.FINS_SUMMARY_COLUMNS

    def test_result_sorted_by_discdate_disctime_code(self):
        """Combined result should be sorted by DiscDate, DiscTime, Code."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        def make_df(date, code):
            df = pd.DataFrame(columns=constants_v2.FINS_SUMMARY_COLUMNS)
            df.loc[0] = [None] * len(constants_v2.FINS_SUMMARY_COLUMNS)
            df.loc[0, "Code"] = code
            df.loc[0, "DiscDate"] = pd.Timestamp(date)
            df.loc[0, "DiscTime"] = "15:00:00"
            return df

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.side_effect = [
                make_df("2024-01-02", "13020"),
                make_df("2024-01-01", "13010"),
            ]
            result = client.get_summary_range("2024-01-01", "2024-01-02")

            assert result.iloc[0]["DiscDate"] == pd.Timestamp("2024-01-01")
            assert result.iloc[1]["DiscDate"] == pd.Timestamp("2024-01-02")

    def test_empty_range_returns_empty_dataframe(self):
        """Empty results should return empty DataFrame with all columns."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            result = client.get_summary_range("2024-01-01", "2024-01-01")

            assert len(result) == 0
            assert list(result.columns) == constants_v2.FINS_SUMMARY_COLUMNS

    def test_empty_range_has_consistent_date_dtypes(self):
        """Empty DataFrame should have datetime dtype for date columns (not object)."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_fins_summary") as mock_get:
            # Return empty DataFrame from each call
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )
            result = client.get_summary_range("2024-01-01", "2024-01-01")

            # Even for empty DataFrame, date columns should have proper dtype
            for col in constants_v2.FINS_SUMMARY_DATE_COLUMNS:
                assert pd.api.types.is_datetime64_any_dtype(
                    result[col]
                ), f"Empty DataFrame column {col} should have datetime dtype"

    def test_max_workers_1_sequential_execution(self):
        """max_workers=1 should execute sequentially (default)."""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=1)

        call_order = []

        def track_calls(date=""):
            call_order.append(date)
            return pd.DataFrame(columns=constants_v2.FINS_SUMMARY_COLUMNS)

        with patch.object(client, "get_fins_summary", side_effect=track_calls):
            client.get_summary_range("2024-01-01", "2024-01-02")

            # Calls should be in date order
            assert call_order == ["2024-01-01", "2024-01-02"]

    def test_max_workers_greater_than_1_uses_threadpool(self):
        """max_workers > 1 should use ThreadPoolExecutor for parallel execution."""
        from concurrent.futures import ThreadPoolExecutor

        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=3)

        with patch.object(client, "get_fins_summary") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants_v2.FINS_SUMMARY_COLUMNS
            )

            with patch(
                "jquants.client_v2.ThreadPoolExecutor", wraps=ThreadPoolExecutor
            ) as mock_pool:
                client.get_summary_range("2024-01-01", "2024-01-03")

                mock_pool.assert_called_once_with(max_workers=3)
