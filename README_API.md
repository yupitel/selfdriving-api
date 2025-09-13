# Measurement API

自動運転車両の走行データ収集用API

## 概要

このAPIは自動運転車両の測定データ（measurement）を管理するためのRESTful APIです。

## 技術スタック

- **FastAPI**: 高速な非同期Webフレームワーク
- **SQLModel**: SQLAlchemyとPydanticを統合したORM
- **PostgreSQL**: データベース
- **Docker**: コンテナ化

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

必要に応じて`.env`ファイルを編集してください。

### 2. 環境別起動方法

#### 開発環境（Development）
自動的にスキーマとテーブルを作成します。

```bash
# 開発環境用スクリプトを使用
./scripts/start-dev.sh

# または手動で起動
docker-compose up -d
```

#### テスト環境（Test）
毎回テーブルを再作成して、クリーンな状態でテストを行います。

```bash
# テスト環境用スクリプトを使用（APIテストも実行）
./scripts/start-test.sh

# または手動で起動
docker-compose -f docker-compose.test.yml up -d
```

#### 本番環境（Production）
既存のデータベースを使用し、スキーマ・テーブルの存在をチェックのみ行います。

```bash
# 環境変数を設定
export DATABASE_URL="postgresql://user:password@host:5432/database"
export DB_MODE="production"

# 本番環境で起動
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 環境変数による動作モード

| 環境変数 | 値 | 動作 |
|---------|-----|------|
| `DB_MODE=development` | デフォルト | スキーマ・テーブルを必要に応じて作成 |
| `DB_MODE=test` | テスト用 | 毎回テーブルを再作成 |
| `DB_MODE=production` | 本番用 | 既存DB構造の検証のみ |

### 4. ローカル開発環境での起動

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# PostgreSQLの起動（Dockerを使用）
docker-compose up -d postgres

# 環境変数設定
export DB_MODE=development

# APIサーバーの起動
uvicorn app.main:app --reload
```

## API エンドポイント

### ヘルスチェック

- `GET /api/v1/health` - APIヘルスチェック
- `GET /api/v1/health/db` - データベース接続チェック

### Measurement API

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| POST | `/api/v1/measurements/` | 測定データの作成（バルク、1件以上） |
| GET | `/api/v1/measurements/` | 測定データ一覧の取得（limit/offset） |
| GET | `/api/v1/measurements/count` | 測定データ件数の取得（フィルタ適用） |
| GET | `/api/v1/measurements/{id}` | 特定の測定データの取得 |
| PUT | `/api/v1/measurements/{id}` | 測定データの更新 |
| DELETE | `/api/v1/measurements/{id}` | 測定データの削除 |
|  |  |  |

### ルール: Create はバルク（1..N）

このリポジトリでは、作成系のエンドポイントはすべて「バルク at ルート」です。単一作成も含め、以下のように配列ラッパーでPOSTします。

- Vehicles: `POST /api/v1/vehicles` ボディ `{ "vehicles": [ { ... } ] }` 返却は `VehicleBulkResponse`
- Pipelines: `POST /api/v1/pipelines` ボディ `{ "pipelines": [ { ... } ] }` 返却は `PipelineBulkResponse`
- Measurements: `POST /api/v1/measurements` ボディ `{ "measurements": [ { ... } ] }` 返却は `BaseResponse<MeasurementResponse[]>`
- Datastreams: `POST /api/v1/datastreams` ボディ `{ "datastreams": [ { ... } ] }` 返却は `DataStreamBulkResponse`
- Drivers: `POST /api/v1/drivers` ボディ `{ "drivers": [ { ... } ] }` 返却は `DriverBulkResponse`
- PipelineData: `POST /api/v1/pipelinedata` ボディ `{ "pipeline_data": [ { ... } ] }` 返却は `BaseResponse<PipelineDataResponse[]>`
- PipelineStates: `POST /api/v1/pipelinestates` ボディ `{ "pipeline_states": [ { ... } ] }` 返却は `BaseResponse<PipelineStateResponse[]>`
- PipelineDependencies: `POST /api/v1/pipelinedependencies` ボディ `{ "pipeline_dependencies": [ { ... } ] }` 返却は `BaseResponse<PipelineDependencyResponse[]>`

