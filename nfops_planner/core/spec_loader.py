from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml
from loguru import logger


@dataclass
class InvalidRule:
    code: str
    message: str


@dataclass
class Spec:
    models: List[Dict[str, Any]]
    common: Dict[str, Any] = field(default_factory=dict)


class SpecLoader:
    def load(self, path: str | Path) -> Tuple[Spec, List[str]]:
        p = Path(path)
        logger.info(f"Loading spec from {p}")
        # YAML は UTF-8 で読む（ファイルも UTF-8 に統一済み）
        with p.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        # 必須: models
        if "models" not in raw:
            raise ValueError("E-SPEC-001: 'models' section is required")

        models = raw.get("models") or []
        common = raw.get("common") or {}

        if not isinstance(models, list):
            raise ValueError("E-SPEC-001: 'models' must be a list")

        # 致命的でない軽い検証（文字列リストで返す）
        invalids: List[str] = []
        for i, m in enumerate(models):
            if not isinstance(m, dict):
                invalids.append(f"E-MODEL-000: model[{i}] is not a mapping")
                continue
            if "name" not in m:
                invalids.append(f"E-MODEL-001: model[{i}] missing 'name'")
            if "params" in m and not isinstance(m["params"], dict):
                invalids.append(f"E-MODEL-002: model[{i}].params must be a mapping")

        return Spec(models=models, common=common), invalids
