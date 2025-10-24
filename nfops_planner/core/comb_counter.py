"""comb_counter.py - 邨・粋縺帶焚邂怜・"""
from typing import Dict
from dataclasses import dataclass
from loguru import logger


@dataclass
class CountResult:
    """繧ｫ繧ｦ繝ｳ繝育ｵ先棡"""
    total_combos: int
    per_model: Dict[str, int]
    computation_time_ms: float


class CombCounter:
    """邨・粋縺帶焚繧ｫ繧ｦ繝ｳ繧ｿ繝ｼ"""
    def __init__(self, max_combos: int = 10000):
        self.max_combos = max_combos
ECHO は <OFF> です。
    def count(self, spec, invalid_rules):
        logger.info("Counting combinations...")
        total = 0
        per_model = {}
        for model in spec.models:
            count = 1
            for param_name, param_def in model.get('params', {}).items():
                if isinstance(param_def, list):
                    count *= len(param_def)
            per_model[model['name']] = count
            total += count
        return CountResult(total_combos=total, per_model=per_model, computation_time_ms=0.0)
