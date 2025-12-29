# Phase 3 詳細設計: ClientV2 エンドポイント実装

> Issue #8 Phase 3 の詳細設計書

## 概要

Phase 2で完成した認証基盤の上に、V2 APIの全18エンドポイントを実装する。
TDD（テスト駆動開発）で進め、V2ネイティブカラム名をそのまま使用する。

## 設計方針

### 1. レスポンス形式

V2 APIは全エンドポイントで統一されたレスポンス形式を使用：

```json
{
  "data": [...],
  "pagination_key": "optional_key"
}
```

V1との違い：
| V1 | V2 |
|----|-----|
| `d["info"]`, `d["daily_quotes"]`, `d["statements"]` など | 全て `d["data"]` |

### 2. V2ネイティブカラム名

V2のカラム名をそのまま使用（V1形式への変換なし）：

| V2 (採用) | V1 (参考) | 説明 |
|-----------|-----------|------|
| `O` | `Open` | 始値 |
| `H` | `High` | 高値 |
| `L` | `Low` | 安値 |
| `C` | `Close` | 終値 |
| `Vo` | `Volume` | 出来高 |
| `Va` | `TurnoverValue` | 売買代金 |
| `CoName` | `CompanyName` | 会社名 |
| `S17` | `Sector17Code` | 17業種コード |
| `S33` | `Sector33Code` | 33業種コード |

### 3. エラーハンドリング

V2 APIのエラーレスポンス形式：

```json
{
  "message": "エラー詳細"
}
```

HTTPステータスコード別の処理：

| Status | 意味 | 処理 |
|--------|------|------|
| 400 | Bad Request | `JQuantsAPIError` を raise |
| 403 | Forbidden | `JQuantsForbiddenError` を raise（※1） |
| 429 | Too Many Requests | urllib3.Retry で自動リトライ後、`JQuantsRateLimitError` を raise |
| 500 | Internal Server Error | urllib3.Retry で自動リトライ |

> **※1 403の意味（V2 API仕様）**: V2 APIは401を返さず、認証エラーも403で返す。403は以下のいずれかを意味する：
> - 無効または期限切れのAPIキー
> - プラン制限（Free/Lightプランで Premium専用エンドポイントへのアクセス）
> - 無効なリソースパス
>
> **注意**: V2 APIは401を返さないため、`JQuantsAuthError` は定義しない。

### 4. ページネーション

V1と同じ方式（whileループで `pagination_key` をチェック）：

```python
def get_xxx(self, ...) -> pd.DataFrame:
    response = self._request("GET", "/path", params=params)
    d = response.json()
    data = d["data"]
    while "pagination_key" in d:
        response = self._request("GET", "/path",
            params={**params, "pagination_key": d["pagination_key"]})
        d = response.json()
        data += d["data"]
    return pd.DataFrame(data)
```

## 実装構造

### ファイル構成

```
jquants/
├── __init__.py
├── client_v1.py          # 既存（Phase 1）
├── client_v2.py          # 認証（Phase 2） + エンドポイント（Phase 3）
├── constants_v1.py       # V1カラム定義（既存constantsから移行）
├── constants_v2.py       # V2カラム定義（新規作成）
├── enums.py
└── exceptions.py         # 新規: カスタム例外クラス

tests/
├── test_client_v1.py
└── test_client_v2.py     # Phase 2テスト + Phase 3テスト
```

### カスタム例外クラス

```python
# jquants/exceptions.py

class JQuantsAPIError(Exception):
    """J-Quants API base exception.

    All J-Quants client errors inherit from this class.
    Users can catch all client-related errors with `except JQuantsAPIError`.

    Attributes:
        status_code: HTTP status code (None for non-HTTP errors like pagination issues)
        response_body: Raw response body for debugging (truncated to 2048 chars)
    """
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class JQuantsForbiddenError(JQuantsAPIError):
    """Forbidden error (403 Forbidden).

    Raised when access is denied. Common causes:
    - Invalid or expired API key
    - Plan limitation (e.g., Free plan accessing Premium-only endpoints)
    - Invalid resource path
    """
    pass


class JQuantsRateLimitError(JQuantsAPIError):
    """Rate limit exceeded (429 Too Many Requests).

    Raised when the API rate limit is exceeded after retry attempts.
    """
    pass
```

> **注意**: V2 APIは401を返さないため、`JQuantsAuthError` は定義しない。

## エンドポイント実装一覧

### Sub-Phase 3.1: 基本インフラ

