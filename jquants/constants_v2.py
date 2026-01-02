"""V2 API column definitions.

Column names are based on official J-Quants V2 API specification:
- https://jpx-jquants.com/ja/spec/eq-bars-daily
- https://jpx-jquants.com/ja/spec/eq-investor-types
- https://jpx-jquants.com/ja/spec/eq-master

These column lists represent the recommended display order (superset).
Columns not present in API response are ignored by _to_dataframe().
"""

# equities/master - 銘柄マスター
EQUITIES_MASTER_COLUMNS = [
    "Date",
    "Code",
    "CoName",
    "CoNameEn",
    "S17",
    "S17Nm",
    "S33",
    "S33Nm",
    "ScaleCat",
    "Mkt",
    "MktNm",
    "Mrgn",  # Standard/Premium only
    "MrgnNm",  # Standard/Premium only
]

# equities/bars/daily - 株価四本値
EQUITIES_BARS_DAILY_COLUMNS = [
    "Date",
    "Code",
    "O",
    "H",
    "L",
    "C",
    "UL",
    "LL",
    "Vo",
    "Va",
    "AdjFactor",  # Official: AdjFactor (NOT AdjFac)
    "AdjO",
    "AdjH",
    "AdjL",
    "AdjC",
    "AdjVo",
    # Premium only (前場 - Morning session)
    "MO",
    "MH",
    "ML",
    "MC",
    "MUL",
    "MLL",
    "MVo",
    "MVa",
    "MAdjO",
    "MAdjH",
    "MAdjL",
    "MAdjC",
    "MAdjVo",
    # Premium only (後場 - Afternoon session)
    "AO",
    "AH",
    "AL",
    "AC",
    "AUL",
    "ALL",
    "AVo",
    "AVa",
    "AAdjO",
    "AAdjH",
    "AAdjL",
    "AAdjC",
    "AAdjVo",
]

# equities/bars/daily/am - 前場四本値
EQUITIES_BARS_DAILY_AM_COLUMNS = [
    "Date",
    "Code",
    "MO",
    "MH",
    "ML",
    "MC",
    "MVo",
    "MVa",
]

# equities/earnings-calendar - 決算発表日程
EQUITIES_EARNINGS_CALENDAR_COLUMNS = [
    "Code",
    "Date",
    "CoName",
    "FY",
    "SectorNm",
    "FQ",
    "Section",
]

# equities/investor-types - 投資部門別売買状況
EQUITIES_INVESTOR_TYPES_COLUMNS = [
    "Section",
    "PubDate",
    "StDate",
    "EnDate",
    # Proprietary
    "PropSell",
    "PropBuy",
    "PropTot",
    "PropBal",
    # Broker
    "BrkSell",
    "BrkBuy",
    "BrkTot",
    "BrkBal",
    # Total
    "TotSell",
    "TotBuy",
    "TotTot",
    "TotBal",
    # Individual
    "IndSell",
    "IndBuy",
    "IndTot",
    "IndBal",
    # Foreign - Official: Frgn* (NOT For*)
    "FrgnSell",
    "FrgnBuy",
    "FrgnTot",
    "FrgnBal",
    # Securities Companies - Official: SecCo*
    "SecCoSell",
    "SecCoBuy",
    "SecCoTot",
    "SecCoBal",
    # Investment Trusts
    "InvTrSell",
    "InvTrBuy",
    "InvTrTot",
    "InvTrBal",
    # Business Companies
    "BusCoSell",
    "BusCoBuy",
    "BusCoTot",
    "BusCoBal",
    # Other Companies
    "OthCoSell",
    "OthCoBuy",
    "OthCoTot",
    "OthCoBal",
    # Insurance Companies
    "InsCoSell",
    "InsCoBuy",
    "InsCoTot",
    "InsCoBal",
    # Banks
    "BankSell",
    "BankBuy",
    "BankTot",
    "BankBal",
    # Trust Banks - Official: TrstBnk* (NOT TrBk*)
    "TrstBnkSell",
    "TrstBnkBuy",
    "TrstBnkTot",
    "TrstBnkBal",
    # Other Financial Institutions
    "OthFinSell",
    "OthFinBuy",
    "OthFinTot",
    "OthFinBal",
]

