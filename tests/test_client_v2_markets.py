"""Sub-Phase 3.3 TDD tests: ClientV2 Markets endpoints (6 methods)."""

from unittest.mock import patch

import pandas as pd

from jquants import ClientV2
from jquants import constants_v2 as constants


class TestGetMarketsTradingCalendar:
    """Test get_markets_trading_calendar() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-04", "HolDiv": "1"},
            ]

            result = client.get_markets_trading_calendar()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_trading_calendar()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_CALENDAR_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-04", "HolDiv": "1"},
            ]

            result = client.get_markets_trading_calendar()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_ascending(self):
        """Result should be sorted by Date ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"Date": "2024-01-05", "HolDiv": "1"},
                {"Date": "2024-01-04", "HolDiv": "1"},
            ]

            result = client.get_markets_trading_calendar()

            assert result.iloc[0]["Date"] < result.iloc[1]["Date"]

    def test_column_order_matches_constants(self):
        """Column order should match constants definition."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {"HolDiv": "1", "Date": "2024-01-04"},  # Wrong order in response
            ]

            result = client.get_markets_trading_calendar()

            assert list(result.columns) == constants.MARKETS_CALENDAR_COLUMNS

    def test_holiday_division_parameter_passed(self):
        """holiday_division parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_trading_calendar(holiday_division="1")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["hol_div"] == "1"

    def test_from_date_parameter_passed(self):
        """from_date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_trading_calendar(from_date="2024-01-01")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"

    def test_to_date_parameter_passed(self):
        """to_date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_trading_calendar(to_date="2024-01-31")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["to"] == "2024-01-31"

    def test_empty_parameters_not_included(self):
        """Empty string parameters should not be included in request."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_trading_calendar()

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert "hol_div" not in call_kwargs["params"]
            assert "from" not in call_kwargs["params"]
            assert "to" not in call_kwargs["params"]


class TestGetMarketsWeeklyMarginInterest:
    """Test get_markets_weekly_margin_interest() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-05",
                    "Code": "13010",
                    "ShrtVol": 1000,
                    "LongVol": 2000,
                    "ShrtNegVol": 500,
                    "LongNegVol": 1000,
                    "ShrtStdVol": 500,
                    "LongStdVol": 1000,
                    "IssType": "1",
                },
            ]

            result = client.get_markets_weekly_margin_interest()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_weekly_margin_interest()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_MARGIN_INTEREST_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-05",
                    "Code": "13010",
                    "ShrtVol": 1000,
                    "LongVol": 2000,
                    "ShrtNegVol": 500,
                    "LongNegVol": 1000,
                    "ShrtStdVol": 500,
                    "LongStdVol": 1000,
                    "IssType": "1",
                },
            ]

            result = client.get_markets_weekly_margin_interest()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_and_code_ascending(self):
        """Result should be sorted by Date, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-05",
                    "Code": "13020",
                    "ShrtVol": 0,
                    "LongVol": 0,
                    "ShrtNegVol": 0,
                    "LongNegVol": 0,
                    "ShrtStdVol": 0,
                    "LongStdVol": 0,
                    "IssType": "1",
                },
                {
                    "Date": "2024-01-05",
                    "Code": "13010",
                    "ShrtVol": 0,
                    "LongVol": 0,
                    "ShrtNegVol": 0,
                    "LongNegVol": 0,
                    "ShrtStdVol": 0,
                    "LongStdVol": 0,
                    "IssType": "1",
                },
            ]

            result = client.get_markets_weekly_margin_interest()

            assert result.iloc[0]["Code"] == "13010"
            assert result.iloc[1]["Code"] == "13020"

    def test_code_parameter_passed(self):
        """code parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_weekly_margin_interest(code="1301")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["code"] == "1301"

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_weekly_margin_interest(date="2024-01-05")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["date"] == "2024-01-05"

    def test_from_to_parameters_passed(self):
        """from_date and to_date parameters should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_weekly_margin_interest(
                from_date="2024-01-01",
                to_date="2024-01-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-01-31"

    def test_date_and_from_date_mutually_exclusive(self):
        """date and from_date/to_date are mutually exclusive."""
        import pytest

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_markets_weekly_margin_interest(
                date="2024-01-05",
                from_date="2024-01-01",
            )

        assert "mutually exclusive" in str(exc_info.value)


class TestGetMarketsShortSelling:
    """Test get_markets_short_selling() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "S33": "0050",
                    "SellExShortVa": 1000000,
                    "ShrtWithResVa": 500000,
                    "ShrtNoResVa": 200000,
                },
            ]

            result = client.get_markets_short_selling()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_short_selling()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_SHORT_RATIO_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "S33": "0050",
                    "SellExShortVa": 1000000,
                    "ShrtWithResVa": 500000,
                    "ShrtNoResVa": 200000,
                },
            ]

            result = client.get_markets_short_selling()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_and_s33_ascending(self):
        """Result should be sorted by Date, S33 ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "S33": "0100",
                    "SellExShortVa": 0,
                    "ShrtWithResVa": 0,
                    "ShrtNoResVa": 0,
                },
                {
                    "Date": "2024-01-04",
                    "S33": "0050",
                    "SellExShortVa": 0,
                    "ShrtWithResVa": 0,
                    "ShrtNoResVa": 0,
                },
            ]

            result = client.get_markets_short_selling()

            assert result.iloc[0]["S33"] == "0050"
            assert result.iloc[1]["S33"] == "0100"

    def test_sector_33_code_parameter_passed(self):
        """sector_33_code parameter should be passed to API as s33."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling(sector_33_code="0050")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["s33"] == "0050"

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling(date="2024-01-04")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["date"] == "2024-01-04"

    def test_from_to_parameters_passed(self):
        """from_date and to_date parameters should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling(
                from_date="2024-01-01",
                to_date="2024-01-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-01-31"

    def test_date_and_from_date_mutually_exclusive(self):
        """date and from_date/to_date are mutually exclusive."""
        import pytest

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_markets_short_selling(
                date="2024-01-04",
                from_date="2024-01-01",
            )

        assert "mutually exclusive" in str(exc_info.value)


class TestGetMarketsBreakdown:
    """Test get_markets_breakdown() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "13010",
                    "LongSellVa": 1000,
                    "ShrtNoMrgnVa": 500,
                    "MrgnSellNewVa": 200,
                    "MrgnSellCloseVa": 100,
                    "LongBuyVa": 1000,
                    "MrgnBuyNewVa": 200,
                    "MrgnBuyCloseVa": 100,
                    "LongSellVo": 100,
                    "ShrtNoMrgnVo": 50,
                    "MrgnSellNewVo": 20,
                    "MrgnSellCloseVo": 10,
                    "LongBuyVo": 100,
                    "MrgnBuyNewVo": 20,
                    "MrgnBuyCloseVo": 10,
                },
            ]

            result = client.get_markets_breakdown()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_breakdown()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_BREAKDOWN_COLUMNS

    def test_date_column_converted_to_timestamp(self):
        """Date column should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "13010",
                    "LongSellVa": 0,
                    "ShrtNoMrgnVa": 0,
                    "MrgnSellNewVa": 0,
                    "MrgnSellCloseVa": 0,
                    "LongBuyVa": 0,
                    "MrgnBuyNewVa": 0,
                    "MrgnBuyCloseVa": 0,
                    "LongSellVo": 0,
                    "ShrtNoMrgnVo": 0,
                    "MrgnSellNewVo": 0,
                    "MrgnSellCloseVo": 0,
                    "LongBuyVo": 0,
                    "MrgnBuyNewVo": 0,
                    "MrgnBuyCloseVo": 0,
                },
            ]

            result = client.get_markets_breakdown()

            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_sorted_by_date_and_code_ascending(self):
        """Result should be sorted by Date, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "Date": "2024-01-04",
                    "Code": "13020",
                    "LongSellVa": 0,
                    "ShrtNoMrgnVa": 0,
                    "MrgnSellNewVa": 0,
                    "MrgnSellCloseVa": 0,
                    "LongBuyVa": 0,
                    "MrgnBuyNewVa": 0,
                    "MrgnBuyCloseVa": 0,
                    "LongSellVo": 0,
                    "ShrtNoMrgnVo": 0,
                    "MrgnSellNewVo": 0,
                    "MrgnSellCloseVo": 0,
                    "LongBuyVo": 0,
                    "MrgnBuyNewVo": 0,
                    "MrgnBuyCloseVo": 0,
                },
                {
                    "Date": "2024-01-04",
                    "Code": "13010",
                    "LongSellVa": 0,
                    "ShrtNoMrgnVa": 0,
                    "MrgnSellNewVa": 0,
                    "MrgnSellCloseVa": 0,
                    "LongBuyVa": 0,
                    "MrgnBuyNewVa": 0,
                    "MrgnBuyCloseVa": 0,
                    "LongSellVo": 0,
                    "ShrtNoMrgnVo": 0,
                    "MrgnSellNewVo": 0,
                    "MrgnSellCloseVo": 0,
                    "LongBuyVo": 0,
                    "MrgnBuyNewVo": 0,
                    "MrgnBuyCloseVo": 0,
                },
            ]

            result = client.get_markets_breakdown()

            assert result.iloc[0]["Code"] == "13010"
            assert result.iloc[1]["Code"] == "13020"

    def test_code_parameter_passed(self):
        """code parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_breakdown(code="1301")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["code"] == "1301"

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_breakdown(date="2024-01-04")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["date"] == "2024-01-04"

    def test_from_to_parameters_passed(self):
        """from_date and to_date parameters should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_breakdown(
                from_date="2024-01-01",
                to_date="2024-01-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-01-31"

    def test_date_and_from_date_mutually_exclusive(self):
        """date and from_date/to_date are mutually exclusive."""
        import pytest

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_markets_breakdown(
                date="2024-01-04",
                from_date="2024-01-01",
            )

        assert "mutually exclusive" in str(exc_info.value)


class TestGetMarketsShortSellingPositions:
    """Test get_markets_short_selling_positions() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "DiscDate": "2024-01-04",
                    "CalcDate": "2024-01-03",
                    "Code": "13010",
                    "SSName": "Test Seller",
                    "SSAddr": "Tokyo",
                    "DICName": "",
                    "DICAddr": "",
                    "FundName": "",
                    "ShrtPosToSO": 0.5,
                    "ShrtPosShares": 10000,
                    "ShrtPosUnits": 100,
                    "PrevRptDate": "2024-01-02",
                    "PrevRptRatio": 0.4,
                    "Notes": "",
                },
            ]

            result = client.get_markets_short_selling_positions()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_short_selling_positions()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_SHORT_SALE_REPORT_COLUMNS

    def test_date_columns_converted_to_timestamp(self):
        """DiscDate, CalcDate, PrevRptDate should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "DiscDate": "2024-01-04",
                    "CalcDate": "2024-01-03",
                    "Code": "13010",
                    "SSName": "",
                    "SSAddr": "",
                    "DICName": "",
                    "DICAddr": "",
                    "FundName": "",
                    "ShrtPosToSO": 0,
                    "ShrtPosShares": 0,
                    "ShrtPosUnits": 0,
                    "PrevRptDate": "2024-01-02",
                    "PrevRptRatio": 0,
                    "Notes": "",
                },
            ]

            result = client.get_markets_short_selling_positions()

            assert pd.api.types.is_datetime64_any_dtype(result["DiscDate"])
            assert pd.api.types.is_datetime64_any_dtype(result["CalcDate"])
            assert pd.api.types.is_datetime64_any_dtype(result["PrevRptDate"])

    def test_sorted_by_discdate_calcdate_code_ascending(self):
        """Result should be sorted by DiscDate, CalcDate, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "DiscDate": "2024-01-04",
                    "CalcDate": "2024-01-03",
                    "Code": "13020",
                    "SSName": "",
                    "SSAddr": "",
                    "DICName": "",
                    "DICAddr": "",
                    "FundName": "",
                    "ShrtPosToSO": 0,
                    "ShrtPosShares": 0,
                    "ShrtPosUnits": 0,
                    "PrevRptDate": "2024-01-02",
                    "PrevRptRatio": 0,
                    "Notes": "",
                },
                {
                    "DiscDate": "2024-01-04",
                    "CalcDate": "2024-01-03",
                    "Code": "13010",
                    "SSName": "",
                    "SSAddr": "",
                    "DICName": "",
                    "DICAddr": "",
                    "FundName": "",
                    "ShrtPosToSO": 0,
                    "ShrtPosShares": 0,
                    "ShrtPosUnits": 0,
                    "PrevRptDate": "2024-01-02",
                    "PrevRptRatio": 0,
                    "Notes": "",
                },
            ]

            result = client.get_markets_short_selling_positions()

            assert result.iloc[0]["Code"] == "13010"
            assert result.iloc[1]["Code"] == "13020"

    def test_calc_date_parameter_passed(self):
        """calc_date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling_positions(calc_date="2024-01-03")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["calc_date"] == "2024-01-03"

    def test_disc_date_parameter_passed(self):
        """disc_date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling_positions(disc_date="2024-01-04")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["disc_date"] == "2024-01-04"

    def test_disc_date_from_to_parameters_passed(self):
        """disc_date_from and disc_date_to parameters should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_short_selling_positions(
                disc_date_from="2024-01-01",
                disc_date_to="2024-01-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["disc_date_from"] == "2024-01-01"
            assert call_kwargs["params"]["disc_date_to"] == "2024-01-31"

    def test_disc_date_and_disc_date_from_mutually_exclusive(self):
        """disc_date and disc_date_from/disc_date_to are mutually exclusive."""
        import pytest

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_markets_short_selling_positions(
                disc_date="2024-01-04",
                disc_date_from="2024-01-01",
            )

        assert "mutually exclusive" in str(exc_info.value)


class TestGetMarketsDailyMarginInterest:
    """Test get_markets_daily_margin_interest() method."""

    def test_returns_dataframe(self):
        """Should return a pandas DataFrame."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "PubDate": "2024-01-04",
                    "Code": "13010",
                    "AppDate": "2024-01-03",
                    "PubReason": {
                        "Restricted": "0",
                        "DailyPublication": "1",
                        "Monitoring": "0",
                        "RestrictedByJSF": "0",
                        "PrecautionByJSF": "0",
                        "UnclearOrSecOnAlert": "0",
                    },
                    "ShrtOut": 10000,
                    "ShrtOutChg": 100,
                    "ShrtOutRatio": 0.5,
                    "LongOut": 20000,
                    "LongOutChg": 200,
                    "LongOutRatio": 1.0,
                    "SLRatio": 50.0,
                    "ShrtNegOut": 5000,
                    "ShrtNegOutChg": 50,
                    "ShrtStdOut": 5000,
                    "ShrtStdOutChg": 50,
                    "LongNegOut": 10000,
                    "LongNegOutChg": 100,
                    "LongStdOut": 10000,
                    "LongStdOutChg": 100,
                    "TSEMrgnRegCls": "0",
                },
            ]

            result = client.get_markets_daily_margin_interest()

            assert isinstance(result, pd.DataFrame)

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        """Empty response should return empty DataFrame with correct columns."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            result = client.get_markets_daily_margin_interest()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == constants.MARKETS_MARGIN_ALERT_COLUMNS

    def test_date_columns_converted_to_timestamp(self):
        """PubDate and AppDate should be converted to pd.Timestamp."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "PubDate": "2024-01-04",
                    "Code": "13010",
                    "AppDate": "2024-01-03",
                    "PubReason": {
                        "Restricted": "0",
                        "DailyPublication": "1",
                        "Monitoring": "0",
                        "RestrictedByJSF": "0",
                        "PrecautionByJSF": "0",
                        "UnclearOrSecOnAlert": "0",
                    },
                    "ShrtOut": 0,
                    "ShrtOutChg": 0,
                    "ShrtOutRatio": 0,
                    "LongOut": 0,
                    "LongOutChg": 0,
                    "LongOutRatio": 0,
                    "SLRatio": 0,
                    "ShrtNegOut": 0,
                    "ShrtNegOutChg": 0,
                    "ShrtStdOut": 0,
                    "ShrtStdOutChg": 0,
                    "LongNegOut": 0,
                    "LongNegOutChg": 0,
                    "LongStdOut": 0,
                    "LongStdOutChg": 0,
                    "TSEMrgnRegCls": "0",
                },
            ]

            result = client.get_markets_daily_margin_interest()

            assert pd.api.types.is_datetime64_any_dtype(result["PubDate"])
            assert pd.api.types.is_datetime64_any_dtype(result["AppDate"])

    def test_nested_pubreason_flattened(self):
        """Nested PubReason object should be flattened with dot notation."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "PubDate": "2024-01-04",
                    "Code": "13010",
                    "AppDate": "2024-01-03",
                    "PubReason": {
                        "Restricted": "0",
                        "DailyPublication": "1",
                        "Monitoring": "0",
                        "RestrictedByJSF": "0",
                        "PrecautionByJSF": "0",
                        "UnclearOrSecOnAlert": "0",
                    },
                    "ShrtOut": 0,
                    "ShrtOutChg": 0,
                    "ShrtOutRatio": 0,
                    "LongOut": 0,
                    "LongOutChg": 0,
                    "LongOutRatio": 0,
                    "SLRatio": 0,
                    "ShrtNegOut": 0,
                    "ShrtNegOutChg": 0,
                    "ShrtStdOut": 0,
                    "ShrtStdOutChg": 0,
                    "LongNegOut": 0,
                    "LongNegOutChg": 0,
                    "LongStdOut": 0,
                    "LongStdOutChg": 0,
                    "TSEMrgnRegCls": "0",
                },
            ]

            result = client.get_markets_daily_margin_interest()

            assert "PubReason.DailyPublication" in result.columns
            assert result.iloc[0]["PubReason.DailyPublication"] == "1"

    def test_sorted_by_date_and_code_ascending(self):
        """Result should be sorted by PubDate, Code ascending."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = [
                {
                    "PubDate": "2024-01-04",
                    "Code": "13020",
                    "AppDate": "2024-01-03",
                    "PubReason": {
                        "Restricted": "0",
                        "DailyPublication": "1",
                        "Monitoring": "0",
                        "RestrictedByJSF": "0",
                        "PrecautionByJSF": "0",
                        "UnclearOrSecOnAlert": "0",
                    },
                    "ShrtOut": 0,
                    "ShrtOutChg": 0,
                    "ShrtOutRatio": 0,
                    "LongOut": 0,
                    "LongOutChg": 0,
                    "LongOutRatio": 0,
                    "SLRatio": 0,
                    "ShrtNegOut": 0,
                    "ShrtNegOutChg": 0,
                    "ShrtStdOut": 0,
                    "ShrtStdOutChg": 0,
                    "LongNegOut": 0,
                    "LongNegOutChg": 0,
                    "LongStdOut": 0,
                    "LongStdOutChg": 0,
                    "TSEMrgnRegCls": "0",
                },
                {
                    "PubDate": "2024-01-04",
                    "Code": "13010",
                    "AppDate": "2024-01-03",
                    "PubReason": {
                        "Restricted": "0",
                        "DailyPublication": "1",
                        "Monitoring": "0",
                        "RestrictedByJSF": "0",
                        "PrecautionByJSF": "0",
                        "UnclearOrSecOnAlert": "0",
                    },
                    "ShrtOut": 0,
                    "ShrtOutChg": 0,
                    "ShrtOutRatio": 0,
                    "LongOut": 0,
                    "LongOutChg": 0,
                    "LongOutRatio": 0,
                    "SLRatio": 0,
                    "ShrtNegOut": 0,
                    "ShrtNegOutChg": 0,
                    "ShrtStdOut": 0,
                    "ShrtStdOutChg": 0,
                    "LongNegOut": 0,
                    "LongNegOutChg": 0,
                    "LongStdOut": 0,
                    "LongStdOutChg": 0,
                    "TSEMrgnRegCls": "0",
                },
            ]

            result = client.get_markets_daily_margin_interest()

            assert result.iloc[0]["Code"] == "13010"
            assert result.iloc[1]["Code"] == "13020"

    def test_code_parameter_passed(self):
        """code parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_daily_margin_interest(code="1301")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["code"] == "1301"

    def test_date_parameter_passed(self):
        """date parameter should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_daily_margin_interest(date="2024-01-04")

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["date"] == "2024-01-04"

    def test_from_to_parameters_passed(self):
        """from_date and to_date parameters should be passed to API."""
        client = ClientV2(api_key="test_api_key")

        with patch.object(client, "_paginated_get") as mock_get:
            mock_get.return_value = []

            client.get_markets_daily_margin_interest(
                from_date="2024-01-01",
                to_date="2024-01-31",
            )

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["from"] == "2024-01-01"
            assert call_kwargs["params"]["to"] == "2024-01-31"

    def test_date_and_from_date_mutually_exclusive(self):
        """date and from_date/to_date are mutually exclusive."""
        import pytest

        client = ClientV2(api_key="test_api_key")

        with pytest.raises(ValueError) as exc_info:
            client.get_markets_daily_margin_interest(
                date="2024-01-04",
                from_date="2024-01-01",
            )

        assert "mutually exclusive" in str(exc_info.value)
