| Phase | Task | Owner | Start | End | Status | Risk | NextAction |
|---|---|---|---|---|---:|---|---|
| P10 | リポジトリ初期化＋最小CI(pytest) | az | 2025-10-25 | 2025-10-25 | 20 | 依存未固定 | requirements定義を追加 |
| P11 | .gitignore/構成雛形整備 | az | 2025-10-25 | 2025-10-26 | 10 | 不要物混入 | 生成物パスを棚卸し |
| P12 | 可観測性ダッシュボード設計(MLflow/ELK/Grafana) | az | 2025-10-25 | 2025-10-27 | 30 | メトリクス選定未確定 | サンプル板をcommit |
| P20 | Phase1: ドライラン見積(CombCounter/Estimator/Report) | az | 2025-10-26 | 2025-10-30 | 10 | 過去runs不足 | ダミーデータで推定検証 |
| P30 | Phase2: データ取込/品質(dq_runner, schema.json) | az | 2025-10-27 | 2025-11-01 | 0 | スキーマ未合意 | schemaドラフト提出 |
| P40 | Phase3: 前処理(y変換/スケーラ, 可逆) | az | 2025-10-29 | 2025-11-03 | 0 | 逆変換仕様抜け | y_transform設計レビュー |
| P50 | nf_runner: 単一/マトリクス実行・Capability検証 | az | 2025-10-30 | 2025-11-08 | 0 | 無効組合せが多い | capability表初版コミット |
| P60 | RDB/MLflow: 実行順・スキーマ厳守で統合 | az | 2025-11-02 | 2025-11-10 | 0 | PK/UK競合 | DDL/UPSERT方針確定 |
| P70 | 全体アーキテクチャ整合/知識ポータル更新 | az | 2025-11-05 | 2025-11-12 | 0 | 所管分散 | 責務とIFを明文化 |
