"""Tests for jquants.constants_v2 module."""

import pytest

from jquants import constants_v2


class TestColumnDefinitions:
    """Tests for V2 column definitions."""

    @pytest.mark.parametrize(
        "columns_name",
        [
            "EQUITIES_MASTER_COLUMNS",
            "EQUITIES_BARS_DAILY_COLUMNS",
            "EQUITIES_BARS_DAILY_AM_COLUMNS",
            "EQUITIES_EARNINGS_CALENDAR_COLUMNS",
            "EQUITIES_INVESTOR_TYPES_COLUMNS",
        ],
    )
    def test_columns_are_list_of_strings(self, columns_name: str):
        """C001: Each column list is list[str] type."""
        columns = getattr(constants_v2, columns_name)

        assert isinstance(columns, list)
        assert all(isinstance(col, str) for col in columns)
        assert len(columns) > 0

    @pytest.mark.parametrize(
        "columns_name",
        [
            "EQUITIES_MASTER_COLUMNS",
            "EQUITIES_BARS_DAILY_COLUMNS",
            "EQUITIES_BARS_DAILY_AM_COLUMNS",
            "EQUITIES_EARNINGS_CALENDAR_COLUMNS",
            "EQUITIES_INVESTOR_TYPES_COLUMNS",
        ],
    )
    def test_no_duplicate_columns(self, columns_name: str):
        """C002: No duplicate columns exist."""
        columns = getattr(constants_v2, columns_name)

        assert len(columns) == len(set(columns)), f"Duplicate found in {columns_name}"

    def test_adj_factor_correct_name(self):
        """C003: AdjFactor is correctly defined (not AdjFac)."""
        # Verify correct name is present
        assert "AdjFactor" in constants_v2.EQUITIES_BARS_DAILY_COLUMNS

        # Verify incorrect name is not present
        assert "AdjFac" not in constants_v2.EQUITIES_BARS_DAILY_COLUMNS


class TestEquitiesMasterColumns:
    """Tests for EQUITIES_MASTER_COLUMNS."""

    def test_contains_required_columns(self):
        """Master columns contain required fields."""
        required = ["Date", "Code", "CoName", "CoNameEn", "S17", "S33", "Mkt"]
        for col in required:
            assert col in constants_v2.EQUITIES_MASTER_COLUMNS


class TestEquitiesBarsDailyColumns:
    """Tests for EQUITIES_BARS_DAILY_COLUMNS."""

    def test_contains_ohlcv_columns(self):
        """Daily bars contain OHLCV columns."""
        required = ["Date", "Code", "O", "H", "L", "C", "Vo", "Va"]
        for col in required:
            assert col in constants_v2.EQUITIES_BARS_DAILY_COLUMNS

    def test_contains_adjusted_columns(self):
        """Daily bars contain adjusted price columns."""
        required = ["AdjFactor", "AdjO", "AdjH", "AdjL", "AdjC", "AdjVo"]
        for col in required:
            assert col in constants_v2.EQUITIES_BARS_DAILY_COLUMNS


class TestEquitiesInvestorTypesColumns:
    """Tests for EQUITIES_INVESTOR_TYPES_COLUMNS."""

    def test_uses_official_frgn_prefix(self):
        """Uses official Frgn* prefix (not For*)."""
        # Correct names (Frgn*)
        assert "FrgnSell" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS
        assert "FrgnBuy" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS

        # Incorrect names (For*) should not exist
        assert "ForSell" not in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS
        assert "ForBuy" not in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS

    def test_uses_official_secco_prefix(self):
        """Uses official SecCo* prefix."""
        assert "SecCoSell" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS
        assert "SecCoBuy" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS

    def test_uses_official_trstbnk_prefix(self):
        """Uses official TrstBnk* prefix (not TrBk*)."""
        assert "TrstBnkSell" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS
        assert "TrstBnkBuy" in constants_v2.EQUITIES_INVESTOR_TYPES_COLUMNS
