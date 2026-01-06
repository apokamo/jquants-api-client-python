# derivatives/bars/daily/options/225 (`get_options_225_daily`)

## Scope

Nikkei 225 options daily bars.

## When to read

- When changing `ClientV2.get_options_225_daily()` or `DERIVATIVES_OPTIONS_225_COLUMNS`.
- When changing the date-range helper behavior for options.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_options_225_daily`, `ClientV2.get_options_225_daily_range`
- `jquants/constants_v2.py`: `DERIVATIVES_OPTIONS_225_COLUMNS`, `DERIVATIVES_OPTIONS_225_DATE_COLUMNS`, `DERIVATIVES_OPTIONS_225_NUMERIC_COLUMNS`
- Design issue (Reference): #25 (note: method naming differs; docs follow the current implementation)

## API

- V2 path: `/v2/derivatives/bars/daily/options/225`
- Method: `ClientV2.get_options_225_daily(date: str)`

## DataFrame contract

- Sorted by: `Code` (ascending)
- Major columns: `Date`, `Code`, `Strike`, `PCDiv`, `O`, `H`, `L`, `C`, `OI`, `IV` (See `constants_v2.py` for full list)

## Range helper

- Exists: `ClientV2.get_options_225_daily_range(start_dt, end_dt=None)`
- Details: `docs/design/v2/core.md#range-helpers`

