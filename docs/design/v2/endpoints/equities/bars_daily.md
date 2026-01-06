# equities/bars/daily (`get_prices_daily_quotes`)

## Scope

Equities daily OHLCV bars (四本値).

## When to read

- When changing `ClientV2.get_prices_daily_quotes()` or `EQUITIES_BARS_DAILY_COLUMNS`.
- When changing the date-range helper behavior for daily quotes.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_prices_daily_quotes`, `ClientV2.get_price_range`
- `jquants/constants_v2.py`: `EQUITIES_BARS_DAILY_COLUMNS`
- Design issue (Reference): #17

## API

- V2 path: `/v2/equities/bars/daily`
- Method: `ClientV2.get_prices_daily_quotes(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Code`, `Date` (ascending)
- Major columns: `Date`, `Code`, `O`, `H`, `L`, `C`, `Vo`, `AdjFactor` (See `constants_v2.py` for full list)

## Range helper

- Exists: `ClientV2.get_price_range(start_dt, end_dt=None)`
- Details: `docs/design/v2/core.md#range-helpers`