注: 旧 `/bulk` エンドポイントは削除済みです。

### Pipeline API

ベースURL: `http://localhost:8000/api/v1`

パスの命名規則は複数形に統一しました（legacyの単数形は当面互換のため維持）。

| リソース | メソッド | エンドポイント | 説明 |
|---------|---------|--------------|------|
| pipelinedata | GET | `/pipelinedata` | パイプラインデータ一覧の取得 |
| pipelinedata | POST | `/pipelinedata` | パイプラインデータの作成（バルク、1件以上） |
| pipelinedata | GET | `/pipelinedata/{id}` | パイプラインデータの取得 |
| pipelinedata | PUT | `/pipelinedata/{id}` | パイプラインデータの更新 |
| pipelinedata | DELETE | `/pipelinedata/{id}` | パイプラインデータの削除 |
|  |  |  |
| pipelinestates | GET | `/pipelinestates` | パイプライン状態一覧の取得 |
| pipelinestates | POST | `/pipelinestates` | パイプライン状態の作成（バルク、1件以上） |
| pipelinestates | GET | `/pipelinestates/{id}` | パイプライン状態の取得 |
| pipelinestates | PUT | `/pipelinestates/{id}` | パイプライン状態の更新 |
| pipelinestates | DELETE | `/pipelinestates/{id}` | パイプライン状態の削除 |
|  |  |  |
| pipelinestates | GET | `/pipelinestates/jobs/by-pipeline-data/{pipeline_data_id}` | 指定データのジョブ一覧 |
| pipelinedependencies | GET | `/pipelinedependencies` | 依存関係一覧の取得 |
| pipelinedependencies | POST | `/pipelinedependencies` | 依存関係の作成（バルク、1件以上） |
| pipelinedependencies | GET | `/pipelinedependencies/{id}` | 依存関係の取得 |
| pipelinedependencies | PUT | `/pipelinedependencies/{id}` | 依存関係の更新 |
| pipelinedependencies | DELETE | `/pipelinedependencies/{id}` | 依存関係の削除 |
|  |  |  |
| pipelinedependencies | GET | `/pipelinedependencies/parent/{parent_id}/children` | 親→子の依存関係 |
| pipelinedependencies | GET | `/pipelinedependencies/child/{child_id}/parents` | 子→親の依存関係 |
| pipelinedependencies | GET | `/pipelinedependencies/chain/{pipeline_state_id}` | 双方向チェーン取得 |

Legacy 互換パス（将来削除予定）

- `/api/v1/pipelinestate` → 新: `/api/v1/pipelinestates`
- `/api/v1/pipelinedependency` → 新: `/api/v1/pipelinedependencies`

### リクエスト例

#### 測定データの作成（バルク）

```bash
curl -X POST "http://localhost:8000/api/v1/measurements/" \
  -H "Content-Type: application/json" \
  -d '{
    "measurements": [
      {
        "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
        "area_id": "550e8400-e29b-41d4-a716-446655440001",
        "local_time": "2024-01-15T09:30:00",
        "measured_at": 1705317000,
        "data_path": "/data/measurements/2024/01/measurement_001"
      }
    ]
  }'
```

#### 測定データの一覧取得（フィルタリング + ページング）

```bash
curl -X GET "http://localhost:8000/api/v1/measurements/?vehicle_id=550e8400-e29b-41d4-a716-446655440000&limit=20&offset=0"
```

安定したページングのため、`limit` と `offset` を標準化しました。

