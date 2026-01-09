# [設計] リクエスト・パイプラインの共通化

Issue: #33

## 概要

### 何を作るのか
HTTPリクエスト処理のパイプライン（構築→送信→例外処理→レスポンス整形）を共通化し、`ClientV2` の各メソッドがビジネスロジック（パラメータ構築）のみに集中できる状態を実現する。

### なぜ作るのか
- 現在の `_request()` の責務が大きくなっている
- 将来的な仕様変更（Premium機能追加等）に備え、リクエストフローを単一のパイプラインに集約したい
- コードの保守性向上

## 現状分析

### 現在のメソッド構造

```
[エンドポイントメソッド]
    │
    ├─ _get_raw()      → _request() → response.content.decode()
    │
    └─ _paginated_get() → _request() → response.json() + pagination
                              │
                              ├─ Pacer制御
                              ├─ 429リトライ
                              └─ エラーハンドリング
```

### 現状の課題

1. **レスポンス処理の分散**: `_get_raw()` と `_paginated_get()` で個別にレスポンス処理
2. **JSON パース責務**: `_paginated_get()` が pagination と JSON パースの両方を担当
3. **拡張性**: 新しいレスポンス形式（例: ストリーミング）への対応が難しい

## インターフェース (Usage)

リファクタリング後もパブリック API は変更なし。内部構造のみ変更。

```python
# ユーザーコード（変更なし）
client = ClientV2(api_key="...")
df = client.get_listed_info(code="7203")
df = client.get_prices_daily_quotes(code="7203", date="2024-01-15")
```

## 入出力定義 (Input/Output)

### `_execute_json_request()` (新設)

**Input:**
- `method` (str): HTTP メソッド ("GET" or "POST")
- `path` (str): API パス (例: "/equities/master")
- `params` (dict | None): クエリパラメータ
- `json_data` (dict | None): POST ボディ

**Output:**
- `dict`: パース済み JSON レスポンス

**Raises:**
- `JQuantsForbiddenError`: 403
- `JQuantsRateLimitError`: 429 (リトライ後)
- `JQuantsAPIError`: その他エラー / JSON パースエラー

### 責務の再配置

| メソッド | 変更前責務 | 変更後責務 |
|----------|------------|------------|
| `_request()` | HTTP送信 + Pacer + 429リトライ + エラーハンドリング | **変更なし**（低レベル HTTP） |
| `_execute_json_request()` | (新設) | `_request()` + JSON パース + 形式検証 |
| `_get_raw()` | `_request()` + decode | `_request()` + decode（**変更なし**） |
| `_paginated_get()` | `_request()` + JSON + pagination | `_execute_json_request()` + pagination |

## 制約事項 (Constraints)

1. **後方互換性**: パブリック API は変更しない
2. **既存テスト**: 全ての結合テストがパスすること
3. **例外体系**: 既存の例外クラス体系を維持
4. **パフォーマンス**: オーバーヘッドを最小限に

## 処理方針 (Policy)

### 新メソッド `_execute_json_request()`

```
_execute_json_request(method, path, params, json_data)
    │
    ├─ _request(method, path, params, json_data)  # 既存
    │       └─ Pacer, 429リトライ, エラーハンドリング
    │
    ├─ response.json()
    │       └─ JSON パースエラー → JQuantsAPIError (status_code=None)
    │           └─ エラーメッセージにレスポンス本文の先頭部分を含める（デバッグ用）
    │
    └─ return dict
```

#### JSONパースエラー時のエラーメッセージ

デバッグを容易にするため、JSONパースエラー時は元のレスポンス本文の先頭部分（最大200文字程度）をエラーメッセージに含める。

```python
# 実装イメージ
try:
    return response.json()
except (ValueError, TypeError) as e:
    body_preview = response.text[:200] if response.text else "(empty)"
    raise JQuantsAPIError(
        f"Failed to parse JSON response: {e}. Response preview: {body_preview}"
    )
```

### `_paginated_get()` の簡素化

```python
# Before
response = self._request("GET", path, params=current_params)
try:
    result = response.json()
except (ValueError, TypeError) as e:
    raise JQuantsAPIError(...)

# After
result = self._execute_json_request("GET", path, params=current_params)
# JSON パースエラーは _execute_json_request 内で処理済み
```

### 段階的リファクタリング

1. **Phase 1**: `_execute_json_request()` 新設
2. **Phase 2**: `_paginated_get()` を書き換え
3. **Phase 3**: 結合テストで回帰確認

## 検証観点 (Test Strategy)

### 正常系
- [ ] 全エンドポイントが正常に動作すること（既存結合テストでカバー）
- [ ] pagination が正常に動作すること
- [ ] `_get_raw()` が従来通り動作すること

### 異常系
- [ ] JSON パースエラー時に `JQuantsAPIError` が発生すること
- [ ] 不正なレスポンス形式（dict 以外）で `JQuantsAPIError` が発生すること
- [ ] 403/429/5xx エラーハンドリングが従来通り動作すること

### 境界値
- [ ] 空レスポンス `{}` の処理
- [ ] `"data": []` の処理
- [ ] 大量ページネーション（max_pages 境界）

## タスクリスト

- [ ] `_execute_json_request()` メソッドの実装
- [ ] `_paginated_get()` のリファクタリング
- [ ] 結合テストによる回帰確認
- [ ] `docs/design/v2/core.md` のドキュメント更新

## 参考

- 公式仕様: https://jpx-jquants.com/ja/spec/
- 既存設計: `docs/design/v2/core.md`
