# indices/bars/daily/topix (`get_indices_topix`)

## スコープ

TOPIX指数の四本値（日次）。

## 読むタイミング

- `ClientV2.get_indices_topix()` または `INDICES_BARS_DAILY_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_indices_topix`
- `jquants/constants_v2.py`: `INDICES_BARS_DAILY_COLUMNS`
- 設計Issue (参照): #20

## API

- V2 パス: `/v2/indices/bars/daily/topix`
- メソッド: `ClientV2.get_indices_topix(from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `Code` (昇順)
- 主要カラム: `Date`, `Code`, `O`, `H`, `L`, `C` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。