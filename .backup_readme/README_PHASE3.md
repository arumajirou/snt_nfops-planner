# Phase 3 - Preprocessing System

## 機能

- Y変換: raw/diff/rolling_sum/cumsum
- スケーリング: standard/robust/minmax/log1p
- リーク防止: trainのみでfit
- 可逆性保証: 往復変換の一致

## 使用方法

```bash
# サンプルデータ生成
python examples\phase3\sample_data_phase3.py

# 前処理実行
python -m nfops_preprocess.preproc_runner \
  --input examples\phase3\sample_train.parquet \
  --y-type diff \
  --scaler robust \
  --scope per_series \
  --out-dir transform

# テスト実行
pytest tests\phase3 -v
```

## 出力

- transform/y_transform.json: 変換メタデータ
- transform/scaler.pkl: スケーラ
- transform/preprocessed_data.parquet: 処理済みデータ
