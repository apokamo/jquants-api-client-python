# equities/master (`get_listed_info`)

## スコープ

株式の銘柄一覧（マスター）データ。

## 読むタイミング

- `ClientV2.get_listed_info()` または `EQUITIES_MASTER_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_listed_info`
- `jquants/constants_v2.py`: `EQUITIES_MASTER_COLUMNS`
- 設計Issue (参照): #17

## API

- V2 パス: `/v2/equities/master`
- メソッド: `ClientV2.get_listed_info(code: str = "", date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Code` (昇順)
- 主要カラム: `Date`, `Code`, `CoName`, `S17`, `S33`, `Mkt` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。