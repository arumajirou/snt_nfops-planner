# Phase 4 - Feature Engineering System

## 機能

- ラグ特徴: regular/seasonal
- 移動統計: rolling mean/std/min/max/ema
- カレンダー特徴: dow/month/祝日
- 価格/販促特徴: pct_change/promo_flag
- DTWクラスタリング: k-medoids
- カテゴリエンコーディング: one-hot/target

## 使用方法

```bash
# サンプルデータ生成
python examples\phase4\sample_data_phase4.py

# 特徴量生成
python -m nfops_features.feat_runner \
  --input examples\phase4\sample_train.parquet \
  --config configs\features.yml \
  --clusters 8 \
  --output-format long \
  --out-dir features

# テスト実行
pytest tests\phase4 -v
```

## 出力

- features/features.parquet: 特徴量テーブル
- features/cluster_labels.parquet: クラスタラベル
- features/feature_catalog.json: 特徴カタログ
