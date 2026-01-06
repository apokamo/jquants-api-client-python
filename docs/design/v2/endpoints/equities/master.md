# equities/master (`get_listed_info`)

## Scope

Listed issue (master) data for equities.

## When to read

- When changing `ClientV2.get_listed_info()` or `EQUITIES_MASTER_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_listed_info`
- `jquants/constants_v2.py`: `EQUITIES_MASTER_COLUMNS`
- Design issue (Reference): #17

## API

- V2 path: `/v2/equities/master`
- Method: `ClientV2.get_listed_info(code: str = "", date: str = "")`

## DataFrame contract

- Sorted by: `Code` (ascending)
- Major columns: `Date`, `Code`, `CoName`, `S17`, `S33`, `Mkt` (See `constants_v2.py` for full list)

## Range helper

- None.

