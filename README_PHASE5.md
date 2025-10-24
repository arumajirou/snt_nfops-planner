# Phase 5 - Training and HPO System

## 機能

- Lightning DataModule: 時系列データセット構築
- モデルファクトリ: Seq2Seq/NeuralForecast対応
- Trainerファクトリ: Callbacks/Strategy設定
- リソース監視: GPU/CPU/RAM/VRAM
- チェックポイント管理: 検証・復元

## 使用方法

```bash
# サンプルデータ生成
python examples\phase5\sample_data_phase5.py

# 学習実行 (simple backend)
python -m nfops_train.train_runner \
  --input examples\phase5\sample_train.parquet \
  --matrix examples\phase5\matrix_spec.yaml \
  --backend simple \
  --max-trials 1 \
  --out-dir checkpoints

# テスト実行
pytest tests\phase5 -v
```

## 出力

- checkpoints/<alias>/best.ckpt: ベストモデル
- combos/<alias>/result.json: 実行結果
- logs/train_*.log: 実行ログ

## 今後の拡張

- Ray Tune統合
- Optuna統合
- HPO/枝刈り/再開機能
- MLflow統合
