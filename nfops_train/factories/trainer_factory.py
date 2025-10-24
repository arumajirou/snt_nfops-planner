"""trainer_factory.py - Trainerファクトリ"""
from pathlib import Path
from loguru import logger
from nfops_train.models import TrainSpec
from nfops_train.callbacks.resource_monitor import ResourceMonitor

try:
    import pytorch_lightning as pl
    from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
except ImportError:
    import lightning.pytorch as pl
    from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor


class TrainerFactory:
    """Trainer factory"""
    @staticmethod
    def create(
        spec: TrainSpec,
        checkpoint_dir: Path,
        alias: str
    ) -> pl.Trainer:
        """Create Trainer with callbacks"""
        logger.info(f"Creating Trainer for {alias}")
        # Checkpoint callback
        checkpoint_callback = ModelCheckpoint(
            dirpath=checkpoint_dir / alias,
            filename='best-{epoch:02d}-{val_loss:.4f}',
            monitor='val_loss',
            mode='min',
            save_top_k=1,
            save_last=True
        )
        # Early stopping
        early_stop_callback = EarlyStopping(
            monitor='val_loss',
            patience=5,
            mode='min',
            verbose=True
        )
        # Learning rate monitor
        lr_monitor = LearningRateMonitor(logging_interval='epoch')
        # Resource monitor
        resource_monitor = ResourceMonitor()
        # Create trainer
        trainer = pl.Trainer(
            max_epochs=spec.max_epochs,
            accelerator=spec.accelerator,
            devices=spec.devices,
            precision=spec.precision,
            callbacks=[
                checkpoint_callback,
                early_stop_callback,
                lr_monitor,
                resource_monitor
            ],
            enable_progress_bar=True,
            enable_model_summary=True,
            log_every_n_steps=10,
            deterministic=True
        )
        logger.success("Trainer created")
        return trainer
