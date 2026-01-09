# [設計] TOPIX四本値取得APIの追加

Issue: #33

## 概要
J-Quants APIで新設されたTOPIX指数四本値取得エンドポイント (`/v2/indices/bars/daily/topix`) をサポートする。

## 背景・目的
J-Quants APIの仕様変更（TOPIX指数データの追加）に対応し、利用者がTOPIXデータを取得できるようにするため。

## インターフェース

### 入力
- `from_date`: 期間開始日 (YYYY-MM-DD, 任意)
- `to_date`: 期間終了日 (YYYY-MM-DD, 任意)

### 出力
- `pd.DataFrame`: TOPIX指数四本値データ
  - カラム: `Date`, `Code`, `Open`, `High`, `Low`, `Close` 等

### 使用例
```python
import jquantsapi
cli = jquantsapi.ClientV2()
df = cli.get_indices_topix(from_date="2024-01-01", to_date="2024-01-31")
```

## 制約・前提条件
- V2クライアント (`ClientV2`) での実装。
- 認証済みのセッションが必要。

## 方針
- `jquants/client_v2.py` に `get_indices_topix` メソッドを追加。
- `jquants/constants_v2.py` に必要なカラム定義を追加。

## 検証観点
- 指定した期間（from_date, to_date）のデータが正しく取得できること。
- 返却されるDataFrameのカラム名が期待通りであること。
- エラー時に適切な例外が発生すること。

## 参考
- [J-Quants API Reference: Indices](https://jpx.gitbook.io/j-quants-api/api-reference/indices)
