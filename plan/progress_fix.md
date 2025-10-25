| Phase | Task | Owner | Start | End | Status | Risk | NextAction |
|---|---|---|---|---|---:|---|---|
| CI | mainへ最小CI(gate/dq/pytest)反映 (#9/#10) | az | 2025-10-25 | 2025-10-26 | 30 | main未反映のままdispatch | #9/#10を先にmerge/再Run |
| CI | pytest軽量セットの安定化(ImportError解消) | az | 2025-10-25 | 2025-10-27 | 20 | scipy不足 | requirements-devにscipy追加 |
| CI | heavy分離(ラベル/手動/夜間) | az | 2025-10-26 | 2025-10-28 | 0 | torch導入に時間 | CPU版torchでheavyを別実行 |
| P2 | dqスモーク整備(--schema必須を満たす) | az | 2025-10-25 | 2025-10-27 | 10 | スキーマ未配置PR | ワークフローでサンプル生成 |
| P2 | outputs/phase2アーティファクト保存 | az | 2025-10-26 | 2025-10-27 | 0 | 生成物散逸 | upload-artifactで固定化 |
| P5/6 | 遅延import/IF分離 + @pytest.mark.heavy | az | 2025-10-27 | 2025-10-31 | 0 | 参照箇所多い | 影響範囲をrgで棚卸し |
| P11 | scipy>=1.11を通常CIに導入 | az | 2025-10-25 | 2025-10-25 | 0 | numpy互換 | wheels想定で導入可 |
| Ops | pipログの可視化(ヒット率集計) | az | 2025-10-28 | 2025-10-30 | 0 | ログ欠落 | -vv + artifact化で担保 |
