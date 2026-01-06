# markets/margin-alert (`get_markets_daily_margin_interest`)

## Scope

Daily margin interest (margin alert), includes nested `PubReason` fields.

## When to read

- When changing `ClientV2.get_markets_daily_margin_interest()` or `MARKETS_MARGIN_ALERT_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_daily_margin_interest`
- `jquants/constants_v2.py`: `MARKETS_MARGIN_ALERT_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/margin-alert`
- Method: `ClientV2.get_markets_daily_margin_interest(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `PubDate`, `Code` (ascending)
- Major columns: `PubDate`, `Code`, `AppDate`, `ShrtOut`, `LongOut` (See `constants_v2.py` for full list)

## Range helper

- None.

