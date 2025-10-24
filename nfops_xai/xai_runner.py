"""xai_runner.py - CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_xai.core.data_aligner import DataAligner
from nfops_xai.analyzers.error_profiler import ErrorProfiler
from nfops_xai.explainers.shap_explainer import ShapExplainer
from nfops_xai.explainers.perm_explainer import PermutationExplainer
from nfops_xai.core.reporter import Reporter
from nfops_xai.utils.logging_config import setup_logging
import time


@click.command()
@click.option('--features', type=click.Path(exists=True), required=True)
@click.option('--preds', type=click.Path(exists=True), required=True)
@click.option('--actuals', type=click.Path(exists=True), required=True)
@click.option('--methods', default='shap,perm')
@click.option('--topk-worst', default=100, type=int)
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='artifacts/xai/')
def main(features, preds, actuals, methods, topk_worst, emit_mlflow, out_dir):
    """XAI Runner - Phase 8"""
    setup_logging()
    logger.info("Starting XAI analysis...")
    start_time = time.time()
    try:
        # 1. Load data
        logger.info(f"Loading features from {features}")
        if features.endswith('.parquet'):
            features_df = pd.read_parquet(features)
        else:
            features_df = pd.read_csv(features, parse_dates=['ds'])
        logger.info(f"Loading predictions from {preds}")
        if preds.endswith('.parquet'):
            preds_df = pd.read_parquet(preds)
        else:
            preds_df = pd.read_csv(preds, parse_dates=['ds'])
        logger.info(f"Loading actuals from {actuals}")
        if actuals.endswith('.parquet'):
            actuals_df = pd.read_parquet(actuals)
        else:
            actuals_df = pd.read_csv(actuals, parse_dates=['ds'])
        # 2. Align data
        aligner = DataAligner()
        aligned = aligner.align(features_df, preds_df, actuals_df)
        # 3. Profile errors
        profiler = ErrorProfiler(topk=topk_worst)
        worst_cases = profiler.profile(aligned)
        # Save worst cases
        output_dir = Path(out_dir)
        profiler.save_worst_cases(
            worst_cases,
            output_dir / "worst_cases.parquet"
        )
        # 4. Identify feature columns
        exclude_cols = {'unique_id', 'ds', 'y', 'y_hat', 'error', 'abs_error', 'q', 'model', 'run_id', 'scenario_id'}
        feature_cols = [
            col for col in aligned.columns 
            if col not in exclude_cols and aligned[col].dtype in ['float64', 'int64']
        ]
        logger.info(f"Analyzing {len(feature_cols)} features")
        # 5. Compute explanations
        method_list = methods.split(',')
        global_importance = None
        shap_df = None
        if 'shap' in method_list:
            shap_explainer = ShapExplainer()
            shap_df = shap_explainer.explain(aligned, feature_cols)
            global_importance = shap_explainer.aggregate_importance(shap_df)
            # Save SHAP values
            shap_df.to_parquet(output_dir / "shap_values.parquet")
            logger.success("Saved SHAP values")
        if 'perm' in method_list:
            perm_explainer = PermutationExplainer()
            perm_df = perm_explainer.explain(aligned, feature_cols)
            # Save permutation importance
            perm_df.to_parquet(output_dir / "permutation_importance.parquet")
            logger.success("Saved permutation importance")
            # Use as global importance if SHAP not computed
            if global_importance is None:
                global_importance = perm_df[['feature', 'importance']].copy()
        # 6. Generate report
        if global_importance is not None:
            reporter = Reporter(output_dir)
            reporter.generate_html(
                global_importance=global_importance,
                worst_cases=worst_cases,
                shap_df=shap_df
            )
        # 7. Summary
        elapsed = time.time() - start_time
        logger.success(f"XAI analysis completed in {elapsed:.1f}s")
        logger.info(f"Features analyzed: {len(feature_cols)}")
        logger.info(f"Worst cases: {len(worst_cases)}")
        if global_importance is not None:
            logger.info(f"Top feature: {global_importance.iloc[0]['feature']}")
        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
