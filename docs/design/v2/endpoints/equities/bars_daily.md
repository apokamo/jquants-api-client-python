# equities/bars/daily (`get_prices_daily_quotes`)

## スコープ

株式の四本値（OHLCV）。

## 読むタイミング

- `ClientV2.get_prices_daily_quotes()` または `EQUITIES_BARS_DAILY_COLUMNS` を変更するとき。
- 株価の期間指定取得ヘルパーの挙動を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_prices_daily_quotes`, `ClientV2.get_price_range`
- `jquants/constants_v2.py`: `EQUITIES_BARS_DAILY_COLUMNS`
- 設計Issue (参照): #17

## API

- V2 パス: `/v2/equities/bars/daily`
- メソッド: `ClientV2.get_prices_daily_quotes(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `Code`, `Date` (昇順)
- 主要カラム: `Date`, `Code`, `O`, `H`, `L`, `C`, `Vo`, `AdjFactor` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- あり: `ClientV2.get_price_range(start_dt, end_dt=None)`
- 詳細: `docs/design/v2/core.md#range-helpers`