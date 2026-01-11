# indices/bars/daily (`get_indices`)

## スコープ

指数の四本値（日次）。

## 読むタイミング

- `ClientV2.get_indices()` または `INDICES_BARS_DAILY_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_indices`
- `jquants/constants_v2.py`: `INDICES_BARS_DAILY_COLUMNS`
- 設計Issue (参照): #20

## API

- V2 パス: `/v2/indices/bars/daily`
- メソッド: `ClientV2.get_indices(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `Code` (昇順)
- 主要カラム: `Date`, `Code`, `O`, `H`, `L`, `C` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。