- 旧 `page` / `per_page` は後方互換のため当面サポートします（内部で `limit/offset` に変換）。
- デフォルトソートは `created_at DESC, id DESC` です（ページング間で順序が安定）。

件数のみを取得する場合は、同一フィルタで `/count` を呼び出してください。

```bash
curl -X GET "http://localhost:8000/api/v1/measurements/count?vehicle_id=550e8400-e29b-41d4-a716-446655440000"
# => { "result": true, "data": { "count": 1234 } }
```

#### 測定データの一括作成（複数件）

```bash
curl -X POST "http://localhost:8000/api/v1/measurements/" \
  -H "Content-Type: application/json" \
  -d '{
    "measurements": [
      {
        "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
        "area_id": "550e8400-e29b-41d4-a716-446655440001",
        "local_time": "2024-01-15T09:30:00",
        "measured_at": 1705317000,
        "data_path": "/data/measurements/2024/01/measurement_001"
      },
      {
        "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
        "area_id": "550e8400-e29b-41d4-a716-446655440001",
        "local_time": "2024-01-15T10:00:00",
        "measured_at": 1705318800,
        "data_path": "/data/measurements/2024/01/measurement_002"
      }
    ]
  }'
```

## テスト

```bash
# テストスクリプトの実行
python test_api.py
```

## API ドキュメント

FastAPIの自動生成ドキュメント：


## 件数取得（/count）エンドポイント（新規）

リストと同一のフィルタを受け付け、正確な件数を返します。レスポンス例: `{ "count": 123 }`。

- `GET /api/v1/vehicles/count`
- `GET /api/v1/measurements/count`
- `GET /api/v1/datastreams/count`
- `GET /api/v1/pipelines/count`

用途:
- ページネーションの総件数表示
- 軽量な統計・UX 最適化（一覧の並行取得と組み合わせ）

## レスポンス仕様の統一（変更点）

一覧系エンドポイントのレスポンスを、以下のシンプルな形式に統一しました。

- 旧: `BaseResponse[XXXListResponse]`（ボディに items と total/page/per_page を含む）
- 新: `BaseResponse[list[XXXResponse]]`（ボディは配列のみ）

対象エンドポイント:
- `GET /api/v1/measurements` → `BaseResponse[list[MeasurementResponse]]`
- `GET /api/v1/pipelinedata` → `BaseResponse[list[PipelineDataResponse]]`
- `GET /api/v1/pipelinestates` → `BaseResponse[list[PipelineStateResponse]]`
- `GET /api/v1/pipelinedependencies` → `BaseResponse[list[PipelineDependencyResponse]]`

備考:
- クエリパラメータは `limit`/`offset` を標準とし、`page`/`per_page` は後方互換のため当面サポートします。
- ボディ内のページネーションメタデータ（total/page/per_page）は廃止しました。
- 必要に応じて将来ヘッダー（例: `X-Total-Count`）での提供を検討できます。

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## データモデル

### Measurement

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | UUID | 一意識別子（自動生成） |
| vehicle_id | UUID | 車両ID |
| area_id | UUID | エリアID |
| local_time | datetime | ローカル時刻 |
| measured_at | integer | 測定時刻（UNIXタイムスタンプ） |
| data_path | string | データファイルのパス（オプション） |
| created_at | integer | 作成時刻（自動設定） |
| updated_at | integer | 更新時刻（自動更新） |

## エラーレスポンス

すべてのエラーレスポンスは以下の形式で返されます：

```json
{
  "success": false,
  "message": "エラーメッセージ",
  "error": "エラーの詳細",
  "data": null
}
```

## 制限事項

- バルクインサートは最大1000件まで（環境変数`BULK_INSERT_MAX_NUM`で設定可能）
- ページあたりの最大取得件数は100件

## 今後の実装予定

- DataStream APIの実装
- Vehicle/Driver APIの実装
- Scene/Tag APIの実装
- Pipeline関連APIの実装
- S3連携機能
- 非同期処理の実装
