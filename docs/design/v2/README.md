# ClientV2 設計 (V2)

## スコープ

`jquants.ClientV2` (V2 API クライアント) のための設計ノートです。これはライブラリのコントリビューターやエージェント向けです。

## 読むタイミング

- エンドポイントの追加・変更や、DataFrameの整形ロジックを変更する前。
- リクエスト/レスポンスのエラー処理、リトライ、ページネーション、レート制限を変更する前。

## 情報源 (Source of truth)

- **実装:** `jquants/*.py` (コードそのもの)
- **設計ドキュメント:** `docs/design/v2/**` (このディレクトリ)
- **参照用 (読み取り専用):** クローズされたIssues (歴史的経緯や根拠の確認用)
  - Core/認証/設定: Issue #9
  - インフラ/リトライ/Pacer: Issues #12, #15
  - エンドポイント設計: #17 (株価), #19 (市場), #20 (指数), #21 (財務), #25 (デリバティブ)

## 索引

### コア (Core)
- `docs/design/v2/core.md`: 認証、設定、リトライ、ページネーション、DataFrameのルール、範囲取得ヘルパー。
- `docs/design/v2/request-pipeline.md`: リクエストパイプラインのリファクタリング設計 (Issue #33)。

### 株式 (`/v2/equities/*`)
- `docs/design/v2/endpoints/equities/master.md`: 銘柄一覧 (`get_listed_info`)
- `docs/design/v2/endpoints/equities/bars_daily.md`: 株価四本値 (`get_prices_daily_quotes`)
- `docs/design/v2/endpoints/equities/earnings_calendar.md`: 決算発表予定 (`get_fins_announcement`)
- `docs/design/v2/endpoints/equities/investor_types.md`: 投資部門別売買状況 (`get_equities_investor_types`)

### 市場 (`/v2/markets/*`)
- `docs/design/v2/endpoints/markets/calendar.md`: 取引カレンダー (`get_markets_trading_calendar`)
- `docs/design/v2/endpoints/markets/margin_interest.md`: 信用取引週末残高 (`get_markets_weekly_margin_interest`)
- `docs/design/v2/endpoints/markets/short_ratio.md`: 空売り比率 (`get_markets_short_selling`)
- `docs/design/v2/endpoints/markets/breakdown.md`: 売買内訳データ (`get_markets_breakdown`)
- `docs/design/v2/endpoints/markets/short_sale_report.md`: 空売り残高 (`get_markets_short_selling_positions`)

### 指数 (`/v2/indices/*`)
- `docs/design/v2/endpoints/indices/bars_daily.md`: 指数四本値 (`get_indices`, `get_indices_topix`)
- `docs/design/v2/endpoints/indices/bars_daily_topix.md`: TOPIX四本値 (廃止パス、スキーマは同じ)

### 財務 (`/v2/fins/*`)
- `docs/design/v2/endpoints/financials/summary.md`: 財務情報 (`get_fins_summary`)

### デリバティブ (`/v2/derivatives/*`)
- `docs/design/v2/endpoints/derivatives/options_225_daily.md`: 日経225オプション (`get_options_225_daily`)

## コントリビューションチェックリスト

エンドポイントを追加または変更する場合:

1. [ ] **実装の更新:**
   - `jquants/client_v2.py` の `ClientV2` にメソッドを追加する。
   - `jquants/constants_v2.py` にカラムを追加する。
2. [ ] **エンドポイントドキュメントの作成/更新:**
   - `docs/design/v2/endpoints/<category>/<name>.md` を作成する。
   - 含める内容: スコープ、読むタイミング、APIシグネチャ、DataFrame契約 (ソートキー + 主要カラム)。
3. [ ] **索引の更新:**
   - `docs/design/v2/README.md` (このファイル) にリンクを追加する。
4. [ ] **コアの検証:**
   - `*_range()` ヘルパーを使用する場合、`docs/design/v2/core.md` のパターンに従っているか確認する。