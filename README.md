# jquants-api-client

[J-Quants API](https://jpx-jquants.com/) V2 対応の Python クライアントライブラリ。

> **Note**: This is a fork of [J-Quants/jquants-api-client-python](https://github.com/J-Quants/jquants-api-client-python) with V2 API support and additional features.

## インストール

```bash
pip install git+https://github.com/apokamo/jquants-api-client-python.git
```

## 使用例

```python
from jquants import ClientV2

cli = ClientV2()  # 環境変数 JQUANTS_API_KEY から読み込み
```

### 銘柄マスター

```python
# 全銘柄
df = cli.get_listed_info()

# 特定銘柄
df = cli.get_listed_info(code="7203")
```

### 株価四本値

```python
# 特定日の全銘柄
df = cli.get_prices_daily_quotes(date="2024-01-15")

# 特定銘柄の期間指定
df = cli.get_prices_daily_quotes(code="7203", from_date="2024-01-01", to_date="2024-01-31")

# 期間一括取得（並列化対応）
df = cli.get_price_range(start_dt="2024-01-01", end_dt="2024-01-31")
```

### 決算情報

```python
# 決算短信サマリー
df = cli.get_fins_summary(code="7203")

# 決算発表予定
df = cli.get_fins_announcement()
```

### 指数

```python
# TOPIX
df = cli.get_indices_topix(from_date="2024-01-01", to_date="2024-01-31")

# 指数四本値
df = cli.get_indices(code="0000", from_date="2024-01-01", to_date="2024-01-31")
```

### オプション・先物

```python
# 日経225オプション
df = cli.get_options_225_daily(date="2024-01-15")

# 期間一括取得
df = cli.get_options_225_daily_range(start_dt="2024-01-01", end_dt="2024-01-31")
```

### 並列取得の設定

```python
# max_workers で並列度を指定（デフォルト: 1 = 直列）
cli = ClientV2(max_workers=3)

# rate_limit でリクエスト頻度を制御（デフォルト: 5 req/min）
cli = ClientV2(rate_limit=10)  # 10 req/min
```

## API キー設定

以下の優先順位で読み込み（後勝ち）:

1. `~/.jquants-api/jquants-api.toml`
2. `./jquants-api.toml`
3. 環境変数 `JQUANTS_API_KEY`
4. コンストラクタ引数 `ClientV2(api_key="...")`

```toml
# jquants-api.toml
[jquants-api-client]
api_key = "your_api_key"
```

## 対応メソッド

### Equities
| メソッド | 説明 | プラン |
|---------|------|--------|
| `get_listed_info` | 銘柄マスター | Free |
| `get_prices_daily_quotes` | 株価四本値 | Free |
| `get_price_range` | 株価四本値（期間一括） | Free |
| `get_fins_summary` | 決算短信サマリー | Free |
| `get_summary_range` | 決算短信サマリー（期間一括） | Free |
| `get_fins_announcement` | 決算発表予定 | Free |
| `get_equities_investor_types` | 投資部門別売買状況 | Light |

### Indices
| メソッド | 説明 | プラン |
|---------|------|--------|
| `get_indices_topix` | TOPIX指数四本値 | Light |
| `get_indices` | 指数四本値 | Standard |

### Markets
| メソッド | 説明 | プラン |
|---------|------|--------|
| `get_markets_trading_calendar` | 取引カレンダー | Free |
| `get_markets_weekly_margin_interest` | 信用取引週末残高 | Standard |
| `get_markets_short_selling` | 業種別空売り比率 | Standard |
| `get_markets_short_selling_positions` | 空売り残高報告 | Standard |
| `get_markets_daily_margin_interest` | 信用取引残高（日々） | Standard |
| `get_markets_breakdown` | 売買内訳データ | Premium |

### Derivatives
| メソッド | 説明 | プラン |
|---------|------|--------|
| `get_options_225_daily` | 日経225オプション日足 | Standard |
| `get_options_225_daily_range` | 日経225オプション（期間一括） | Standard |

## 動作環境

- Python 3.12+
- J-Quants API キー（[公式サイト](https://jpx-jquants.com/)で取得）

## ライセンス

Apache-2.0（オリジナル: [J-Quants Project Contributors](https://github.com/J-Quants/jquants-api-client-python)）