| タスク | 説明 |
|--------|------|
| `exceptions.py` 作成 | カスタム例外クラス |
| `constants_v2.py` 作成 | V2カラム定義 |
| `_request()` 拡張 | エラーハンドリング強化 |
| 共通ヘルパーメソッド | `_get_raw()`, `_paginated_get()`, `_to_dataframe()` |

### Sub-Phase 3.2: Equities エンドポイント (5件)

| V2 エンドポイント | メソッド名 | 並列取得 |
|------------------|-----------|---------|
| `/v2/equities/master` | `get_listed_info()` | - |
| `/v2/equities/bars/daily` | `get_prices_daily_quotes()` | `get_price_range()` |
| `/v2/equities/bars/daily/am` | `get_prices_prices_am()` | - |
| `/v2/equities/earnings-calendar` | `get_fins_announcement()` | - |
| `/v2/equities/investor-types` | `get_markets_trades_spec()` | - |

### Sub-Phase 3.3: Markets エンドポイント (6件)

| V2 エンドポイント | メソッド名 | 並列取得 |
|------------------|-----------|---------|
| `/v2/markets/calendar` | `get_markets_trading_calendar()` | - |
| `/v2/markets/margin-interest` | `get_markets_weekly_margin_interest()` | `get_weekly_margin_range()` |
| `/v2/markets/short-ratio` | `get_markets_short_selling()` | `get_short_selling_range()` |
| `/v2/markets/breakdown` | `get_markets_breakdown()` | `get_breakdown_range()` |
| `/v2/markets/short-sale-report` | `get_markets_short_selling_positions()` | `get_short_selling_positions_range()` |
| `/v2/markets/margin-alert` | `get_markets_daily_margin_interest()` | `get_daily_margin_interest_range()` |

### Sub-Phase 3.4: Indices エンドポイント (2件)

| V2 エンドポイント | メソッド名 | 並列取得 |
|------------------|-----------|---------|
| `/v2/indices/bars/daily` | `get_indices()` | - |
| `/v2/indices/bars/daily/topix` | `get_indices_topix()` | - |

### Sub-Phase 3.5: Financials エンドポイント (3件)

| V2 エンドポイント | メソッド名 | 並列取得 |
|------------------|-----------|---------|
| `/v2/fins/summary` | `get_fins_statements()` | `get_statements_range()` |
| `/v2/fins/details` | `get_fins_fs_details()` | `get_fs_details_range()` |
| `/v2/fins/dividend` | `get_fins_dividend()` | `get_dividend_range()` |

### Sub-Phase 3.6: Derivatives エンドポイント (3件)

| V2 エンドポイント | メソッド名 | 並列取得 |
|------------------|-----------|---------|
| `/v2/derivatives/bars/daily/options/225` | `get_option_index_option()` | `get_index_option_range()` |
| `/v2/derivatives/bars/daily/futures` | `get_derivatives_futures()` | `get_derivatives_futures_range()` |
| `/v2/derivatives/bars/daily/options` | `get_derivatives_options()` | `get_derivatives_options_range()` |

## constants_v2.py 設計

```python
# V2 カラム定義（ネイティブカラム名）

# 株価四本値 (equities/bars/daily)
PRICES_DAILY_QUOTES_COLUMNS = [
    "Date",
    "Code",
    "O",      # Open
    "H",      # High
    "L",      # Low
    "C",      # Close
    "UL",     # UpperLimit
    "LL",     # LowerLimit
    "Vo",     # Volume
    "Va",     # TurnoverValue
    "AdjFactor", # AdjustmentFactor（公式仕様準拠）
    "AdjO",   # AdjustmentOpen
    "AdjH",   # AdjustmentHigh
    "AdjL",   # AdjustmentLow
    "AdjC",   # AdjustmentClose
    "AdjVo",  # AdjustmentVolume
]

PRICES_DAILY_QUOTES_PREMIUM_COLUMNS = [
    *PRICES_DAILY_QUOTES_COLUMNS,
    # Morning session
    "MO", "MH", "ML", "MC", "MUL", "MLL", "MVo", "MVa",
    "MAdjO", "MAdjH", "MAdjL", "MAdjC", "MAdjVo",
    # Afternoon session
    "AO", "AH", "AL", "AC", "AUL", "ALL", "AVo", "AVa",
    "AAdjO", "AAdjH", "AAdjL", "AAdjC", "AAdjVo",
]

# 上場銘柄一覧 (equities/master)
LISTED_INFO_COLUMNS = [
    "Date",
    "Code",
    "CoName",    # CompanyName
    "CoNameEn",  # CompanyNameEnglish
    "S17",       # Sector17Code
    "S17Nm",     # Sector17CodeName
    "S33",       # Sector33Code
    "S33Nm",     # Sector33CodeName
    "ScaleCat",  # ScaleCategory
    "Mkt",       # MarketCode
    "MktNm",     # MarketCodeName
]

# ... 他のエンドポイントも同様
```

