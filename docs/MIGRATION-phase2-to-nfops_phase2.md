# phase2 → nfops_phase2 改名の安全移行ガイド

## 概要
将来 `phase2` 名前空間を `nfops_phase2` に統一するための段階的手順。破壊的変更を避けつつ周知期間を設ける。

## 手順
1. **新パッケージの用意**  
   `src/nfops_phase2/` を作り、`src/phase2/` の中身を移動。一時的に `pyproject.toml` の find/include は両方を含める。

2. **互換スタブ**  
   `src/phase2/__init__.py` で `DeprecationWarning` を出しつつ `from nfops_phase2 import *`。  
   `src/phase2/dq_runner.py` は `from nfops_phase2.dq_runner import *` へフォワード。

3. **エントリポイントの切替**  
   `pyproject.toml` の `[project.scripts] dq = "nfops_phase2.dq_runner:main"` へ。リポジトリローカルの `bin/dq` ラッパは `python -m nfops_phase2.dq_runner` に。

4. **参照置換 & テスト**  
   コード内 `import phase2...` → `import nfops_phase2...` を段階的に置換。`pytest -W default` で警告検証。

5. **旧名の撤去**  
   周知後のリリースで `src/phase2/` を削除し、`find.include` から `phase2*` を外す。

## 検証観点
- `dq --help` の動作  
- `python -m nfops_phase2.dq_runner --help` の成功  
- 旧 import での `DeprecationWarning` 発火（CI で捕捉）
