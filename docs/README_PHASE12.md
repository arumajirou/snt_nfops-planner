# Phase 1.2: 分位ループと CLI/ENV の入力仕様（強化）
- `--importance-quantiles` または `NFOPS_IMPORTANCE_QUANTILES` で分位列を指定できます。
- 入力は「0–1 の小数 CSV」。例: `0.4,0.5,0.7,0.9`
- **無効入力**（非数値/範囲外/空列）は **既定 `(0.3..0.9)` へフォールバック**し、`stderr` に警告を出します。
- `assumptions.json` には常に `reduction_strategy=importance_quantile_loop` が入ります（テストで一意確認）。
