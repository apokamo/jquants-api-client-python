"""Sub-Phase 3.4 TDD tests: ClientV2 Indices endpoints (2 methods)."""

from unittest.mock import patch

import pandas as pd
import pytest

from jquants import ClientV2
from jquants import constants_v2 as constants


class TestGetIndices:
    """Test get_indices() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "0000",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 90.0,
                    "C": 105.0,
                },
            ]

            result = client.get_indices(code="0000")

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_indices(code="0000")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.INDICES_BARS_DAILY_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "0000",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 90.0,
                    "C": 105.0,
                },
            ]

            result = client.get_indices(code="0000")

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_code_ascending(self):
        """Result should be sorted by Date, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-05",
                    "Code": "0001",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 90.0,
                    "C": 105.0,
                },
                {
                    "Date": "2024-01-04",
                    "Code": "0000",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 90.0,
                    "C": 105.0,
                },
                {
                    "Date": "2024-01-04",
                    "Code": "0001",
                    "O": 100.0,
                    "H": 110.0,
                    "L": 90.0,
                    "C": 105.0,
                },
            ]

            result = client.get_indices(code="0000")

            # Check Date ascending
            assert result.iloc[0]["Date"] <= result.iloc[1]["Date"]
            # Check Code ascending for same date
            same_date_rows = result[result["Date"] == pd.Timestamp("2024-01-04")]
            if len(same_date_rows) > 1:
                assert same_date_rows.iloc[0]["Code"] < same_date_rows.iloc[1]["Code"]

    def test_column_order_matches_constants(self):
        """Column order should match constants definition."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "C": 105.0,
                    "L": 90.0,
                    "H": 110.0,
                    "O": 100.0,
                    "Code": "0000",
                    "Date": "2024-01-04",
                },
            ]

            result = client.get_indices(code="0000")

            assert list(result.columns) == constants.INDICES_BARS_DAILY_COLUMNS

    def test_code_parameter_passed(self):
        """code parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(code="0000")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["code"] == "0000"

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(date="2024-01-04")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["date"] == "2024-01-04"

    def test_from_date_parameter_passed(self):
        """from_date parameter should be passed to API as 'from'."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(code="0000", from_date="2024-01-01")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == "2024-01-01"

    def test_to_date_parameter_passed(self):
        """to_date parameter should be passed to API as 'to'."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(code="0000", to_date="2024-01-31")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["to"] == "2024-01-31"

    def test_empty_parameters_not_included(self):
        """Empty string parameters should not be included in request."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(code="0000")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "date" not in call_args[1]["params"]
            assert "from" not in call_args[1]["params"]
            assert "to" not in call_args[1]["params"]

    def test_raises_value_error_when_code_and_date_both_empty(self):
        """Should raise ValueError when both code and date are empty."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_indices()

        assert (
            "code" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        )

    def test_raises_value_error_when_date_and_from_date_both_specified(self):
        """Should raise ValueError when date and from_date are both specified."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_indices(code="0000", date="2024-01-04", from_date="2024-01-01")

        assert "mutually exclusive" in str(exc_info.value).lower()

    def test_raises_value_error_when_date_and_to_date_both_specified(self):
        """Should raise ValueError when date and to_date are both specified."""
        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_indices(code="0000", date="2024-01-04", to_date="2024-01-31")

        assert "mutually exclusive" in str(exc_info.value).lower()

    def test_api_path_is_correct(self):
        """API path should be /indices/bars/daily."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices(code="0000")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/indices/bars/daily"


class TestGetIndicesTopix:
    """Test get_indices_topix() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "TOPIX",
                    "O": 2400.0,
                    "H": 2450.0,
                    "L": 2380.0,
                    "C": 2420.0,
                },
            ]

            result = client.get_indices_topix()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_indices_topix()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.INDICES_BARS_DAILY_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "TOPIX",
                    "O": 2400.0,
                    "H": 2450.0,
                    "L": 2380.0,
                    "C": 2420.0,
                },
            ]

            result = client.get_indices_topix()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_code_ascending(self):
        """Result should be sorted by Date, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-05",
                    "Code": "TOPIX",
                    "O": 2400.0,
                    "H": 2450.0,
                    "L": 2380.0,
                    "C": 2420.0,
                },
                {
                    "Date": "2024-01-04",
                    "Code": "TOPIX",
                    "O": 2400.0,
                    "H": 2450.0,
                    "L": 2380.0,
                    "C": 2420.0,
                },
            ]

            result = client.get_indices_topix()

            assert result.iloc[0]["Date"] < result.iloc[1]["Date"]

    def test_column_order_matches_constants(self):
        """Column order should match constants definition."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "C": 2420.0,
                    "L": 2380.0,
                    "H": 2450.0,
                    "O": 2400.0,
                    "Code": "TOPIX",
                    "Date": "2024-01-04",
                },
            ]

            result = client.get_indices_topix()

            assert list(result.columns) == constants.INDICES_BARS_DAILY_COLUMNS

    def test_from_date_parameter_passed(self):
        """from_date parameter should be passed to API as 'from'."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices_topix(from_date="2024-01-01")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == "2024-01-01"

    def test_to_date_parameter_passed(self):
        """to_date parameter should be passed to API as 'to'."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices_topix(to_date="2024-01-31")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["to"] == "2024-01-31"

    def test_empty_parameters_not_included(self):
        """Empty string parameters should not be included in request."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices_topix()

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "from" not in call_args[1]["params"]
            assert "to" not in call_args[1]["params"]

    def test_no_required_parameters(self):
        """Should work without any parameters (no ValueError)."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            # Should not raise
            result = client.get_indices_topix()

            assert isinstance(result, pd.DataFrame)

    def test_api_path_is_correct(self):
        """API path should be /indices/bars/daily/topix."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_indices_topix()

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/indices/bars/daily/topix"
