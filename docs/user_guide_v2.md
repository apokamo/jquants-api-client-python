# J-Quants API V2 Client User Guide

このガイドでは、`jquants-api-client-python` の V2 クライアント（`ClientV2`）の使用方法について解説します。

## 目次

1. [インストール](#インストール)
2. [認証と設定](#認証と設定)
3. [基本的な使い方](#基本的な使い方)
4. [日付範囲取得と並列化](#日付範囲取得と並列化)
5. [レート制限とリトライ](#レート制限とリトライ)
6. [エラーハンドリング](#エラーハンドリング)
7. [データ形式 (DataFrame)](#データ形式-dataframe)

---

## インストール

```bash
pip install jquants-api-client
```

## 認証と設定

V2 API は **API Key**（`x-api-key`）方式を使用します。IDトークン更新（V1方式）は不要です。

APIキーは [J-Quants API サイト](https://jpx-jquants.com/) から取得してください。

### 設定方法（優先度順）

以下の順序でAPIキーを解決します。セキュリティのため、コードへのハードコードは避けてください。

1. **コンストラクタ引数**
   ```python
   client = ClientV2(api_key="YOUR_API_KEY")
   ```

2. **環境変数**
   ```bash
   export JQUANTS_API_KEY="YOUR_API_KEY"
   ```
   ```python
   client = ClientV2()  # 環境変数を自動読込
   ```

3. **設定ファイル (TOML)**
   以下のパスにある `jquants-api.toml` を自動的に探します。
   - カレントディレクトリ (`./jquants-api.toml`)
   - ユーザーホーム (`~/.jquants-api/jquants-api.toml`)

   **jquants-api.toml の形式:**
   ```toml
   [jquants-api-client]
   api_key = "YOUR_API_KEY"
   ```

---

## 基本的な使い方

エンドポイントに対応するメソッドを呼び出すと、整理された `pandas.DataFrame` が返されます。

```python
from jquants import ClientV2

# クライアントの初期化（環境変数からAPIキーを読み込む場合）
client = ClientV2()

# 1. 銘柄一覧を取得（全銘柄）
df_master = client.get_listed_info()
print(df_master.head())

# 2. 株価四本値を取得（特定の日付）
df_daily = client.get_prices_daily_quotes(date="2024-01-04")
print(df_daily.head())

# 3. 決算発表予定を取得
df_cal = client.get_fins_announcement()
```

---

## 日付範囲取得と並列化

多くのデータ取得メソッドには、期間を指定して一括取得するための `*_range()` メソッドが用意されています。

### 期間指定での取得

```python
# 2024年1月の株価データを取得
df_range = client.get_price_range(
    start_dt="2024-01-01",
    end_dt="2024-01-31"
)
```

### 並列ダウンロード (max_workers)

期間指定取得はデフォルトでは直列（1日ずつ）で行われますが、`max_workers` を指定することで並列化し、取得を高速化できます。
ただし、レート制限（後述）の範囲内で制御されます。

```python
# 並列度=5 でクライアントを初期化
client = ClientV2(max_workers=5)

# 内部で5並列でダウンロード実行
df_range = client.get_price_range(start_dt="2023-01-01", end_dt="2023-12-31")
```

---

## レート制限と並列化の設定

`ClientV2` インスタンスを作成する際に、ご自身の契約プランや利用シーンに合わせて設定を行います。これらは現在、設定ファイル（TOML）や環境変数からは読み込まれないため、必ずコード上で指定してください。

### 設定方法

```python
from jquants import ClientV2

client = ClientV2(
    rate_limit=120,    # 1分あたりの最大リクエスト数 (req/min)
    max_workers=5,     # 同時に実行するスレッド数
)
```

### プラン別推奨設定

J-Quants API はプランごとにリクエスト上限が定められています。上限を超えると 429 エラーが発生するため、以下の推奨値を参考に設定してください。

| プラン | 推奨 `rate_limit` | 推奨 `max_workers` | 備考 |
| :--- | :--- | :--- | :--- |
| **Free** | 5 (デフォルト) | 1 | 並列化のメリットはほぼありません。 |
| **Light / Standard** | 100 〜 120 | 2 〜 4 | 複数日のデータ取得がスムーズになります。 |
| **Premium** | 400 〜 600 | 5 〜 10 | 大量のデータを高速に一括取得可能です。 |

※最新の正確な制限値は、公式の[プラン別データ仕様](https://jpx-jquants.com/ja/spec/data-spec)をご確認ください。

### 設定の仕組み (Pacer)

- **自動調整**: `rate_limit` を指定すると、ライブラリ内部の Pacer がリクエスト間隔を自動調整（ペーシング）します。
- **並列数との関係**: `max_workers` を増やしても、全体の取得速度は `rate_limit` によって制限されます。`max_workers` は「通信の待ち時間（レイテンシ）」を埋めるために使用し、`rate_limit` は「APIサーバーへの負荷」を制御するために使用します。

### 429 (Too Many Requests) リトライ

万が一レート制限を超えた場合（HTTP 429エラー）、クライアントは自動的に待機してリトライします。

- **デフォルト動作:** 310秒待機してリトライ（最大3回）
- **設定変更:**
  ```python
  client = ClientV2(
      retry_wait_seconds=60,  # 待機時間を60秒に変更
      retry_max_attempts=5    # 最大5回リトライ
  )
  ```

---

## エラーハンドリング

例外はすべて `jquants.exceptions` モジュールで定義されています。

```python
from jquants import ClientV2
from jquants.exceptions import JQuantsForbiddenError, JQuantsRateLimitError, JQuantsAPIError

try:
    client = ClientV2()
    df = client.get_prices_daily_quotes(date="2024-01-04")

except JQuantsForbiddenError as e:
    # 403: APIキー間違い、またはプラン未契約のエンドポイント
    print(f"権限エラー: {e}")

except JQuantsRateLimitError as e:
    # 429: リトライ上限を超えてレート制限にかかった
    print(f"レート制限超過: {e}")

except JQuantsAPIError as e:
    # その他のAPIエラー (5xxなど)
    print(f"APIエラー: {e}")

except Exception as e:
    # ネットワークエラーなど (requests.Timeout 等)
    print(f"予期せぬエラー: {e}")
```

---

## データ形式 (DataFrame)

取得される `pandas.DataFrame` は以下のように整形されています。

- **カラム名:** API仕様に準拠（CamelCase）。
- **日付型:** `Date` などのカラムは `datetime64[ns]` 型に変換済み。
- **数値型:** 数値カラムは数値型に変換済み。
- **ソート:** 各エンドポイントに適した順序（例: 日付昇順、コード昇順）でソート済み。

具体的なカラム定義は `jquants/constants_v2.py` または各ドキュメントを参照してください。
