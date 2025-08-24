# About

API for self driving portal

## Architecture

### SQL

PostgreSQL

## Middleware

- FastAPI
  - Python における API 実装に利用
- pydantic
  - FastAPI で利用する schema における BaseModel で利用
- sqlmodel
  - sql 関連の DB 接続管理 / Model 管理などで利用

## Folder Structure

### cores

設定関連や SQL の Session 管理などで利用

### models

SQL からのデータ取得時に使うテーブル定義情報

### schemas

FastAPI 上で使うデータ定義情報

### SQL Schema

- vehicle
  - 車両情報テーブル
- driver
  - ドライバー情報テーブル
- measurement
  - 走行情報テーブル
  - ドライバー / 車両 / 走行日時などの情報を管理
- datastream
  - 走行情報に紐づく走行ログなどの管理テーブル
  - 1 つの measurement レコードに対して複数の datastream レコードが紐づく
  - 走行情報に紐づく各種情報について
    - 走行ログ情報
      - センサ情報は巨大なため、30 分毎に自動で分割されて管理されるため、1 レコードで各分割されたログを管理
    - 補正後データ情報
      - カメラ歪の補正や位置情報の補正をしたあとの情報
- scene
  - datastream の走行ログの中の一部を学習用に切り出した情報
- tag
  - measurement / datastream / scene に紐づくタグ
- pipeline
  - データ解析に用いるパイプラインの管理情報
- pipelinedata
  - パイプラインに適用するデータの管理情報
  - datastream / scene の情報が紐づく
- pipelinestate
  - pipeline と pipelinedata を紐づけてパイプラインの実行を行った際の管理テーブル
  - パイプラインの実行結果や状態を管理
