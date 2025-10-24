"""config_loader.py - 設定読込"""
import yaml
from pathlib import Path
from loguru import logger
from nfops_features.models import FeatSpec


class ConfigLoader:
    """Feature configuration loader"""
    def load(self, config_path: Path) -> FeatSpec:
        """Load feature config"""
        logger.info(f"Loading config from {config_path}")
        with open(config_path, encoding='utf-8') as f:
            raw = yaml.safe_load(f)
        spec = FeatSpec(
            hist=raw.get('hist', {}),
            calendar=raw.get('calendar', []),
            price=raw.get('price'),
            promo=raw.get('promo'),
            stat=raw.get('stat'),
            futr=raw.get('futr')
        )
        logger.success(f"Config loaded: {len(spec.calendar)} calendar features")
        return spec
