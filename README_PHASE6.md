# Phase 6 - Prediction and Probability System

## 機能

- 点予測: メディアン推定
- 分位予測: 複数分位点推定
- 予測区間(PI): 信頼区間構築
- 逆変換: Phase3メタからの復元
- 後校正: isotonic regression等
- 校正レポート: coverage/CRPS/NLL
- シナリオ管理: 複数futr対応

## 使用方法

```bash
# サンプルデータ生成
python examples\phase6\sample_data_phase6.py

# 予測実行
python -m nfops_predict.predict_runner \
  --input examples\phase6\sample_train.parquet \
  --ckpt checkpoints\SimpleSeq2Seq_h24_bs32\best.ckpt \
  --quantiles 0.1,0.5,0.9 \
  --scenario examples\phase6\scenarios\base.csv \
  --transform-meta examples\phase6\y_transform.json \
  --out-dir preds

# テスト実行
pytest tests\phase6 -v
```

## 出力

- preds/preds.parquet: 分位別予測
- preds/pi.parquet: 予測区間
- preds/calibration_report.html: 校正レポート

## メトリクス

- coverage@80/90/95: 実被覆率
- pinball_loss: 分位損失
- CRPS: 連続確率スコア
- NLL: 負対数尤度
