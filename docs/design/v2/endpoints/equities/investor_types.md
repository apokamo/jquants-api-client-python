# equities/investor-types (`get_equities_investor_types`)

## スコープ

投資部門別売買状況。

## 読むタイミング

- `ClientV2.get_equities_investor_types()` または `EQUITIES_INVESTOR_TYPES_COLUMNS` を変更するとき。

## 情報源 (Source of truth)

- `jquants/client_v2.py`: `ClientV2.get_equities_investor_types`
- `jquants/constants_v2.py`: `EQUITIES_INVESTOR_TYPES_COLUMNS`
- 設計Issue (参照): #51

## API

- V2 パス: `/v2/equities/investor-types`
- メソッド: `ClientV2.get_equities_investor_types(section: str = "", from_date: str = "", to_date: str = "")`

## DataFrame 契約 (Contract)

- ソート順: `PubDate`, `Section` (昇順)
- 主要カラム: `Section`, `PubDate`, `StDate`, `EnDate`, `PropSell`, `PropBuy`, ... (全リストは `constants_v2.py` を参照)

## 範囲取得ヘルパー (Range helper)

- なし。
