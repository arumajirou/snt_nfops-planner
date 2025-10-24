"""eval_runner.py - CLI"""
import click
import pandas as pd
import json
from pathlib import Path
from loguru import logger
from nfops_eval.core.data_aligner import DataAligner
from nfops_eval.metrics.metric_computer import MetricComputer
from nfops_eval.testers.dm_tester import DMTester
from nfops_eval.testers.coverage_tester import CoverageTester
from nfops_eval.testers.effect_size import EffectSizeEstimator
from nfops_eval.testers.multicomp import MultiCompCorrector
from nfops_eval.core.reporter import Reporter
from nfops_eval.models import ComparisonResult
from nfops_eval.utils.logging_config import setup_logging
import time


@click.command()
@click.option('--preds', type=click.Path(exists=True), required=True)
@click.option('--actuals', type=click.Path(exists=True), required=True)
@click.option('--baseline-run', default='baseline')
@click.option('--candidates', default=None)
@click.option('--metrics', default='SMAPE,MAE,RMSE')
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='eval/')
def main(preds, actuals, baseline_run, candidates, metrics, emit_mlflow, out_dir):
    """Evaluation Runner - Phase 7"""
    setup_logging()
    logger.info("Starting evaluation...")
    start_time = time.time()
    try:
        # 1. Load data
        logger.info(f"Loading predictions from {preds}")
        if preds.endswith('.parquet'):
            pred_df = pd.read_parquet(preds)
        else:
            pred_df = pd.read_csv(preds, parse_dates=['ds'])
        logger.info(f"Loading actuals from {actuals}")
        if actuals.endswith('.parquet'):
            act_df = pd.read_parquet(actuals)
        else:
            act_df = pd.read_csv(actuals, parse_dates=['ds'])
        logger.info(f"Loaded {len(pred_df)} predictions, {len(act_df)} actuals")
        # 2. Align data
        aligner = DataAligner()
        aligned = aligner.align(pred_df, act_df)
        # 3. Compute metrics
        metric_computer = MetricComputer()
        metrics_overall = metric_computer.compute(aligned)
        logger.info("Overall metrics:")
        logger.info(f"  SMAPE: {metrics_overall.smape:.2f}")
        logger.info(f"  MAE: {metrics_overall.mae:.2f}")
        logger.info(f"  RMSE: {metrics_overall.rmse:.2f}")
        # 4. Statistical tests (if we have baseline)
        test_results = []
        # DM test (simplified - comparing with zero)
        dm_tester = DMTester()
        errors = aligned['error'].values
        zeros = np.zeros_like(errors)
        dm_result = dm_tester.test(errors, zeros)
        test_results.append(dm_result)
        # Effect size
        effect_estimator = EffectSizeEstimator()
        # Dummy comparison for demo
        cliffs_d = 0.0  # Would compare two models
        # 5. Create comparison result
        comparison = ComparisonResult(
            model_a=baseline_run,
            model_b="perfect",
            metrics_a=metrics_overall,
            metrics_b=metrics_overall,  # Dummy
            tests=test_results,
            rank=1
        )
        # 6. Generate report
        output_dir = Path(out_dir)
        reporter = Reporter(output_dir)
        reporter.generate_html([comparison])
        reporter.save_comparison_table([comparison])
        # 7. Save test results
        tests_json = {
            "meta": {
                "baseline": baseline_run,
                "n_predictions": len(aligned)
            },
            "tests": [t.to_dict() for t in test_results]
        }
        tests_path = output_dir / "tests.json"
        with open(tests_path, 'w', encoding='utf-8') as f:
            json.dump(tests_json, f, indent=2)
        logger.success(f"Saved tests: {tests_path}")
        # 8. Summary
        elapsed = time.time() - start_time
        logger.success(f"Evaluation completed in {elapsed:.1f}s")
        logger.info(f"Overall SMAPE: {metrics_overall.smape:.2f}")
        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
