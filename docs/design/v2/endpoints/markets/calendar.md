# markets/calendar (`get_markets_trading_calendar`)

## Scope

Trading calendar.

## When to read

- When changing `ClientV2.get_markets_trading_calendar()` or `MARKETS_CALENDAR_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_trading_calendar`
- `jquants/constants_v2.py`: `MARKETS_CALENDAR_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/calendar`
- Method: `ClientV2.get_markets_trading_calendar(holiday_division: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date` (ascending)
- Major columns: `Date`, `HolDiv` (See `constants_v2.py` for full list)

## Range helper

- None.

