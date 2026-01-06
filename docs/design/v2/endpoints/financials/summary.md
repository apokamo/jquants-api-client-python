# fins/summary (`get_fins_summary`)

## Scope

Financials summary (決算短信サマリー).

## When to read

- When changing `ClientV2.get_fins_summary()` or `FINS_SUMMARY_COLUMNS`.
- When changing the date-range helper behavior for summaries.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_fins_summary`, `ClientV2.get_summary_range`
- `jquants/constants_v2.py`: `FINS_SUMMARY_COLUMNS`, `FINS_SUMMARY_DATE_COLUMNS`
- Design issue (Reference): #21

## API

- V2 path: `/v2/fins/summary`
- Method: `ClientV2.get_fins_summary(code: str = "", date: str = "")`

## DataFrame contract

- Sorted by: `DiscDate`, `DiscTime`, `Code` (ascending)
- Major columns: `DiscDate`, `Code`, `Sales`, `OP`, `NP`, `EPS`, `DivAnn` (See `constants_v2.py` for full list)

## Range helper

- Exists: `ClientV2.get_summary_range(start_dt, end_dt=None)`
- Details: `docs/design/v2/core.md#range-helpers`

