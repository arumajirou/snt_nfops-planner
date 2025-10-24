"""comb_counter.py - 邨・粋縺帶焚邂怜・"""
from typing import Dict
from dataclasses import dataclass
from loguru import logger


@dataclass
class CountResult:
    """繧ォ繧ヲ繝ウ繝育オ先棡"""
    total_combos: int
    per_model: Dict[str, int]
    computation_time_ms: float


class CombCounter:
    """邨・粋縺帶焚繧ォ繧ヲ繝ウ繧ソ繝シ"""
    def __init__(self, max_combos: int = 10000):
        self.max_combos = max_combos
    def count(self, spec, invalid_rules):
        logger.info("Counting combinations...")
        total = 0
        per_model = {}
        for model in spec.models:
            if not model.get("active", True):
                continue
            count = 1
            for param_name, param_def in model.get('params', {}).items():
                if isinstance(param_def, list):
                    count *= len(param_def)
            per_model[model['name']] = count
            total += count
        return CountResult(total_combos=total, per_model=per_model, computation_time_ms=0.0)
