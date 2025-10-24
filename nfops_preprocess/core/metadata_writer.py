"""metadata_writer.py - メタデータ保存"""
import json
import pickle
from pathlib import Path
from loguru import logger
from nfops_preprocess.models import YTransformMeta


class MetadataWriter:
    """メタデータ保存"""
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def save_y_transform(self, meta: YTransformMeta):
        """Save y_transform.json"""
        path = self.output_dir / "y_transform.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(meta.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved: {path}")
    def save_scaler(self, scaler, filename: str = "scaler.pkl"):
        """Save scaler.pkl"""
        path = self.output_dir / filename
        with open(path, 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Saved: {path}")
