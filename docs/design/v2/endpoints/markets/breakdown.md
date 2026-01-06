# markets/breakdown (`get_markets_breakdown`)

## Scope

Markets breakdown data.

## When to read

- When changing `ClientV2.get_markets_breakdown()` or `MARKETS_BREAKDOWN_COLUMNS`.

## Source of truth

- `jquants/client_v2.py`: `ClientV2.get_markets_breakdown`
- `jquants/constants_v2.py`: `MARKETS_BREAKDOWN_COLUMNS`
- Design issue (Reference): #19

## API

- V2 path: `/v2/markets/breakdown`
- Method: `ClientV2.get_markets_breakdown(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame contract

- Sorted by: `Date`, `Code` (ascending)
- Major columns: `Date`, `Code`, `LongSellVa`, `ShrtNoMrgnVa`, `MrgnSellNewVa`, `LongBuyVa`, `MrgnBuyNewVa` (See `constants_v2.py` for full list)

## Range helper

- None.

