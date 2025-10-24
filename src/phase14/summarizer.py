# src/phase14/summarizer.py
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Dict, Any

TEMPLATE = """# バッチ結果ダイジェスト
- batch_id: {batch_id}
- gatekeeper: {register}
- sMAPE: {smape}
- 計画: trials≈{trials}, gpu_hours≈{gpu}
- 参照: {ref_dir}

## 所感（ルール→LLM流暢化の前段）
- 精度はしきい値{smape_max}以内: {within}
- 改善候補: 学習回数↑ or 探索空間の縮約（高コストhpの抑制）
"""

def build_summary(inputs: Dict[str, Any]) -> str:
    smape = inputs.get("smape", 0.18)
    smape_max = inputs.get("smape_max", 0.2)
    within = "YES" if smape <= smape_max else "NO"
    return TEMPLATE.format(
        batch_id=inputs.get("batch_id","unknown"),
        register=inputs.get("register","unknown"),
        smape=smape, smape_max=smape_max,
        trials=inputs.get("estimated_trials", 8),
        gpu=inputs.get("estimated_gpu_hours", 0.5),
        ref_dir=inputs.get("ref_dir","N/A")
    )
