"""monitor_runner.py - 監視実行CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_monitor.core.window_builder import WindowBuilder
from nfops_monitor.detectors.drift_detector import DriftDetector
from nfops_monitor.detectors.residual_monitor import ResidualMonitor
from nfops_monitor.detectors.calibration_monitor import CalibrationMonitor
from nfops_monitor.reporters.html_reporter import HTMLReporter
from nfops_monitor.reporters.alert_generator import AlertGenerator
import time


@click.command()
@click.option('--reference', type=click.Path(exists=True), help='Reference data (parquet)')
@click.option('--current', type=click.Path(exists=True), help='Current data (parquet)')
@click.option('--features', default='', help='Features to monitor (comma-separated)')
@click.option('--reference-days', default=90, type=int, help='Reference window days')
@click.option('--current-days', default=7, type=int, help='Current window days')
@click.option('--psi-warning', default=0.1, type=float, help='PSI warning threshold')
@click.option('--psi-critical', default=0.25, type=float, help='PSI critical threshold')
@click.option('--smape-increase-critical', default=20.0, type=float, help='SMAPE increase critical (%)')
@click.option('--coverage-gap-critical', default=5.0, type=float, help='Coverage gap critical (pt)')
@click.option('--out-dir', default='monitor/', help='Output directory')
def main(
    reference,
    current,
    features,
    reference_days,
    current_days,
    psi_warning,
    psi_critical,
    smape_increase_critical,
    coverage_gap_critical,
    out_dir
):
    """Monitor Runner - Phase 11"""
    logger.info("Starting drift and accuracy monitoring...")
    
    start_time = time.time()
    
    try:
        # Parse features
        if features:
            feature_list = [f.strip() for f in features.split(',')]
        else:
            feature_list = []
        
        # Load data
        if reference and current:
            logger.info(f"Loading reference from {reference}")
            reference_df = pd.read_parquet(reference)
            
            logger.info(f"Loading current from {current}")
            current_df = pd.read_parquet(current)
        else:
            # Use single file with windowing
            logger.info("Using window builder (single file mode)")
            data_path = reference or current
            df = pd.read_parquet(data_path)
            
            window_builder = WindowBuilder(
                reference_days=reference_days,
                current_days=current_days
            )
            reference_df, current_df = window_builder.build(df)
        
        logger.info(f"Reference: {len(reference_df)} rows")
        logger.info(f"Current: {len(current_df)} rows")
        
        # Auto-detect features if not specified
        if not feature_list:
            # Use numeric columns except target and identifiers
            exclude_cols = {'unique_id', 'ds', 'y', 'y_hat', 'q', 
                           'model_version', 'scenario_id', 'run_id'}
            feature_list = [
                col for col in reference_df.columns
                if col not in exclude_cols and 
                   reference_df[col].dtype in ['float64', 'int64']
            ]
            logger.info(f"Auto-detected {len(feature_list)} features")
        
        # 1. Drift Detection
        drift_detector = DriftDetector(
            psi_warning=psi_warning,
            psi_critical=psi_critical
        )
        drift_results = drift_detector.detect(
            reference_df,
            current_df,
            feature_list
        )
        
        # 2. Accuracy Monitoring
        residual_monitor = ResidualMonitor(
            increase_pct_critical=smape_increase_critical
        )
        
        # Check if y and y_hat columns exist
        if 'y' in current_df.columns and 'y_hat' in current_df.columns:
            accuracy_metrics = residual_monitor.monitor(
                reference_df,
                current_df
            )
        else:
            logger.warning("y or y_hat column not found, skipping accuracy monitoring")
            from nfops_monitor.models import AccuracyMetrics
            accuracy_metrics = AccuracyMetrics(
                window="7d",
                smape=0.0,
                mae=0.0,
                delta_pct=0.0,
                alert_level="ok"
            )
        
        # 3. Coverage Monitoring
        calibration_monitor = CalibrationMonitor(
            gap_critical=coverage_gap_critical
        )
        
        # Check if quantile columns exist
        q_cols = ['y_hat_q0.1', 'y_hat_q0.9']
        if 'y' in current_df.columns and all(c in current_df.columns for c in q_cols):
            coverage_metrics = calibration_monitor.monitor(current_df)
        else:
            logger.warning("Quantile columns not found, skipping coverage monitoring")
            from nfops_monitor.models import CoverageMetrics
            coverage_metrics = CoverageMetrics(
                alpha=0.1,
                coverage=0.0,
                nominal=0.9,
                gap=0.0,
                alert_level="ok"
            )
        
        # 4. Generate Report
        output_dir = Path(out_dir)
        html_reporter = HTMLReporter(output_dir)
        html_reporter.generate(
            drift_results,
            accuracy_metrics,
            coverage_metrics
        )
        
        # 5. Generate Alert
        alert_dir = Path('alerts')
        alert_generator = AlertGenerator(alert_dir)
        alert_generator.generate(
            drift_results,
            accuracy_metrics,
            coverage_metrics
        )
        
        # Summary
        elapsed = time.time() - start_time
        logger.success(f"Monitoring completed in {elapsed:.1f}s")
        
        critical_count = sum(1 for r in drift_results if r.alert_level == "critical")
        warning_count = sum(1 for r in drift_results if r.alert_level == "warning")
        
        logger.info(f"Drift: {critical_count} critical, {warning_count} warning")
        logger.info(f"Accuracy: {accuracy_metrics.alert_level}")
        logger.info(f"Coverage: {coverage_metrics.alert_level}")
        
        return 0
    
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
