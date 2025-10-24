# Phase 8 - XAI and Error Analysis

## 機能

- ErrorProfiler: ワースト予測の抽出
- ShapExplainer: SHAP値計算(線形近似)
- PermutationExplainer: Permutation重要度
- データ整列: features/preds/actuals結合
- XAIレポート: HTML出力

## 使用方法

```bash
# サンプルデータ生成
python examples\phase8\sample_data_phase8.py

# XAI分析実行
python -m nfops_xai.xai_runner \
  --features examples\phase8\test_features.parquet \
  --preds examples\phase8\test_preds.parquet \
  --actuals examples\phase8\test_actuals.parquet \
  --methods shap,perm \
  --topk-worst 50 \
  --out-dir artifacts\xai

# テスト実行
pytest tests\phase8 -v
```

## 出力

- artifacts/xai/shap_values.parquet: SHAP値
- artifacts/xai/permutation_importance.parquet: Permutation重要度
- artifacts/xai/worst_cases.parquet: ワーストケース
- artifacts/xai/xai_report.html: XAIレポート

## メトリクス

- global_importance: グローバル特徴量重要度
- local_explanations_count: ローカル説明数
- xai_build_sec: 処理時間
- worst_cases_analyzed: 分析済みワーストケース数

## 注意事項

- SHAP実装は線形近似の簡易版
- 本番環境では shap ライブラリの使用を推奨
- Permutationは再予測なしの簡易版
- 完全版にはCaptum統合が必要
