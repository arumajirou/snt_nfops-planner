"""model_loader.py - モデル読込"""
import torch
import json
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any


class ModelLoader:
    """Model loader"""
ECHO is on.
    def __init__(self, checkpoint_path: Path):
        """
        Args:
            checkpoint_path: Path to checkpoint file
        """
        self.checkpoint_path = Path(checkpoint_path)
ECHO is on.
    def load(self) -> Dict[str, Any]:
        """Load model and metadata"""
        logger.info(f"Loading model from {self.checkpoint_path}")
ECHO is on.
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
ECHO is on.
        # Load checkpoint
        checkpoint = torch.load(
            self.checkpoint_path,
            map_location='cpu'
        )
ECHO is on.
        # Extract hparams
        hparams = checkpoint.get('hyper_parameters', {})
ECHO is on.
        logger.info(f"Loaded model with hparams: {list^(hparams.keys^(^)^)}")
ECHO is on.
        return {
            'checkpoint': checkpoint,
            'hparams': hparams,
            'state_dict': checkpoint.get('state_dict', {})
        }
ECHO is on.
    def load_hparams_from_json(self, json_path: Path) -> Dict:
        """Load hparams from JSON file"""
        with open(json_path, encoding='utf-8') as f:
            return json.load(f)
