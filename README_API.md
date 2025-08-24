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
| POST | `/api/v1/measurements/` | 測定データの作成 |
| GET | `/api/v1/measurements/` | 測定データ一覧の取得 |
| GET | `/api/v1/measurements/{id}` | 特定の測定データの取得 |
| PUT | `/api/v1/measurements/{id}` | 測定データの更新 |
| DELETE | `/api/v1/measurements/{id}` | 測定データの削除 |
| POST | `/api/v1/measurements/bulk` | 測定データの一括作成 |

### リクエスト例

#### 測定データの作成

```bash
curl -X POST "http://localhost:8000/api/v1/measurements/" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
    "area_id": "550e8400-e29b-41d4-a716-446655440001",
    "local_time": "2024-01-15T09:30:00",
    "measured_at": 1705317000,
    "data_path": "/data/measurements/2024/01/measurement_001"
  }'
```

#### 測定データの一覧取得（フィルタリング付き）

```bash
curl -X GET "http://localhost:8000/api/v1/measurements/?vehicle_id=550e8400-e29b-41d4-a716-446655440000&page=1&per_page=20"
```

#### 測定データの一括作成

```bash
curl -X POST "http://localhost:8000/api/v1/measurements/bulk" \
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