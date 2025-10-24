"""predict_runner.py - CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_predict.core.model_loader import ModelLoader
from nfops_predict.core.futr_loader import FutrLoader
from nfops_predict.predictors.predictor import Predictor
from nfops_predict.predictors.pi_constructor import PIConstructor
from nfops_predict.core.inverse_restorer import InverseRestorer
from nfops_predict.calibrators.calibrator import Calibrator
from nfops_predict.core.reporter import Reporter
from nfops_predict.utils.logging_config import setup_logging
import time


@click.command()
@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--ckpt', type=click.Path(exists=True), required=True)
@click.option('--quantiles', default='0.1,0.5,0.9')
@click.option('--scenario', 'scenarios', multiple=True, help='Future scenarios')
@click.option('--calibrate', default='none', type=click.Choice(['none', 'isotonic']))
@click.option('--transform-meta', type=click.Path(), default=None)
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='preds/')
def main(input, ckpt, quantiles, scenarios, calibrate, transform_meta, emit_mlflow, out_dir):
    """Prediction Runner - Phase 6"""
    setup_logging()
    logger.info("Starting prediction...")
ECHO is on.
    start_time = time.time()
ECHO is on.
    try:
        # 1. Parse quantiles
        qs = [float(q.strip()) for q in quantiles.split(',')]
        logger.info(f"Quantiles: {qs}")
ECHO is on.
        # 2. Load model
        model_loader = ModelLoader(Path(ckpt))
        model_ctx = model_loader.load()
ECHO is on.
        # 3. Load data
        logger.info(f"Loading data from {input}")
        if input.endswith('.parquet'):
            df = pd.read_parquet(input)
        else:
            df = pd.read_csv(input, parse_dates=['ds'])
        logger.info(f"Loaded {len^(df^)} rows")
ECHO is on.
        # 4. Create predictor
        predictor = Predictor(
            model=None,  # Simplified
            hparams=model_ctx['hparams']
        )
ECHO is on.
        # 5. Predict
        result = predictor.predict_quantiles(
            df=df,
            quantiles=qs,
            scenario_id="base",
            run_id="test_run"
        )
ECHO is on.
        # 6. Construct PI
        pi_constructor = PIConstructor(alpha=0.1)
        pi_df = pi_constructor.construct_from_quantiles(result.df)
ECHO is on.
        # 7. Inverse transform
        if transform_meta:
            inverse_restorer = InverseRestorer(Path(transform_meta))
            result.df = inverse_restorer.inverse(result.df)
ECHO is on.
        # 8. Calibration
        if calibrate != 'none':
            calibrator = Calibrator(method=calibrate)
            # Note: Need validation data to fit calibrator
            # result.df = calibrator.calibrate(result.df)
            logger.info("Calibration skipped ^(needs validation data^)")
ECHO is on.
        # 9. Save results
        output_dir = Path(out_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
ECHO is on.
        # Predictions
        preds_path = output_dir / "preds.parquet"
        result.df.to_parquet(preds_path)
        logger.success(f"Saved predictions: {preds_path}")
ECHO is on.
        # PI
        pi_path = output_dir / "pi.parquet"
        pi_df.to_parquet(pi_path)
        logger.success(f"Saved PI: {pi_path}")
ECHO is on.
        # 10. Generate report
        reporter = Reporter(output_dir)
        metrics = reporter.compute_metrics(result.df)
        reporter.generate_html(result.df, metrics)
ECHO is on.
        # 11. Summary
        elapsed = time.time() - start_time
        logger.success(f"Prediction completed in {elapsed:.1f}s")
        logger.info(f"Total predictions: {len^(result.df^)}")
        logger.info(f"Coverage@90: {metrics.coverage_90:.2%%}")
ECHO is on.
        return 0
ECHO is on.
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
