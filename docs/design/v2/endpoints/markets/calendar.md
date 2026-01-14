# markets/calendar (`get_markets_trading_calendar`)

## スコープ

取引カレンダー。

## 読むタイミング

- `ClientV2.get_markets_trading_calendar()` または `MARKETS_CALENDAR_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_trading_calendar`
- `jquants/constants_v2.py`: `MARKETS_CALENDAR_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/calendar`
- メソッド: `ClientV2.get_markets_trading_calendar(holiday_division: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date` (昇順)
- 主要カラム: `Date`, `HolDiv` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。