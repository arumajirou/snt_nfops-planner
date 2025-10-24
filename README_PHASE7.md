# Phase 7 - Evaluation and Statistical Testing

## 機能

- データ整列: 予測と実測の結合
- 指標計算: SMAPE/MAE/RMSE/MAPE
- 統計検定: Diebold-Mariano検定
- 被覆率検定: 二項検定
- 効果量: Cliff's delta/A12/Hedges' g
- 多重比較補正: BH/Holm法
- 評価レポート: HTML出力

## 使用方法

```bash
# サンプルデータ生成
python examples\phase7\sample_data_phase7.py

# 評価実行
python -m nfops_eval.eval_runner \
  --preds examples\phase7\test_preds.parquet \
  --actuals examples\phase7\test_actuals.parquet \
  --baseline-run test_run \
  --metrics SMAPE,MAE,RMSE \
  --out-dir eval

# テスト実行
pytest tests\phase7 -v
```

## 出力

- eval/eval_report.html: 評価レポート
- eval/tests.json: 検定結果
- eval/compare_table.parquet: 比較テーブル

## メトリクス

- SMAPE: Symmetric MAPE
- MAE: Mean Absolute Error
- RMSE: Root Mean Squared Error
- MAPE: Mean Absolute Percentage Error
- CRPS: Continuous Ranked Probability Score (planned)
