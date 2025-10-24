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
        self.input_size = input_size
        self.h = h
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.loss_type = loss
        # Encoder
        self.encoder = nn.LSTM(
            input_size=1,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.1
        )
        # Decoder
        self.decoder = nn.Linear(hidden_dim, h)
        # Loss
        if loss == "mse":
            self.criterion = nn.MSELoss()
        elif loss == "mae":
            self.criterion = nn.L1Loss()
        else:
            self.criterion = nn.MSELoss()
    def forward(self, x):
        """Forward pass"""
        # x: (batch, input_size)
        x = x.unsqueeze(-1)  # (batch, input_size, 1)
        # Encode
        _, (h_n, _) = self.encoder(x)
        # Decode
        h_last = h_n[-1]  # (batch, hidden_dim)
        y_pred = self.decoder(h_last)  # (batch, h)
        return y_pred
    def training_step(self, batch, batch_idx):
        """Training step"""
        hist = batch['hist']
        futr = batch['futr']
        y_pred = self(hist)
        loss = self.criterion(y_pred, futr)
        self.log('train_loss', loss, prog_bar=True)
        return loss
    def validation_step(self, batch, batch_idx):
        """Validation step"""
        hist = batch['hist']
        futr = batch['futr']
        y_pred = self(hist)
        loss = self.criterion(y_pred, futr)
        # Calculate metrics
        mae = torch.abs(y_pred - futr).mean()
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_mae', mae, prog_bar=True)
        return loss
    def configure_optimizers(self):
        """Configure optimizer"""
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.lr
        )
        return optimizer


class ModelFactory:
    """Model factory"""
    @staticmethod
    def create(spec: TrainSpec) -> pl.LightningModule:
        """Create model"""
        logger.info(f"Creating model: {spec.model}")
        # For now, use simple model
        # TODO: Integrate NeuralForecast models
        model = SimpleSeq2SeqModel(
            input_size=spec.input_size,
            h=spec.h,
            hidden_dim=128,
            lr=spec.lr,
            loss=spec.loss
        )
        # Count parameters
        n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"Model parameters: {n_params:,}")
        return model
