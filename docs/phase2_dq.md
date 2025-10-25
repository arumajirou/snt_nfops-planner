# Phase 2 Data Quality Runner
## 実行例
- GX 前段ゲート（任意）: `make dq.ge` で `bin/gx-run` を実行後に DQ を実行（checkpoint 未配置時はスキップ）
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

## 雛形推定のロジックとフラグ
- `--infer-rows` (default 10000): 雛形推定で読むサンプル行数
- 型判定しきい値: 60% 以上が解釈可能ならその型（数値/日付/bool）
- 数値: `range: {min,max}` を付与
- 文字列: 低カーディナリティ(<=50 かつ distinct/n <= 0.2)なら `allowed` を付与
- 必須: 欠損率 0% で `required: true`
- PK 推奨: `unique_id+ds` が重複しなければ推奨、無ければ単独ユニーク列を候補化
- PK 推奨ヒューリスティック: `["unique_id","ds"]` がユニークなら推奨。次点で `id|key|code` を含む単一列がユニークなら推奨。測定列は推奨しない。
