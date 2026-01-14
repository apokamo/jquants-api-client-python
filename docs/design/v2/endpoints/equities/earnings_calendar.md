# equities/earnings-calendar (`get_fins_announcement`)

## スコープ

決算発表カレンダー。

## 読むタイミング

- `ClientV2.get_fins_announcement()` または `EQUITIES_EARNINGS_CALENDAR_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_fins_announcement`
- `jquants/constants_v2.py`: `EQUITIES_EARNINGS_CALENDAR_COLUMNS`
- 設計Issue (参照): #17

## API

- V2 パス: `/v2/equities/earnings-calendar`
- メソッド: `ClientV2.get_fins_announcement()`

## DataFrame 契約 (Contract)

- ソート順: `Date`, `Code` (昇順)
- 主要カラム: `Date`, `Code`, `CoName`, `FY`, `FQ` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。