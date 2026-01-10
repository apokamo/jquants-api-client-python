# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-10

### Added

- **ClientV2**: J-Quants API V2 対応の新クライアント
  - APIキー認証（`x-api-key` ヘッダー）
  - 環境変数 `JQUANTS_API_KEY` または `jquants-api.toml` から設定読み込み
  - V2ネイティブカラム名をそのまま使用（変換なし）

- **Standard エンドポイント（12件）**:
  - Equities: `get_listed_info()`, `get_prices_daily_quotes()`, `get_fins_announcement()`
  - Markets: `get_markets_trading_calendar()`, `get_markets_weekly_margin_interest()`, `get_markets_short_selling()`, `get_markets_short_selling_positions()`, `get_markets_daily_margin_interest()`
  - Indices: `get_indices()`, `get_indices_topix()`
  - Financials: `get_fins_summary()`
  - Derivatives: `get_options_225_daily()`

- **日付範囲取得ヘルパー**:
  - `get_price_range()`, `get_summary_range()`, `get_options_225_daily_range()`
  - 並列取得対応（`max_workers` で制御）

- **レートリミット対応**:
  - Leaky Bucket (Pacer) 方式による整流化
  - 429エラー時の自動リトライ（デフォルト5分10秒待機）
  - プラン別レート設定（`rate_limit` パラメータ）

- **カスタム例外**:
  - `JQuantsAPIError`: 一般的なAPIエラー
  - `JQuantsForbiddenError`: 認証失敗・プラン制限エラー

- **ドキュメント**:
  - V2ユーザーガイド
  - Progressive Disclosure 構成のドキュメント

### Removed

- **V1 クライアント（jquantsapi）**: 完全削除
  - `ClientV1` クラス
  - `jquantsapi` パッケージ
  - V1関連テスト

### Changed

- パッケージ名を `jquantsapi` から `jquants` に変更
- Python 3.11+ 必須

## [Unreleased]

### Planned

- Premium エンドポイント（6件）
  - `/v2/equities/bars/daily/am`
  - `/v2/equities/investor-types`
  - `/v2/fins/details`
  - `/v2/fins/dividend`
  - `/v2/derivatives/bars/daily/futures`
  - `/v2/derivatives/bars/daily/options`

[0.1.0]: https://github.com/apokamo/jquants-api-client-python/releases/tag/v0.1.0
[Unreleased]: https://github.com/apokamo/jquants-api-client-python/compare/v0.1.0...HEAD
