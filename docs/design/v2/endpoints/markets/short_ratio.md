# markets/short-ratio (`get_markets_short_selling`)

## スコープ

業種別空売り比率。

## 読むタイミング

- `ClientV2.get_markets_short_selling()` または `MARKETS_SHORT_RATIO_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_short_selling`
- `jquants/constants_v2.py`: `MARKETS_SHORT_RATIO_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/short-ratio`
- メソッド: `ClientV2.get_markets_short_selling(sector_33_code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `S33` (昇順)
- 主要カラム: `Date`, `S33`, `SellExShortVa`, `ShrtWithResVa`, `ShrtNoResVa` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。