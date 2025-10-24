"""model_factory.py - モデルファクトリ"""
import torch
import torch.nn as nn
from loguru import logger
from nfops_train.models import TrainSpec

try:
    import pytorch_lightning as pl
except ImportError:
    import lightning.pytorch as pl


class SimpleSeq2SeqModel(pl.LightningModule):
    """Simple Seq2Seq model for demonstration"""
ECHO is on.
    def __init__(
        self,
        input_size: int,
        h: int,
        hidden_dim: int = 128,
        lr: float = 1e-3,
        loss: str = "mse"
    ):
        super().__init__()
        self.save_hyperparameters()
ECHO is on.
        self.input_size = input_size
        self.h = h
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.loss_type = loss
ECHO is on.
        # Encoder
        self.encoder = nn.LSTM(
            input_size=1,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.1
        )
ECHO is on.
        # Decoder
        self.decoder = nn.Linear(hidden_dim, h)
ECHO is on.
        # Loss
        if loss == "mse":
            self.criterion = nn.MSELoss()
        elif loss == "mae":
            self.criterion = nn.L1Loss()
        else:
            self.criterion = nn.MSELoss()
ECHO is on.
    def forward(self, x):
        """Forward pass"""
        # x: (batch, input_size)
        x = x.unsqueeze(-1)  # (batch, input_size, 1)
ECHO is on.
        # Encode
        _, (h_n, _) = self.encoder(x)
ECHO is on.
        # Decode
        h_last = h_n[-1]  # (batch, hidden_dim)
        y_pred = self.decoder(h_last)  # (batch, h)
ECHO is on.
        return y_pred
ECHO is on.
    def training_step(self, batch, batch_idx):
        """Training step"""
        hist = batch['hist']
        futr = batch['futr']
ECHO is on.
        y_pred = self(hist)
        loss = self.criterion(y_pred, futr)
ECHO is on.
        self.log('train_loss', loss, prog_bar=True)
        return loss
ECHO is on.
    def validation_step(self, batch, batch_idx):
        """Validation step"""
        hist = batch['hist']
        futr = batch['futr']
ECHO is on.
        y_pred = self(hist)
        loss = self.criterion(y_pred, futr)
ECHO is on.
        # Calculate metrics
        mae = torch.abs(y_pred - futr).mean()
ECHO is on.
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_mae', mae, prog_bar=True)
ECHO is on.
        return loss
ECHO is on.
    def configure_optimizers(self):
        """Configure optimizer"""
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.lr
        )
        return optimizer


class ModelFactory:
    """Model factory"""
ECHO is on.
    @staticmethod
    def create(spec: TrainSpec) -> pl.LightningModule:
        """Create model"""
        logger.info(f"Creating model: {spec.model}")
ECHO is on.
        # For now, use simple model
        # TODO: Integrate NeuralForecast models
        model = SimpleSeq2SeqModel(
            input_size=spec.input_size,
            h=spec.h,
            hidden_dim=128,
            lr=spec.lr,
            loss=spec.loss
        )
ECHO is on.
        # Count parameters
        n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"Model parameters: {n_params:,}")
ECHO is on.
        return model
