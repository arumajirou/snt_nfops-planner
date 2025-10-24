"""artifact_bundler.py - Artifact収集"""
from pathlib import Path
from loguru import logger
from typing import List, Dict
import shutil


class ArtifactBundler:
    """Artifact bundler"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
    
    def bundle(
        self,
        checkpoint_path: Path,
        transform_dir: Path,
        features_dir: Path,
        output_dir: Path
    ) -> List[str]:
        """Bundle required artifacts"""
        logger.info("Bundling artifacts...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        bundled = []
        
        # 1. Checkpoint
        if checkpoint_path.exists():
            dest = output_dir / "model.ckpt"
            shutil.copy2(checkpoint_path, dest)
            bundled.append("model.ckpt")
            logger.success(f"Bundled checkpoint: {dest}")
        else:
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
        
        # 2. Transform metadata
        transform_meta = transform_dir / "y_transform.json"
        if transform_meta.exists():
            dest = output_dir / "y_transform.json"
            shutil.copy2(transform_meta, dest)
            bundled.append("y_transform.json")
            logger.success(f"Bundled transform: {dest}")
        
        # 3. Scaler
        scaler_path = transform_dir / "scaler.pkl"
        if scaler_path.exists():
            dest = output_dir / "scaler.pkl"
            shutil.copy2(scaler_path, dest)
            bundled.append("scaler.pkl")
            logger.success(f"Bundled scaler: {dest}")
        
        # 4. Feature catalog
        feature_catalog = features_dir / "feature_catalog.json"
        if feature_catalog.exists():
            dest = output_dir / "feature_catalog.json"
            shutil.copy2(feature_catalog, dest)
            bundled.append("feature_catalog.json")
            logger.success(f"Bundled feature catalog: {dest}")
        
        logger.success(f"Bundled {len(bundled)} artifacts")
        return bundled
