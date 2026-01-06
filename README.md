# jquants-api-client

[![PyPI version](https://badge.fury.io/py/jquants-api-client.svg)](https://badge.fury.io/py/jquants-api-client)

個人投資家向けデータ API 配信サービス「 [J-Quants API](https://jpx-jquants.com/#jquants-api) 」の Python クライアントライブラリです。
J-Quants や API 仕様についての詳細を知りたい方は [公式ウェブサイト](https://jpx-jquants.com/) をご参照ください。
現在、J-Quants API は有償版サービスとして提供されています。

## 使用方法

pip 経由でインストールします。

```shell
pip install jquants-api-client
```

### J-Quants API の利用

To use J-Quants API, you need to "Applications for J-Quants API" from [J-Quants API Web site](https://jpx-jquants.com/?lang=en) and to select a plan.

J-Quants API を利用するためには[J-Quants API の Web サイト](https://jpx-jquants.com/) から「J-Quants API 申し込み」及び利用プランの選択が必要になります。

jquants-api-client-python を使用するためには「J-Quants API メニューページから取得した API キー」が必要になります。必要に応じて下記の Web サイトより取得してください。

[J-Quants API メニューページ](https://jpx-jquants.com/)

### サンプルコード

```python
from jquants import ClientV2

api_key = "*****"
cli = ClientV2(api_key=api_key)
df = cli.get_prices_daily_quotes(date="2022-07-25")
print(df)
```

API レスポンスが Dataframe の形式で取得できます。

## 対応 API

V2 API の各エンドポイントに対応したメソッドを提供しています。

### 基本エンドポイント

ご契約のプランに応じて、以下のメソッドが利用可能です。

#### Free プラン以上
- `get_listed_info`: 銘柄マスター
- `get_prices_daily_quotes`: 株価四本値
- `get_fins_summary`: 決算短信サマリー（一括取得）
- `get_fins_announcement`: 決算発表予定

#### Light プラン以上
- `get_indices_topix`: TOPIX指数四本値

#### Standard プラン以上
- `get_options_225_daily`: 日経225オプション日足
- `get_markets_weekly_margin_interest`: 信用取引週末残高
- `get_markets_short_selling`: 業種別空売り比率
- `get_indices`: 指数四本値
- `get_markets_short_selling_positions`: 空売り残高報告
- `get_markets_daily_margin_interest`: 信用取引残高（日々公表分）

#### Premium プラン以上
- `get_markets_breakdown`: 売買内訳データ

### 期間指定・一括取得ユーティリティ (`*_range`)

日付範囲を指定してデータを一括取得し、結合した DataFrame を返す便利なメソッドです。内部で `max_workers` による並列取得が可能です。

- `get_price_range`: 株価四本値
- `get_summary_range`: 決算短信サマリー
- `get_options_225_daily_range`: 日経225オプション日足

## 設定

認証用の API キーは設定ファイルおよび環境変数を使用して指定することも可能です。
設定は下記の順に読み込まれ、設定項目が重複している場合は後に読み込まれた値で上書きされます。

1. `/content/drive/MyDrive/drive_ws/secret/jquants-api.toml` (Google Colab のみ)
2. `${HOME}/.jquants-api/jquants-api.toml`
3. `jquants-api.toml`
4. `os.environ["JQUANTS_API_CLIENT_CONFIG_FILE"]`
5. `${JQUANTS_API_KEY}`

### 設定ファイル例

`jquants-api.toml` は下記のように設定します。

```toml
[jquants-api-client]
api_key = "*****"
```

## 動作確認

Google Colab および Python 3.11 で動作確認を行っています。
J-Quants API は有償版で継続開発されているため、本ライブラリも今後仕様が変更となる可能性があります。
Python の EOL を迎えたバージョンはサポート対象外となります。
Please note we only support Python supported versions. Unsupported versions (after EOL) are not supported.
ref. https://devguide.python.org/versions/#supported-versions

## 開発

J-Quants API Client の開発に是非ご協力ください。
Github 上で Issue や Pull Request をお待ちしております。
