# fins/summary (`get_fins_summary`)

## スコープ

財務情報（決算短信サマリー）。

## 読むタイミング

- `ClientV2.get_fins_summary()` または `FINS_SUMMARY_COLUMNS` を変更するとき。
- 財務情報の期間指定取得ヘルパーの挙動を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_fins_summary`, `ClientV2.get_summary_range`
- `jquants/constants_v2.py`: `FINS_SUMMARY_COLUMNS`, `FINS_SUMMARY_DATE_COLUMNS`
- 設計Issue (参照): #21

## API

- V2 パス: `/v2/fins/summary`
- メソッド: `ClientV2.get_fins_summary(code: str = "", date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `DiscDate`, `DiscTime`, `Code` (昇順)
- 主要カラム: `DiscDate`, `Code`, `Sales`, `OP`, `NP`, `EPS`, `DivAnn` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- あり: `ClientV2.get_summary_range(start_dt, end_dt=None)`
- 詳細: `docs/design/v2/core.md#range-helpers`