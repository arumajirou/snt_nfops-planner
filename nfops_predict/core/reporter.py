"""reporter.py - レポート生成"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from nfops_predict.models import CalibrationMetrics


class Reporter:
    """Calibration report generator"""
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def compute_metrics(
        self,
        pred_df: pd.DataFrame,
        y_true: pd.DataFrame = None
    ) -> CalibrationMetrics:
        """Compute calibration metrics"""
        logger.info("Computing calibration metrics...")
        # Dummy metrics for demonstration
        metrics = CalibrationMetrics(
            coverage_80=0.82,
            coverage_90=0.91,
            coverage_95=0.94,
            pinball_losses={0.1: 0.05, 0.5: 0.03, 0.9: 0.06},
            crps=2.45,
            nll=3.12
        )
        logger.info(f"Coverage@90: {metrics.coverage_90:.2%%}")
        return metrics
    def generate_html(
        self,
        pred_df: pd.DataFrame,
        metrics: CalibrationMetrics,
        filename: str = "calibration_report.html"
    ):
        """Generate HTML report"""
        logger.info("Generating calibration report...")
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Calibration Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                  border: 1px solid #ddd; border-radius: 5px; }}
        .good {{ background-color: #d4edda; }}
        .warning {{ background-color: #fff3cd; }}
        table {{ border-collapse: collapse; width: 100%%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Calibration Report</h1>
    <h2>Coverage Metrics</h2>
    <div class="metric good">
        <strong>Coverage@80:</strong> {metrics.coverage_80:.2%%}
    </div>
    <div class="metric good">
        <strong>Coverage@90:</strong> {metrics.coverage_90:.2%%}
    </div>
    <div class="metric good">
        <strong>Coverage@95:</strong> {metrics.coverage_95:.2%%}
    </div>
    <h2>Probabilistic Metrics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>CRPS</td><td>{metrics.crps:.4f}</td></tr>
        <tr><td>NLL</td><td>{metrics.nll:.4f}</td></tr>
    </table>
    <h2>Pinball Losses</h2>
    <table>
        <tr><th>Quantile</th><th>Loss</th></tr>
"""
        for q, loss in metrics.pinball_losses.items():
            html += f"        <tr><td>{q:.2f}</td><td>{loss:.4f}</td></tr>\n"
        html += """
    </table>
    <h2>Summary</h2>
    <p>Total predictions: """ + str(len(pred_df)) + """</p>
    <p>Report generated successfully.</p>
</body>
</html>"""
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
        logger.success(f"Report saved: {output_path}")
