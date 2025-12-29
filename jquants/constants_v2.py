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
