# equities/earnings-calendar (`get_fins_announcement`)

## Scope

Earnings announcement calendar.

## When to read

- When changing `ClientV2.get_fins_announcement()` or `EQUITIES_EARNINGS_CALENDAR_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_fins_announcement`
- `jquants/constants_v2.py`: `EQUITIES_EARNINGS_CALENDAR_COLUMNS`
- Design issue (Reference): #17

## API

- V2 path: `/v2/equities/earnings-calendar`
- Method: `ClientV2.get_fins_announcement()`

## DataFrame contract

- Sorted by: `Date`, `Code` (ascending)
- Major columns: `Date`, `Code`, `CoName`, `FY`, `FQ` (See `constants_v2.py` for full list)

## Range helper

- None.

