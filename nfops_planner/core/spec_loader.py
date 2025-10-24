"""spec_loader.py - 仕様読込"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import pandas as pd
from pydantic import BaseModel, Field
from loguru import logger


class Spec(BaseModel):
    """仕様�E冁E��表現"""
    models: List[Dict] = []
    common: Dict = {}


class InvalidRule(BaseModel):
    """無効値ルール"""
    model: str
    param_a: str
    operator: str
    value: Any
    reason: str


class SpecLoader:
    """仕様読込"""
    def load(self, spec_path: Path, invalid_path: Optional[Path] = None):
        logger.info(f"Loading spec from {spec_path}")
        with open(spec_path) as f:
            raw = yaml.safe_load(f)
        spec = Spec(**raw)
        invalids = []
        if invalid_path:
            df = pd.read_csv(invalid_path)
            for _, row in df.iterrows():
                invalids.append(InvalidRule(**row.to_dict()))
        return spec, invalids
