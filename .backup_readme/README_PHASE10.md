# Phase 10 - Production Inference System

## 機能

- オンラインAPI: FastAPI推論サーバー
- バッチ推論: 大量データ処理
- キャッシュ: LRUキャッシュでレスポンス高速化
- Circuit Breaker: 障害時の自動遮断
- 監査ログ: JSONL形式の構造化ログ
- メトリクス: Prometheus互換エンドポイント

## 使用方法
```powershell
# 依存パッケージインストール
pip install fastapi uvicorn loguru click

# サンプルバッチ入力生成
python examples\phase10\sample_batch_input.py

# オンラインAPI起動
python nfops_inference\online\app.py

# 別ウィンドウでAPIテスト
# ヘルスチェック
Invoke-WebRequest -Uri http://localhost:8080/health | Select-Object -ExpandProperty Content

# バージョン情報
Invoke-WebRequest -Uri http://localhost:8080/version | Select-Object -ExpandProperty Content

# メトリクス
Invoke-WebRequest -Uri http://localhost:8080/metrics | Select-Object -ExpandProperty Content

# 予測リクエスト (JSONファイルを使用)
$json = Get-Content examples\phase10\sample_request.json -Raw
Invoke-WebRequest -Uri http://localhost:8080/predict -Method Post -Body $json -ContentType "application/json" | Select-Object -ExpandProperty Content

# バッチ推論
python -m nfops_inference.batch.batch_infer `
  --input examples\phase10\batch_input.parquet `
  --output preds\prod\prod_preds.parquet `
  --model-name sales_demand_D `
  --version 27 `
  --scenario base `
  --quantiles 0.1,0.5,0.9 `
  --micro-batch 1024

# テスト実行
pytest tests\phase10 -v
```

## エンドポイント

### GET /health
ヘルスチェック

### GET /version
モデルバージョン情報

### GET /metrics
Prometheus形式メトリクス

### POST /predict
予測リクエスト

## 出力

- preds/prod/prod_preds.parquet: バッチ予測結果
- logs/inference/inference.log: 監査ログ (JSONL)

## メトリクス

- cache_hit_rate: キャッシュヒット率
- cache_size: キャッシュサイズ
- circuit_breaker_state: サーキットブレーカー状態

## アーキテクチャ
```
Request → FastAPI → Router → Cache → Predictor → Response
                           ↓
                    Circuit Breaker
                           ↓
                      Audit Logger
```

## 注意事項

- 予測ロジックは簡易実装（ランダム）
- 本番環境では実際のモデルロード処理が必要
- キャッシュはインメモリ（Redisなど推奨）
- メトリクスはPrometheus collectで収集推奨
