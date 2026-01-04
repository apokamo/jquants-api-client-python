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

# =============================================================================
# Financials endpoints
# =============================================================================

# fins/summary - 決算短信サマリー
# ref: https://jpx-jquants.com/ja/spec/fin-summary
FINS_SUMMARY_COLUMNS = [
    # 基本情報
    "DiscDate",
    "DiscTime",
    "Code",
    "DiscNo",
    "DocType",
    # 会計期間
    "CurPerType",
    "CurPerSt",
    "CurPerEn",
    "CurFYSt",
    "CurFYEn",
    "NxtFYSt",
    "NxtFYEn",
    # 連結実績
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
    "CFO",
    "CFI",
    "CFF",
    "CashEq",
    # 配当実績
    "Div1Q",
    "Div2Q",
    "Div3Q",
    "DivFY",
    "DivAnn",
    "DivUnit",
    "DivTotalAnn",
    "PayoutRatioAnn",
    # 配当予想（当期）
    "FDiv1Q",
    "FDiv2Q",
    "FDiv3Q",
    "FDivFY",
    "FDivAnn",
    "FDivUnit",
    "FDivTotalAnn",
    "FPayoutRatioAnn",
    # 配当予想（翌期）
    "NxFDiv1Q",
    "NxFDiv2Q",
    "NxFDiv3Q",
    "NxFDivFY",
    "NxFDivAnn",
    "NxFDivUnit",
    "NxFPayoutRatioAnn",
    # 連結予想2Q
    "FSales2Q",
    "FOP2Q",
    "FOdP2Q",
    "FNP2Q",
    "FEPS2Q",
    "NxFSales2Q",
    "NxFOP2Q",
    "NxFOdP2Q",
    "NxFNp2Q",
    "NxFEPS2Q",
    # 連結予想期末
    "FSales",
    "FOP",
    "FOdP",
    "FNP",
    "FEPS",
    "NxFSales",
    "NxFOP",
    "NxFOdP",
    "NxFNp",
    "NxFEPS",
    # 会計方針変更
    "MatChgSub",
    "SigChgInC",
    "ChgByASRev",
    "ChgNoASRev",
    "ChgAcEst",
    "RetroRst",
    # 株式数
    "ShOutFY",
    "TrShFY",
    "AvgSh",
    # 非連結実績
    "NCSales",
    "NCOP",
    "NCOdP",
    "NCNP",
    "NCEPS",
    "NCTA",
    "NCEq",
    "NCEqAR",
    "NCBPS",
    # 非連結予想2Q
    "FNCSales2Q",
    "FNCOP2Q",
    "FNCOdP2Q",
    "FNCNP2Q",
    "FNCEPS2Q",
    "NxFNCSales2Q",
    "NxFNCOP2Q",
    "NxFNCOdP2Q",
    "NxFNCNP2Q",
    "NxFNCEPS2Q",
    # 非連結予想期末
    "FNCSales",
    "FNCOP",
    "FNCOdP",
    "FNCNP",
    "FNCEPS",
    "NxFNCSales",
    "NxFNCOP",
    "NxFNCOdP",
    "NxFNCNP",
    "NxFNCEPS",
]

# 日付型として扱うカラム
FINS_SUMMARY_DATE_COLUMNS = [
    "DiscDate",
    "CurPerSt",
    "CurPerEn",
    "CurFYSt",
    "CurFYEn",
    "NxtFYSt",
    "NxtFYEn",
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

# =============================================================================
# Derivatives endpoints
# =============================================================================

# derivatives/bars/daily/options/225 - 日経225オプション日足
# ref: https://jpx-jquants.com/ja/spec/drv-bars-daily-opt-225
DERIVATIVES_OPTIONS_225_COLUMNS = [
    # 基本情報
    "Date",
    "Code",
    # 全セッションOHLC
    "O",
    "H",
    "L",
    "C",
    # 夜間セッションOHLC（初回取引日は空文字）
    "EO",
    "EH",
    "EL",
    "EC",
    # 日中セッションOHLC
    "AO",
    "AH",
    "AL",
    "AC",
    # 出来高・建玉
    "Vo",
    "OI",
    "Va",
    "VoOA",
    # 契約情報
    "CM",
    "Strike",
    "PCDiv",
    # 期日情報
    "LTD",
    "SQD",
    # 価格・ボラティリティ（2016-07-19以降のみ）
    "Settle",
    "Theo",
    "BaseVol",
    "UnderPx",
    "IV",
    "IR",
    # 管理区分
    "EmMrgnTrgDiv",
]

# 日付型として扱うカラム
DERIVATIVES_OPTIONS_225_DATE_COLUMNS = ["Date", "LTD", "SQD"]

# 数値型変換が必要なカラム（夜間セッションは初回取引日で空文字となる）
DERIVATIVES_OPTIONS_225_NUMERIC_COLUMNS = ["EO", "EH", "EL", "EC"]
