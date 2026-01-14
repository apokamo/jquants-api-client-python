# derivatives/bars/daily/options/225 (`get_options_225_daily`)

## スコープ

日経225オプションの四本値（日次）。

## 読むタイミング

- `ClientV2.get_options_225_daily()` または `DERIVATIVES_OPTIONS_225_COLUMNS` を変更するとき。
- オプションの期間指定取得ヘルパーの挙動を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_options_225_daily`, `ClientV2.get_options_225_daily_range`
- `jquants/constants_v2.py`: `DERIVATIVES_OPTIONS_225_COLUMNS`, `DERIVATIVES_OPTIONS_225_DATE_COLUMNS`, `DERIVATIVES_OPTIONS_225_NUMERIC_COLUMNS`
- 設計Issue (参照): #25 (注: メソッド名は異なります。ドキュメントは現在の実装に従います)

## API

- V2 パス: `/v2/derivatives/bars/daily/options/225`
- メソッド: `ClientV2.get_options_225_daily(date: str)`

## DataFrame 契約 (Contract)

- ソート順: `Code` (昇順)
- 主要カラム: `Date`, `Code`, `Strike`, `PCDiv`, `O`, `H`, `L`, `C`, `OI`, `IV` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- あり: `ClientV2.get_options_225_daily_range(start_dt, end_dt=None)`
- 詳細: `docs/design/v2/core.md#range-helpers`