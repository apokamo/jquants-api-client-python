# markets/margin-alert (`get_markets_daily_margin_interest`)

## スコープ

信用取引残高（日々公表信用残高）。ネストされた `PubReason` フィールドを含みます。

## 読むタイミング

- `ClientV2.get_markets_daily_margin_interest()` または `MARKETS_MARGIN_ALERT_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_markets_daily_margin_interest`
- `jquants/constants_v2.py`: `MARKETS_MARGIN_ALERT_COLUMNS`
- 設計Issue (参照): #19

## API

- V2 パス: `/v2/markets/margin-alert`
- メソッド: `ClientV2.get_markets_daily_margin_interest(code: str = "", date: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `PubDate`, `Code` (昇順)
- 主要カラム: `PubDate`, `Code`, `AppDate`, `ShrtOut`, `LongOut` (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。