## テスト設計

### テストカテゴリ

1. **URL生成テスト**: 各エンドポイントのURL/パラメータ生成
2. **レスポンスパーステスト**: `d["data"]`形式のパース
3. **カラム名テスト**: V2ネイティブカラム名のDataFrame
4. **ページネーションテスト**: pagination_key処理
5. **エラーハンドリングテスト**: 各HTTPステータスコードの処理
6. **並列取得テスト**: get_*_range メソッド

### テスト例

```python
class TestClientV2Equities:
    """Equities エンドポイントのテスト"""

    def test_get_prices_daily_quotes_url(self, mock_session):
        """URL生成テスト"""
        client = ClientV2(api_key="test")
        client.get_prices_daily_quotes(code="7203", date="2024-01-01")
        mock_session.request.assert_called_with(
            "GET",
            "https://api.jquants.com/v2/equities/bars/daily",
            params={"code": "7203", "date": "2024-01-01"},
            ...
        )

    def test_get_prices_daily_quotes_response_parsing(self, mock_response):
        """レスポンスパーステスト"""
        mock_response.json.return_value = {
            "data": [
                {"Date": "2024-01-01", "Code": "7203", "O": 100, "H": 110, ...}
            ]
        }
        df = client.get_prices_daily_quotes(code="7203")
        assert "O" in df.columns  # V2ネイティブカラム名
        assert "Open" not in df.columns  # V1カラム名ではない

    def test_get_prices_daily_quotes_pagination(self, mock_response):
        """ページネーションテスト"""
        mock_response.json.side_effect = [
            {"data": [{"Code": "7203"}], "pagination_key": "key1"},
            {"data": [{"Code": "7204"}]},  # no pagination_key
        ]
        df = client.get_prices_daily_quotes()
        assert len(df) == 2

class TestClientV2ErrorHandling:
    """エラーハンドリングのテスト"""

    @pytest.mark.parametrize("status_code,exception_class", [
        (400, JQuantsAPIError),
        (403, JQuantsForbiddenError),
        (429, JQuantsRateLimitError),
    ])
    def test_http_error_handling(self, mock_response, status_code, exception_class):
        """HTTPエラーのハンドリング"""
        mock_response.status_code = status_code
        mock_response.json.return_value = {"message": "error"}
        with pytest.raises(exception_class):
            client.get_prices_daily_quotes()

    # Note: V2 APIは401を返さないため、401のテストは不要
```

## 実装順序（TDD）

各エンドポイントについて：

1. **Red**: 失敗するテストを書く
   - URL生成テスト
   - レスポンスパーステスト
   - カラム名テスト

2. **Green**: 最小限のコードでテストを通す
   - `_get_xxx_raw()` メソッド
   - `get_xxx()` メソッド

3. **Refactor**: コードを整理
   - 重複の排除
   - 型ヒントの追加

## 完了条件

- [ ] `exceptions.py` 作成完了
- [ ] `constants_v2.py` 作成完了
- [ ] 全18エンドポイント実装完了
- [ ] 全並列取得メソッド実装完了
- [ ] 全テストがパス
- [ ] `make lint` パス
- [ ] カバレッジ 95%以上

## 見積もり

| Sub-Phase | エンドポイント数 | テスト数（概算） |
|-----------|-----------------|-----------------|
| 3.1 基本インフラ | - | 10 |
| 3.2 Equities | 5 | 25 |
| 3.3 Markets | 6 | 30 |
| 3.4 Indices | 2 | 10 |
| 3.5 Financials | 3 | 15 |
| 3.6 Derivatives | 3 | 15 |
| **合計** | **18** | **~105** |

## 参考資料

- [V2 API仕様](https://jpx-jquants.com/ja/spec)
- [V1→V2 移行ガイド](https://jpx-jquants.com/ja/spec/migration-v1-v2)
- [endpoint_mapping.md](../tmp/jquants-v2-migration/endpoint_mapping.md)
- [column_mapping.py](../tmp/jquants-v2-migration/column_mapping.py)

---

*Generated with Claude Code*
