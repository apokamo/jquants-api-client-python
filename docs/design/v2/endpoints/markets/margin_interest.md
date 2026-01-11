# markets/margin-interest (`get_markets_weekly_margin_interest`)

## スコープ

信用取引週末残高。

## 読むタイミング

- `ClientV2.get_markets_weekly_margin_interest()` または `MARKETS_MARGIN_INTEREST_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_weekly_margin_interest`
- `jquants/constants_v2.py`: `MARKETS_MARGIN_INTEREST_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/margin-interest`
- メソッド: `ClientV2.get_markets_weekly_margin_interest(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `Code` (昇順)
- 主要カラム: `Date`, `Code`, `ShrtVol`, `LongVol` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。