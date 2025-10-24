"""checkpoint_manager.py - チェックポイント管理"""
import torch
from pathlib import Path
from loguru import logger
from typing import Optional


class CheckpointManager:
    """Checkpoint manager"""
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    def find_best(self, alias: str) -> Optional[Path]:
        """Find best checkpoint for alias"""
        alias_dir = self.checkpoint_dir / alias
        if not alias_dir.exists():
            return None
        # Look for best checkpoint
        best_ckpts = list(alias_dir.glob('best-*.ckpt'))
        if best_ckpts:
            return best_ckpts[0]
        # Fallback to last
        last_ckpt = alias_dir / 'last.ckpt'
        if last_ckpt.exists():
            return last_ckpt
        return None
    def validate(self, ckpt_path: Path) -> bool:
        """Validate checkpoint integrity"""
        try:
            state = torch.load(ckpt_path, map_location='cpu')
            required_keys = ['state_dict', 'hyper_parameters']
            for key in required_keys:
                if key not in state:
                    logger.warning(f"Missing key in checkpoint: {key}")
                    return False
            logger.info(f"Checkpoint valid: {ckpt_path}")
            return True
        except Exception as e:
            logger.error(f"Checkpoint validation failed: {e}")
            return False