# =============================================================================
# Markets endpoints
# =============================================================================

# markets/calendar - 取引カレンダー
# ref: https://jpx-jquants.com/ja/spec/mkt-cal
MARKETS_CALENDAR_COLUMNS = [
    "Date",
    "HolDiv",
]

# markets/margin-interest - 信用取引週末残高
# ref: https://jpx-jquants.com/ja/spec/mkt-margin-int
MARKETS_MARGIN_INTEREST_COLUMNS = [
    "Date",
    "Code",
    "ShrtVol",
    "LongVol",
    "ShrtNegVol",
    "LongNegVol",
    "ShrtStdVol",
    "LongStdVol",
    "IssType",
]

# markets/short-ratio - 業種別空売り比率
# ref: https://jpx-jquants.com/ja/spec/mkt-short-ratio
MARKETS_SHORT_RATIO_COLUMNS = [
    "Date",
    "S33",
    "SellExShortVa",
    "ShrtWithResVa",
    "ShrtNoResVa",
]

# markets/breakdown - 売買内訳データ
# ref: https://jpx-jquants.com/ja/spec/mkt-breakdown
MARKETS_BREAKDOWN_COLUMNS = [
    "Date",
    "Code",
    "LongSellVa",
    "ShrtNoMrgnVa",
    "MrgnSellNewVa",
    "MrgnSellCloseVa",
    "LongBuyVa",
    "MrgnBuyNewVa",
    "MrgnBuyCloseVa",
    "LongSellVo",
    "ShrtNoMrgnVo",
    "MrgnSellNewVo",
    "MrgnSellCloseVo",
    "LongBuyVo",
    "MrgnBuyNewVo",
    "MrgnBuyCloseVo",
]

# markets/short-sale-report - 空売り残高報告
# ref: https://jpx-jquants.com/ja/spec/mkt-short-sale
MARKETS_SHORT_SALE_REPORT_COLUMNS = [
    "DiscDate",
    "CalcDate",
    "Code",
    "SSName",
    "SSAddr",
    "DICName",
    "DICAddr",
    "FundName",
    "ShrtPosToSO",
    "ShrtPosShares",
    "ShrtPosUnits",
    "PrevRptDate",
    "PrevRptRatio",
    "Notes",
]

# markets/margin-alert - 信用取引残高（日々公表分）
# ref: https://jpx-jquants.com/ja/spec/mkt-margin-alert
# Note: PubReason is a nested object, flattened with dot notation
MARKETS_MARGIN_ALERT_COLUMNS = [
    "PubDate",
    "Code",
    "AppDate",
    "PubReason.Restricted",
    "PubReason.DailyPublication",
    "PubReason.Monitoring",
    "PubReason.RestrictedByJSF",
    "PubReason.PrecautionByJSF",
    "PubReason.UnclearOrSecOnAlert",
    "ShrtOut",
    "ShrtOutChg",
    "ShrtOutRatio",
    "LongOut",
    "LongOutChg",
    "LongOutRatio",
    "SLRatio",
    "ShrtNegOut",
    "ShrtNegOutChg",
    "ShrtStdOut",
    "ShrtStdOutChg",
    "LongNegOut",
    "LongNegOutChg",
    "LongStdOut",
    "LongStdOutChg",
    "TSEMrgnRegCls",
]

# =============================================================================
# Indices endpoints
# =============================================================================

# indices/bars/daily - 指数四本値
# indices/bars/daily/topix - TOPIX指数四本値
# ref: https://jpx-jquants.com/ja/spec/idx-bars-daily
# ref: https://jpx-jquants.com/ja/spec/idx-bars-daily-topix
# Note: Both endpoints share the same response schema
INDICES_BARS_DAILY_COLUMNS = [
    "Date",
    "Code",
    "O",
    "H",
    "L",
    "C",
]
