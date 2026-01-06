# markets/short-sale-report (`get_markets_short_selling_positions`)

## Scope

Short selling positions (short sale report).

## When to read

- When changing `ClientV2.get_markets_short_selling_positions()` or `MARKETS_SHORT_SALE_REPORT_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_short_selling_positions`
- `jquants/constants_v2.py`: `MARKETS_SHORT_SALE_REPORT_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/short-sale-report`
- Method: `ClientV2.get_markets_short_selling_positions(code: str = "", calc_date: str = "", disc_date: str = "", disc_date_from: str = "", disc_date_to: str = "")`

## DataFrame contract

- Sorted by: `DiscDate`, `CalcDate`, `Code` (ascending)
- Major columns: `DiscDate`, `CalcDate`, `Code`, `SSName`, `ShrtPosToSO`, `ShrtPosShares` (See `constants_v2.py` for full list)

## Range helper

- None.

