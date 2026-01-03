"""Sub-Phase 3.6 TDD tests: ClientV2 Derivatives endpoints."""

from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from jquants import ClientV2
from jquants import constants_v2 as constants


class TestGetIndexOption:
    """Test get_index_option() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "188010019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": "",
                    "EH": "",
                    "EL": "",
                    "EC": "",
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 36000,
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert isinstance(result, pd.DataFrame)

    def test_date_parameter_required(self):
        """date parameter is required - should raise TypeError if missing."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(TypeError):
            client.get_index_option()  # type: ignore

    def test_date_empty_string_raises_valueerror(self):
        """Empty string date should raise ValueError."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_index_option(date="")

        assert "'date' is required" in str(exc_info.value)

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_index_option(date="2024-01-04")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["date"] == "2024-01-04"

    def test_correct_api_path_called(self):
        """Should call the correct API path."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_index_option(date="2024-01-04")

            mock_get.assert_called_once_with(
                "/derivatives/bars/daily/options/225",
                params={"date": "2024-01-04"},
            )

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_index_option(date="2024-01-04")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.DERIVATIVES_OPTIONS_225_COLUMNS

    def test_date_columns_converted_to_timestamp(self):
        """Date, LTD, SQD columns should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "188010019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": 99.0,
                    "EH": 100.0,
                    "EL": 98.0,
                    "EC": 99.5,
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 36000,
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])
            assert pd.api.types.is_datetime64_any_dtype(result["LTD"])
            assert pd.api.types.is_datetime64_any_dtype(result["SQD"])

    def test_date_columns_empty_string_becomes_nat(self):
        """Empty string in date columns should become pd.NaT."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "188010019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": "",
                    "EH": "",
                    "EL": "",
                    "EC": "",
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 36000,
                    "PCDiv": "1",
                    "LTD": "",
                    "SQD": "",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert pd.isna(result.iloc[0]["LTD"])
            assert pd.isna(result.iloc[0]["SQD"])

    def test_numeric_columns_empty_string_becomes_nan(self):
        """Empty string in EO/EH/EL/EC should become NaN."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "188010019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": "",
                    "EH": "",
                    "EL": "",
                    "EC": "",
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 36000,
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert pd.isna(result.iloc[0]["EO"])
            assert pd.isna(result.iloc[0]["EH"])
            assert pd.isna(result.iloc[0]["EL"])
            assert pd.isna(result.iloc[0]["EC"])

    def test_sorted_by_code_ascending(self):
        """Result should be sorted by Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "188020019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": 99.0,
                    "EH": 100.0,
                    "EL": 98.0,
                    "EC": 99.5,
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 37000,
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
                {
                    "Date": "2024-01-04",
                    "Code": "188010019",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": 99.0,
                    "EH": 100.0,
                    "EL": 98.0,
                    "EC": 99.5,
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "Strike": 36000,
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert result.iloc[0]["Code"] == "188010019"
            assert result.iloc[1]["Code"] == "188020019"

    def test_column_order_matches_constants(self):
        """Column order should match constants definition."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            # Response with columns in different order
            mock_get.return_value = [
                {
                    "Code": "188010019",
                    "Date": "2024-01-04",
                    "Strike": 36000,
                    "O": 100.0,
                    "H": 110.0,
                    "L": 95.0,
                    "C": 105.0,
                    "EO": 99.0,
                    "EH": 100.0,
                    "EL": 98.0,
                    "EC": 99.5,
                    "AO": 100.0,
                    "AH": 110.0,
                    "AL": 95.0,
                    "AC": 105.0,
                    "Vo": 1000,
                    "OI": 5000,
                    "Va": 10500000,
                    "VoOA": 100,
                    "CM": "2024-01",
                    "PCDiv": "1",
                    "LTD": "2024-01-12",
                    "SQD": "2024-01-12",
                    "Settle": 105.0,
                    "Theo": 104.5,
                    "BaseVol": 0.15,
                    "UnderPx": 36500.0,
                    "IV": 0.16,
                    "IR": 0.01,
                    "EmMrgnTrgDiv": "0",
                },
            ]

            result = client.get_index_option(date="2024-01-04")

            assert list(result.columns) == constants.DERIVATIVES_OPTIONS_225_COLUMNS


class TestGetIndexOptionRange:
    """Test get_index_option_range() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                {
                    "Date": pd.to_datetime(["2024-01-04"]),
                    "Code": ["188010019"],
                }
            )

            result = client.get_index_option_range(start_dt="2024-01-04")

            assert isinstance(result, pd.DataFrame)

    def test_start_dt_required(self):
        """start_dt parameter is required."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(TypeError):
            client.get_index_option_range()  # type: ignore

    def test_end_dt_defaults_to_today(self):
        """end_dt should default to today if not specified."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            today = date.today().isoformat()
            client.get_index_option_range(start_dt=today)

            # Should be called once for today
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert call_args["date"] == today

    def test_start_dt_after_end_dt_raises_error(self):
        """start_dt > end_dt should raise ValueError."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_index_option_range(
                start_dt="2024-01-10",
                end_dt="2024-01-01",
            )

        assert "must not be after" in str(exc_info.value)

    def test_date_range_generates_correct_calls(self):
        """Should call get_index_option for each date in range."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            client.get_index_option_range(
                start_dt="2024-01-04",
                end_dt="2024-01-06",
            )

            # Should call for 3 days: 2024-01-04, 2024-01-05, 2024-01-06
            assert mock_get.call_count == 3
            dates_called = [call[1]["date"] for call in mock_get.call_args_list]
            assert dates_called == ["2024-01-04", "2024-01-05", "2024-01-06"]

    def test_accepts_string_date(self):
        """Should accept string date format."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            client.get_index_option_range(
                start_dt="2024-01-04",
                end_dt="2024-01-04",
            )

            mock_get.assert_called_once()

    def test_accepts_date_object(self):
        """Should accept date object."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            client.get_index_option_range(
                start_dt=date(2024, 1, 4),
                end_dt=date(2024, 1, 4),
            )

            mock_get.assert_called_once()

    def test_accepts_datetime_object(self):
        """Should accept datetime object."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            client.get_index_option_range(
                start_dt=datetime(2024, 1, 4, 10, 0, 0),
                end_dt=datetime(2024, 1, 4, 15, 0, 0),
            )

            mock_get.assert_called_once()

    def test_empty_period_returns_empty_dataframe_with_columns(self):
        """Empty period should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            result = client.get_index_option_range(
                start_dt="2024-01-04",
                end_dt="2024-01-04",
            )

            assert isinstance(result, pd.DataFrame)
            assert list(result.columns) == constants.DERIVATIVES_OPTIONS_225_COLUMNS

    def test_sorted_by_code_and_date_ascending(self):
        """Result should be sorted by Code, Date ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "get_index_option") as mock_get:
            # Return data in wrong order
            mock_get.side_effect = [
                pd.DataFrame(
                    {
                        "Date": pd.to_datetime(["2024-01-05"]),
                        "Code": ["188010019"],
                        **{
                            col: [0]
                            for col in constants.DERIVATIVES_OPTIONS_225_COLUMNS
                            if col not in ["Date", "Code"]
                        },
                    }
                ),
                pd.DataFrame(
                    {
                        "Date": pd.to_datetime(["2024-01-04"]),
                        "Code": ["188010019"],
                        **{
                            col: [0]
                            for col in constants.DERIVATIVES_OPTIONS_225_COLUMNS
                            if col not in ["Date", "Code"]
                        },
                    }
                ),
            ]

            result = client.get_index_option_range(
                start_dt="2024-01-04",
                end_dt="2024-01-05",
            )

            # Should be sorted by Code, Date
            assert result.iloc[0]["Date"] < result.iloc[1]["Date"]

    def test_sequential_execution_with_max_workers_1(self):
        """Should execute sequentially when max_workers=1 (default)."""
        client = ClientV2(api_key="test_api_key", max_workers=1)

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            client.get_index_option_range(
                start_dt="2024-01-04",
                end_dt="2024-01-05",
            )

            # Sequential: 2 calls
            assert mock_get.call_count == 2

    def test_parallel_execution_with_max_workers_greater_than_1(self):
        """Should execute in parallel when max_workers > 1."""
        client = ClientV2(api_key="test_api_key", max_workers=2)

        with patch.object(client, "get_index_option") as mock_get:
            mock_get.return_value = pd.DataFrame(
                columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS
            )

            with patch("jquants.client_v2.ThreadPoolExecutor") as mock_executor_class:
                mock_executor = mock_executor_class.return_value.__enter__.return_value
                mock_executor.map.return_value = [
                    pd.DataFrame(columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS),
                    pd.DataFrame(columns=constants.DERIVATIVES_OPTIONS_225_COLUMNS),
                ]

                client.get_index_option_range(
                    start_dt="2024-01-04",
                    end_dt="2024-01-05",
                )

                # ThreadPoolExecutor should be used
                mock_executor_class.assert_called_once_with(max_workers=2)
