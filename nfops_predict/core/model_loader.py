"""model_loader.py - モデル読込"""
import torch
import json
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any


class ModelLoader:
    """Model loader"""
    def __init__(self, checkpoint_path: Path):
        """
        Args:
            checkpoint_path: Path to checkpoint file
        """
        self.checkpoint_path = Path(checkpoint_path)
    def load(self) -> Dict[str, Any]:
        """Load model and metadata"""
        logger.info(f"Loading model from {self.checkpoint_path}")
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
        # Load checkpoint
        checkpoint = torch.load(
            self.checkpoint_path,
            map_location='cpu'
        )
        # Extract hparams
        hparams = checkpoint.get('hyper_parameters', {})
        logger.info(f"Loaded model with hparams: {list(hparams.keys())}")
        return {
            'checkpoint': checkpoint,
            'hparams': hparams,
            'state_dict': checkpoint.get('state_dict', {})
        }
    def load_hparams_from_json(self, json_path: Path) -> Dict:
        """Load hparams from JSON file"""
        with open(json_path, encoding='utf-8') as f:
            return json.load(f)
