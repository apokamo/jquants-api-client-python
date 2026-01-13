# [設計] get_equities_investor_types メソッド追加

Issue: #51

## 概要

投資部門別売買状況 (`/equities/investor-types`) を取得するメソッドを ClientV2 に追加する。

## 背景・目的

- Sub-Phase 3.2 で計画されていたが実装漏れ
- スタンダードプラン対象エンドポイントで唯一の未実装
- カラム定義 (`EQUITIES_INVESTOR_TYPES_COLUMNS`) は既に存在

## インターフェース

### 入力

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| section | str | No | 市場区分 (例: "TSEPrime", "TSEStandard", "TSEGrowth") |
| from_date | str | No | 開始日 YYYY-MM-DD |
| to_date | str | No | 終了日 YYYY-MM-DD |

**制約**:
- パラメータはすべて省略可能（全件取得）
- `from_date`/`to_date` は単独または組み合わせで使用可
- 日付形式は YYYY-MM-DD のみ（YYYYMMDD は ValueError）

### 出力

| 項目 | 型 | 説明 |
|------|-----|------|
| 戻り値 | pd.DataFrame | 投資部門別売買状況 |
| カラム | EQUITIES_INVESTOR_TYPES_COLUMNS | 68カラム |
| ソート | PubDate, Section 昇順 | |
| 日付型変換 | PubDate, StDate, EnDate | pd.Timestamp |

### 使用例

```python
from jquants import ClientV2

client = ClientV2(api_key="...")

# 全件取得
df = client.get_equities_investor_types()

# 市場区分指定
df = client.get_equities_investor_types(section="TSEPrime")

# 期間指定
df = client.get_equities_investor_types(
    from_date="2024-01-01",
    to_date="2024-12-31"
)

# 組み合わせ
df = client.get_equities_investor_types(
    section="TSEPrime",
    from_date="2024-01-01",
    to_date="2024-12-31"
)
```

## 制約・前提条件

- Light プラン以上が必要
- 単位は千円（JPX公式統計と同一）
- ページネーション対応（`_paginated_get` 使用）
- 2022年4月の市場区分見直し対応済み

## 方針

既存メソッド (`get_markets_short_selling` 等) と同様のパターンで実装:

```python
def get_equities_investor_types(
    self,
    section: str = "",
    from_date: str = "",
    to_date: str = "",
) -> pd.DataFrame:
    # 1. 日付バリデーション（from/to組み合わせ）
    # 2. パラメータ構築
    # 3. _paginated_get でデータ取得
    # 4. _to_dataframe で DataFrame 変換
    #    - date_columns: ["PubDate", "StDate", "EnDate"]
    #    - sort_columns: ["PubDate", "Section"]
```

## 検証観点

### 正常系
- パラメータなしで全件取得できること
- section 指定で該当市場のみ取得できること
- from_date/to_date で期間絞り込みできること
- 組み合わせ指定が正しく動作すること
- カラム順序が `EQUITIES_INVESTOR_TYPES_COLUMNS` と一致すること
- 日付カラムが pd.Timestamp 型に変換されること
- PubDate, Section でソートされていること

### 異常系
- 不正な日付形式で ValueError が発生すること
- 存在しない section でも空 DataFrame が返ること（APIエラーにならない）

### 境界値
- 空レスポンス時に空 DataFrame（カラム定義維持）が返ること
- ページネーションが正しく処理されること（大量データ）

## 参考

- V2 API仕様: https://jpx-jquants.com/ja/spec/eq-investor-types
- 既存カラム定義: `jquants/constants_v2.py` L101-171
