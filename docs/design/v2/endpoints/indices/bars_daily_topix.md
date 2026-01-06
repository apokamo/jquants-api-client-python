# indices/bars/daily/topix (`get_indices_topix`)

## Scope

TOPIX index daily OHLCV bars.

## When to read

- When changing `ClientV2.get_indices_topix()` or `INDICES_BARS_DAILY_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_indices_topix`
- `jquants/constants_v2.py`: `INDICES_BARS_DAILY_COLUMNS`
- Design issue (Reference): #20

## API

- V2 path: `/v2/indices/bars/daily/topix`
- Method: `ClientV2.get_indices_topix(from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date`, `Code` (ascending)
- Major columns: `Date`, `Code`, `O`, `H`, `L`, `C` (See `constants_v2.py` for full list)

## Range helper

- None.

