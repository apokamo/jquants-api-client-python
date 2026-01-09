# リクエスト・パイプライン

## 概要

HTTPリクエスト処理のパイプライン（構築→送信→例外処理→レスポンス整形）を共通化し、`ClientV2` の各メソッドがビジネスロジック（パラメータ構築）のみに集中できる構造。

### 設計意図

- リクエストフローを単一のパイプラインに集約し、保守性を向上
- 将来的な仕様変更（Premium機能追加等）に備えた基盤

## アーキテクチャ

### メソッド階層

```
[エンドポイントメソッド]
    │
    ├─ _paginated_get()
    │       └─ _execute_json_request() + pagination + 形式検証
    │
    └─ _get_raw()
            └─ _request() + UTF-8 decode
```

### 責務の配置

| メソッド | 責務 |
|----------|------|
| `_request()` | HTTP送信 + Pacer + 429リトライ + エラーハンドリング |
| `_execute_json_request()` | `_request()` + JSON パース |
| `_get_raw()` | `_request()` + UTF-8 decode |
| `_paginated_get()` | `_execute_json_request()` + pagination + 形式検証 |

## `_execute_json_request()` 仕様

### Input

- `method` (str): HTTP メソッド ("GET" or "POST")
- `path` (str): API パス (例: "/equities/master")
- `params` (dict | None): クエリパラメータ
- `json_data` (dict | None): POST ボディ

### Output

- `dict`: パース済み JSON レスポンス

### Raises

- `JQuantsForbiddenError`: 403
- `JQuantsRateLimitError`: 429 (リトライ後)
- `JQuantsAPIError`: その他エラー / JSON パースエラー

### JSONパースエラー時の挙動

JSONパースエラー時は `JQuantsAPIError` (status_code=None) を送出。
デバッグを容易にするため、元のレスポンス本文の先頭部分（最大200文字）をエラーメッセージに含める。

```python
try:
    return response.json()
except (ValueError, TypeError) as e:
    body_preview = response.text[:200] if response.text else "(empty)"
    raise JQuantsAPIError(
        f"Failed to parse JSON response: {e}. Response preview: {body_preview}"
    )
```

## 制約事項

1. **後方互換性**: パブリック API は変更しない
2. **例外体系**: 既存の例外クラス体系を維持
3. **パフォーマンス**: オーバーヘッドを最小限に

## 参考

- 公式仕様: https://jpx-jquants.com/ja/spec/
- 関連設計: `docs/design/v2/core.md` (Request Pipeline セクション)
- 関連Issue: #33
