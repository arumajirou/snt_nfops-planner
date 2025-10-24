"""train_runner.py - CLI"""
import click
import pandas as pd
import yaml
import json
from pathlib import Path
from loguru import logger
from datetime import datetime
import time
from nfops_train.models import TrainSpec, TrialState, TrialResult
from nfops_train.core.dataset_builder import DatasetBuilder
from nfops_train.factories.model_factory import ModelFactory
from nfops_train.factories.trainer_factory import TrainerFactory
from nfops_train.core.checkpoint_manager import CheckpointManager
from nfops_train.utils.logging_config import setup_logging
import torch


def run_single_trial(
    spec: TrainSpec,
    df: pd.DataFrame,
    train_end,
    val_end,
    checkpoint_dir: Path,
    alias: str
) -> TrialResult:
    """Run single training trial"""
    start_time = time.time()
    try:
        # Set seed
        torch.manual_seed(spec.seed)
        # Build dataset
        datamodule = DatasetBuilder.build(
            df=df,
            train_end=train_end,
            val_end=val_end,
            h=spec.h,
            input_size=spec.input_size,
            batch_size=spec.batch_size
        )
        # Create model
        model = ModelFactory.create(spec)
        # Create trainer
        trainer = TrainerFactory.create(spec, checkpoint_dir, alias)
        # Train
        logger.info(f"Starting training: {alias}")
        trainer.fit(model, datamodule)
        # Get best metric
        best_metric = trainer.callback_metrics.get('val_loss', None)
        if best_metric is not None:
            best_metric = float(best_metric.item())
        # Find best checkpoint
        ckpt_mgr = CheckpointManager(checkpoint_dir)
        best_ckpt = ckpt_mgr.find_best(alias)
        duration = time.time() - start_time
        result = TrialResult(
            alias=alias,
            state=TrialState.COMPLETED,
            best_metric=best_metric,
            duration_sec=duration,
            gpu_peak_mb=None,
            checkpoint_path=str(best_ckpt) if best_ckpt else None
        )
        logger.success(f"Trial completed: {alias} in {duration:.1f}s")
        return result
    except Exception as e:
        logger.exception(f"Trial failed: {alias}")
        duration = time.time() - start_time
        return TrialResult(
            alias=alias,
            state=TrialState.FAILED,
            best_metric=None,
            duration_sec=duration,
            gpu_peak_mb=None,
            checkpoint_path=None
        )


@click.command()
@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--matrix', type=click.Path(exists=True), required=True)
@click.option('--backend', default='simple', type=click.Choice(['simple', 'ray', 'optuna']))
@click.option('--max-trials', default=1, type=int)
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='checkpoints/')
def main(input, matrix, backend, max_trials, emit_mlflow, out_dir):
    """Training Runner - Phase 5"""
    setup_logging()
    logger.info("Starting training...")
    try:
        # 1. データ読込
        logger.info(f"Loading data from {input}")
        if input.endswith('.parquet'):
            df = pd.read_parquet(input)
        else:
            df = pd.read_csv(input, parse_dates=['ds'])
        logger.info(f"Loaded {len(df)} rows")
        # 2. Matrix読込
        with open(matrix, encoding='utf-8') as f:
            matrix_spec = yaml.safe_load(f)
        # 3. Split決定
        train_end = pd.to_datetime('2024-06-01')
        val_end = pd.to_datetime('2024-07-01')
        # 4. 簡易実行 (backend=simple)
        if backend == 'simple':
            # First model only
            model_spec = matrix_spec['models'][0]
            spec = TrainSpec(
                model=model_spec['name'],
                h=24,
                input_size=48,
                batch_size=32,
                max_epochs=10,
                loss='mse',
                lr=1e-3,
                seed=42,
                precision='32',
                accelerator='cpu',
                devices=1
            )
            alias = f"{spec.model}_h{spec.h}_bs{spec.batch_size}"
            result = run_single_trial(
                spec=spec,
                df=df,
                train_end=train_end,
                val_end=val_end,
                checkpoint_dir=Path(out_dir),
                alias=alias
            )
            # Save result
            results_dir = Path('combos') / alias
            results_dir.mkdir(parents=True, exist_ok=True)
            with open(results_dir / 'result.json', 'w') as f:
                json.dump({
                    'alias': result.alias,
                    'state': result.state.value,
                    'best_metric': result.best_metric,
                    'duration_sec': result.duration_sec
                }, f, indent=2)
            logger.success(f"Training completed: {result.state.value}")
            if result.best_metric:
                logger.info(f"Best val_loss: {result.best_metric:.4f}")
        else:
            logger.warning(f"Backend {backend} not yet implemented")
        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
