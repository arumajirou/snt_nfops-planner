"""catalog_writer.py - 特徴カタログ出力"""
import json
from pathlib import Path
from loguru import logger
from nfops_features.models import FeatureCatalog


class CatalogWriter:
    """Feature catalog writer"""
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def write(self, catalog: FeatureCatalog):
        """Write feature catalog"""
        path = self.output_dir / "feature_catalog.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(catalog.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved catalog: {path}")
