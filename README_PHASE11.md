# Phase 11 - Monitoring System (Drift & Accuracy)

## 機能

- データドリフト検知: PSI, KS検定
- 精度監視: ローリングSMAPE, MAE
- カバレッジ監視: 経験的カバレッジvsノミナル
- HTMLレポート生成
- JSONアラート生成
- 自動しきい値判定

## 使用方法
```powershell
# 依存パッケージインストール
pip install scipy

# サンプルデータ生成
python examples\phase11\sample_monitor_data.py

# 監視実行
python -m nfops_monitor.monitor_runner `
  --reference examples\phase11\reference.parquet `
  --current examples\phase11\current.parquet `
  --features feature_1,feature_2,feature_3 `
  --psi-warning 0.1 `
  --psi-critical 0.25 `
  --smape-increase-critical 20.0 `
  --coverage-gap-critical 5.0 `
  --out-dir monitor

# 結果確認
start monitor\drift_report.html
Get-Content alerts\alert.json

# テスト実行
pytest tests\phase11 -v
```

## 出力

- monitor/drift_report.html: ドリフト/精度レポート
- alerts/alert.json: アラート情報

## メトリクス

### ドリフト
- PSI (Population Stability Index): 分布の安定性
- KS統計量とp値: 分布の差の検定

### 精度
- SMAPE: Symmetric Mean Absolute Percentage Error
- MAE: Mean Absolute Error
- Delta %: 参照期間からの変化率

### カバレッジ
- Empirical Coverage: 実測カバレッジ
- Gap: ノミナルとのギャップ（ポイント）

## アラートレベル

- **OK**: 正常範囲内
- **WARNING**: 注意が必要
- **CRITICAL**: 即座の対応が必要

## しきい値 (デフォルト)

- PSI Warning: 0.1
- PSI Critical: 0.25
- KS Alpha: 0.01
- SMAPE Increase Critical: 20%
- Coverage Gap Critical: 5pt

## 推奨アクション

### Data Drift検出時
- Phase 4: 特徴量エンジニアリング見直し
- データソースの変更確認

### Accuracy Drop検出時
- Phase 5: HPO再実行または再学習
- モデルアーキテクチャ見直し

### Coverage Gap検出時
- Phase 6: 校正の再適用
- 分位予測の見直し

## 注意事項

- 簡易実装のため一部統計手法は近似
- 本番環境ではEvidentlyやGreat Expectations推奨
- マルチテスト補正は未実装
