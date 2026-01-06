# markets/short-ratio (`get_markets_short_selling`)

## Scope

Short selling ratio by 33 sector.

## When to read

- When changing `ClientV2.get_markets_short_selling()` or `MARKETS_SHORT_RATIO_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_short_selling`
- `jquants/constants_v2.py`: `MARKETS_SHORT_RATIO_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/short-ratio`
- Method: `ClientV2.get_markets_short_selling(sector_33_code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date`, `S33` (ascending)
- Major columns: `Date`, `S33`, `SellExShortVa`, `ShrtWithResVa`, `ShrtNoResVa` (See `constants_v2.py` for full list)

## Range helper

- None.

