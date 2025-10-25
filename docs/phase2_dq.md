# Phase 2 Data Quality Runner
## 実行例
- 一括: `bin/dq --input tests/data/sample.csv --schema schema/example_schema.json --strict-columns --profile`
- チャンク: `bin/dq --input tests/data/sample.csv --schema schema/example_schema.json --chunksize 200000 --invalid-cap 50000 --invalid-rate-threshold 0.05`

## 生成物とスキーマ
- outputs/phase2/<alias>/invalid_rows.parquet
- outputs/phase2/<alias>/data_profiling.html  ( --profile 時 )
- outputs/phase2/<alias>/summary.json
  - n_rows, n_invalid_rows, invalid_rate, checks[], schema_hash, content_hash, encoding_used, chunksize, invalid_cap, strict_columns, created_at

## 失敗時の終了コード
- 2: 入力/スキーマが存在しない、引数不足（bin/dq で検知）
- 1: 品質ゲート（invalid 行あり or invalid_rate 閾値超過）
