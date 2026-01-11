# ClientV2 コア設計

## スコープ

エンドポイント間で共有される振る舞い:
設定解決、リクエスト/リトライ、ページネーション、DataFrame整形、レート制限、および範囲取得ヘルパー。

## 情報源 (Source of truth)

- 実装: `jquants/client_v2.py`, `jquants/exceptions.py`, `jquants/pacer.py`
- 設計根拠 (参照): Issues #9, #12, #15

## APIキーと設定の解決

以下の優先順位で解決されます（後勝ち）:

1. Colab 設定 (暗黙的)
2. ユーザーデフォルト設定 (暗黙的): `${HOME}/.jquants-api/jquants-api.toml`
3. CWD 設定 (暗黙的): `jquants-api.toml`
4. 明示的な設定ファイル (fail-fast): `JQUANTS_API_CLIENT_CONFIG_FILE`
5. 環境変数 (空でも上書き): `JQUANTS_API_KEY`
6. コンストラクタ引数 (最高優先度): `ClientV2(api_key=...)`

TOML スキーマ:

```toml
[jquants-api-client]
api_key = "your_api_key"
```

## レート制限 (Pacer)

- `ClientV2(rate_limit=..., max_workers=...)` は、ペーシングと並列取得の挙動を制御します。
- **Pacer の振る舞い:** `rate_limit` (1分あたりのリクエスト数) に基づいて、リクエスト間の最小間隔を強制します。
  - 計算式: `interval = 60.0 / rate_limit`
  - デフォルト: `rate_limit=5` (Freeプラン), `max_workers=1` (順次処理)。
- ペーシングは、429リトライを含むすべてのリクエストの前に `Pacer.wait()` を介して強制されます。

## リクエスト / リトライ / エラー

### リクエストパイプライン

低レベルのHTTPリクエストフローは、階層構造にカプセル化されています。

| メソッド | 責務 |
| :--- | :--- |
| `_request()` | HTTP送信 + Pacer + 429リトライ + エラーハンドリング (例外送出) |
| `_execute_json_request()` | `_request()` + JSON パース (パース失敗時は `JQuantsAPIError` を送出) |
| `_get_raw()` | `_request()` + UTF-8 decode (生のJSON文字列アクセス用) |
| `_paginated_get()` | `_execute_json_request()` + ページネーション処理 + レスポンス形式検証 |

エンドポイントは標準的なV2 API呼び出しに `_paginated_get()` を使用し、エンドポイントメソッドはパラメータ構築とDataFrame整形に集中させます。

### 一時的なエラー (5xx)
- `requests.Session` + `urllib3.Retry` を使用します。
- **戦略:** ステータスコード `[500, 502, 503, 504]` に対して3回リトライ。
- **バックオフ:** `backoff_factor=0.5`。
- **許可されるメソッド:** `["HEAD", "GET", "OPTIONS"]` (副作用を防ぐためPOSTは除外)。

### レート制限エラー (429)
- ヘルパーメソッドを使用して `ClientV2._request()` 内のカスタムロジックで処理されます:
  - `_parse_retry_after()`: `Retry-After` ヘッダをパースします (RFC 7231 準拠)。
  - `_calculate_retry_wait()`: 待機時間またはリトライ中止を決定する純粋関数。
- **パラメータ:**
  - `retry_on_429`: bool (デフォルト: `True`)
  - `retry_wait_seconds`: int (デフォルト: `310`) — `Retry-After` ヘッダがない/無効な場合のフォールバック。
  - `retry_max_attempts`: int (デフォルト: `3`)
- **待機ポリシー:**
  - `Retry-After` ヘッダが存在し有効な場合、その値を尊重します (`Retry-After: 0` での即時リトライを含む)。
  - ヘッダがないか無効な場合、`retry_wait_seconds` にフォールバックします。

### 例外
すべてのカスタム例外は `jquants.exceptions.JQuantsAPIError` を継承します。

| 例外 | HTTP ステータス | 説明 |
| :--- | :--- | :--- |
| `JQuantsForbiddenError` | 403 | 無効なAPIキー、プラン制限、または無効なパス。 |
| `JQuantsRateLimitError` | 429 | リトライ上限を超えてレート制限にかかった場合。 |
| `JQuantsAPIError` | その他/なし | その他のAPIエラーまたはクライアント側の契約違反 (例: ページネーションループ)。 |

**注:** ネットワーク層の例外 (`requests.Timeout`, `requests.ConnectionError`) はラップされません。

## DataFrame 契約 (Contract)

エンドポイントは一般的にこのパターンに従います:

- `*_raw()` (または同等の内部呼び出し): JSONを取得し、ページネーションを処理します。
- 公開 `get_*()`: 型付き/順序付きで、一貫してソートされた DataFrame を返します。
- `*_range()`: 日付範囲ヘルパー。オプションで並列化が可能 (`max_workers` で制御)。

`constants_v2.py` のカラムリストは推奨される順序として扱われます。レスポンスにカラムが欠けていても許容されます。

## 範囲取得ヘルパー (Range helpers)

一部のエンドポイントには、日ごとのデータを取得して結合する `*_range()` ヘルパーが付属しています。

このコードベースでの例:

- `ClientV2.get_price_range()` (株式四本値)
- `ClientV2.get_summary_range()` (財務情報)
- `ClientV2.get_options_225_daily_range()` (日経225オプション)

共通の契約:

- 入力は `YYYY-MM-DD` 文字列、`date`、または `datetime` を受け入れ、`_normalize_date()` で正規化されます。
- 日付文字列は `YYYY-MM-DD` として扱われます (`YYYYMMDD` ではなく)。無効な形式は日付範囲生成中に `ValueError` を発生させます。
- 日付範囲は包括的であり、検証されます (`start_dt` が `end_dt` より後であってはなりません)。
- 取得戦略は `ClientV2.max_workers` に依存します:
  - `max_workers == 1`: 順次処理 (デフォルト、最も安全)
  - `max_workers > 1`: Pacer制御下での `ThreadPoolExecutor` による並列処理
- 結果は結合され、エンドポイントの自然なソートキーを使用して再ソートされます。
- 要求された期間にデータがない場合、期待されるカラムセットを持つ空の `DataFrame` を返します。

### 内部: `_fetch_date_range`

`*_range()` ヘルパーの共通実装。Issue #40 (Phase 3.7) で抽出されました。

パラメータ:
- `start_dt`, `end_dt`: 日付範囲 (`_normalize_date()` で正規化済み)
- `fetch_func`: 単一日取得関数 (例: `get_prices_daily_quotes`)
- `sort_columns`: 最終的な DataFrame のソートキー
- `empty_columns`: 空の結果用カラムリスト
- `date_columns`: `datetime64[ns]` に変換するカラム (空の結果でも型安全性を確保)
- `ensure_all_columns`: Trueの場合、すべてのカラムが存在し正しい順序であることを保証するためにreindexする

振る舞い:
- 日付文字列を正規化します ("2024-1-5" → "2024-01-05" のようにゼロ埋めなしも対応)
- `start_dt <= end_dt` を検証します (正規化後、安全な文字列比較)
- 非YYYY-MM-DD形式を拒否し、ユーザーフレンドリーなエラーメッセージを表示します
- `max_workers` に基づいて順次または並列実行にディスパッチします
- `pd.concat` の前に空の DataFrame をフィルタリングします (FutureWarning 回避)
- 空の結果でも日付カラムの型を保証します
- 結果を `sort_columns` でソートします