# markets/breakdown (`get_markets_breakdown`)

## スコープ

売買内訳データ。

## 読むタイミング

- `ClientV2.get_markets_breakdown()` または `MARKETS_BREAKDOWN_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_breakdown`
- `jquants/constants_v2.py`: `MARKETS_BREAKDOWN_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/breakdown`
- メソッド: `ClientV2.get_markets_breakdown(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `Code` (昇順)
- 主要カラム: `Date`, `Code`, `LongSellVa`, `ShrtNoMrgnVa`, `MrgnSellNewVa`, `LongBuyVa`, `MrgnBuyNewVa` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。