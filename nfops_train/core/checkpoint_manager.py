"""checkpoint_manager.py - チェックポイント管理"""
import torch
from pathlib import Path
from loguru import logger
from typing import Optional


class CheckpointManager:
    """Checkpoint manager"""
ECHO is on.
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
ECHO is on.
    def find_best(self, alias: str) -> Optional[Path]:
        """Find best checkpoint for alias"""
        alias_dir = self.checkpoint_dir / alias
ECHO is on.
        if not alias_dir.exists():
            return None
ECHO is on.
        # Look for best checkpoint
        best_ckpts = list(alias_dir.glob('best-*.ckpt'))
        if best_ckpts:
            return best_ckpts[0]
ECHO is on.
        # Fallback to last
        last_ckpt = alias_dir / 'last.ckpt'
        if last_ckpt.exists():
            return last_ckpt
ECHO is on.
        return None
ECHO is on.
    def validate(self, ckpt_path: Path) -> bool:
        """Validate checkpoint integrity"""
        try:
            state = torch.load(ckpt_path, map_location='cpu')
            required_keys = ['state_dict', 'hyper_parameters']
ECHO is on.
            for key in required_keys:
                if key not in state:
                    logger.warning(f"Missing key in checkpoint: {key}")
                    return False
ECHO is on.
            logger.info(f"Checkpoint valid: {ckpt_path}")
            return True
ECHO is on.
        except Exception as e:
            logger.error(f"Checkpoint validation failed: {e}")
            return False
