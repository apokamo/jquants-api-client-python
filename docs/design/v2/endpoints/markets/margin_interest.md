# markets/margin-interest (`get_markets_weekly_margin_interest`)

## Scope

Weekly margin interest.

## When to read

- When changing `ClientV2.get_markets_weekly_margin_interest()` or `MARKETS_MARGIN_INTEREST_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_weekly_margin_interest`
- `jquants/constants_v2.py`: `MARKETS_MARGIN_INTEREST_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/margin-interest`
- Method: `ClientV2.get_markets_weekly_margin_interest(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date`, `Code` (ascending)
- Major columns: `Date`, `Code`, `ShrtVol`, `LongVol` (See `constants_v2.py` for full list)

## Range helper

- None.

