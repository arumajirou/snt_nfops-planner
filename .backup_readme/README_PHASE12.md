# Phase 12 - Observability System (Resources, Cost, Audit)

## 機能

- メトリクス収集: システムリソース（CPU, RAM, GPU）
- コスト計算: 電力/GPU時間からコストとCO2算出
- Grafanaダッシュボード生成: Overview, Audit
- Prometheusアラートルール生成: SLO, GPU, CO2
- 監査ログ: JSONL形式の構造化ログ

## 使用方法
```powershell
# 依存パッケージインストール
pip install psutil pyyaml

# 全機能実行
python -m nfops_observability.observability_runner `
  --collect-metrics `
  --calculate-cost `
  --generate-dashboards `
  --generate-alerts `
  --log-audit `
  --energy-kwh 10.0 `
  --gpu-hours 5.0

# 個別実行例

# メトリクス収集のみ
python -m nfops_observability.observability_runner --collect-metrics

# コスト計算のみ
python -m nfops_observability.observability_runner --calculate-cost --energy-kwh 15.0 --gpu-hours 8.0

# ダッシュボード生成のみ
python -m nfops_observability.observability_runner --generate-dashboards --out-dir grafana\dashboards

# アラートルール生成のみ
python -m nfops_observability.observability_runner --generate-alerts --rules-dir prometheus\rules

# テスト実行
pytest tests\phase12 -v
```

## 出力

### メトリクス
- monitor/metrics.txt: Prometheus形式のメトリクス

### ダッシュボード
- grafana/dashboards/00_overview.json: 概要ダッシュボード
- grafana/dashboards/40_audit.json: 監査ダッシュボード

### アラートルール
- prometheus/rules/slo.yaml: SLOアラート
- prometheus/rules/gpu.yaml: GPUアラート
- prometheus/rules/co2.yaml: CO2/コストアラート

### ログ
- logs/audit/audit.log: 監査ログ（JSONL）

## メトリクス

### システム
- nf_gpu_util: GPU使用率（%）
- nf_vram_used_gb: VRAM使用量（GB）
- nf_cpu_percent: CPU使用率（%）
- nf_ram_used_gb: RAM使用量（GB）

### コスト/CO2
- nf_co2_kg: CO2排出量（kg）
- nf_cost_usd: コスト（USD）
- codecarbon_energy_kwh: 電力消費（kWh）

### 推論
- nf_infer_latency_ms_bucket: レイテンシヒストグラム
- nf_infer_requests_total: リクエスト総数
- nf_infer_errors_total: エラー総数

## アラート

### SLO
- InferenceLatencyHigh: p95レイテンシ>250ms
- InferenceErrorRateHigh: エラー率>0.5%

### GPU
- ZombieGPUProcess: Podなしでリソース使用
- GPUUtilizationLow: GPU使用率<20%

### CO2/コスト
- CO2BudgetExceeded: 週次CO2予算超過
- CostBudgetExceeded: 週次コスト予算超過

## 監査イベント

- PROMOTE: モデル昇格
- PREDICT: 予測リクエスト
- REGISTRY: レジストリ操作
- LOGIN: ログイン

## 価格設定

pricing/electricity.yaml: 地域別電力価格とカーボン強度
pricing/gpu.yaml: GPUタイプ別時間単価

## 注意事項

- GPU情報取得は簡易実装（pynvml推奨）
- 実際のPrometheus/Grafana統合が必要
- 監査ログは最小構成
