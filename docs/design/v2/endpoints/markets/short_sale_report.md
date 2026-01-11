# markets/short-sale-report (`get_markets_short_selling_positions`)

## スコープ

空売り残高情報。

## 読むタイミング

- `ClientV2.get_markets_short_selling_positions()` または `MARKETS_SHORT_SALE_REPORT_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_short_selling_positions`
- `jquants/constants_v2.py`: `MARKETS_SHORT_SALE_REPORT_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/short-sale-report`
- メソッド: `ClientV2.get_markets_short_selling_positions(code: str = "", calc_date: str = "", disc_date: str = "", disc_date_from: str = "", disc_date_to: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `DiscDate`, `CalcDate`, `Code` (昇順)
- 主要カラム: `DiscDate`, `CalcDate`, `Code`, `SSName`, `ShrtPosToSO`, `ShrtPosShares` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。