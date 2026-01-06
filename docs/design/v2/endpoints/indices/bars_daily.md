# indices/bars/daily (`get_indices`)

## Scope

Index daily OHLCV bars.

## When to read

- When changing `ClientV2.get_indices()` or `INDICES_BARS_DAILY_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_indices`
- `jquants/constants_v2.py`: `INDICES_BARS_DAILY_COLUMNS`
- Design issue (Reference): #20

## API

- V2 path: `/v2/indices/bars/daily`
- Method: `ClientV2.get_indices(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date`, `Code` (ascending)
- Major columns: `Date`, `Code`, `O`, `H`, `L`, `C` (See `constants_v2.py` for full list)

## Range helper

- None.

