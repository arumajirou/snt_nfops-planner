"""html_reporter.py - HTMLレポート生成"""
from pathlib import Path
from loguru import logger
from typing import List
from nfops_monitor.models import DriftResult, AccuracyMetrics, CoverageMetrics


class HTMLReporter:
    """HTML report generator"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        drift_results: List[DriftResult],
        accuracy_metrics: AccuracyMetrics,
        coverage_metrics: CoverageMetrics,
        filename: str = "drift_report.html"
    ):
        """Generate drift report"""
        logger.info("Generating HTML report")
        
        # Count alerts
        critical_count = sum(1 for r in drift_results if r.alert_level == "critical")
        warning_count = sum(1 for r in drift_results if r.alert_level == "warning")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Drift & Accuracy Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .summary-card {{ display: inline-block; margin: 10px; padding: 20px; border-radius: 8px; min-width: 200px; text-align: center; }}
        .card-ok {{ background: #d4edda; border: 2px solid #28a745; }}
        .card-warning {{ background: #fff3cd; border: 2px solid #ffc107; }}
        .card-critical {{ background: #f8d7da; border: 2px solid #dc3545; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .alert-ok {{ color: #28a745; font-weight: bold; }}
        .alert-warning {{ color: #ffc107; font-weight: bold; }}
        .alert-critical {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Drift & Accuracy Monitoring Report</h1>
        
        <h2>Summary</h2>
        <div class="summary-card card-{'critical' if critical_count > 0 else 'warning' if warning_count > 0 else 'ok'}">
            <div class="metric-label">Critical Alerts</div>
            <div class="metric-value">{critical_count}</div>
        </div>
        <div class="summary-card card-{'warning' if warning_count > 0 else 'ok'}">
            <div class="metric-label">Warning Alerts</div>
            <div class="metric-value">{warning_count}</div>
        </div>
        <div class="summary-card card-{accuracy_metrics.alert_level if accuracy_metrics.alert_level != 'ok' else 'ok'}">
            <div class="metric-label">Accuracy Status</div>
            <div class="metric-value">{accuracy_metrics.alert_level.upper()}</div>
        </div>
        <div class="summary-card card-{coverage_metrics.alert_level if coverage_metrics.alert_level != 'ok' else 'ok'}">
            <div class="metric-label">Coverage Status</div>
            <div class="metric-value">{coverage_metrics.alert_level.upper()}</div>
        </div>
        
        <h2>Data Drift Detection</h2>
        <table>
            <tr>
                <th>Feature</th>
                <th>PSI</th>
                <th>KS Statistic</th>
                <th>KS P-value</th>
                <th>Alert Level</th>
            </tr>"""
        
        for result in drift_results:
            alert_class = f"alert-{result.alert_level}"
            ks_stat = f"{result.ks_statistic:.4f}" if result.ks_statistic else "N/A"
            ks_pval = f"{result.ks_pvalue:.4f}" if result.ks_pvalue else "N/A"
            
            html += f"""
            <tr>
                <td>{result.feature}</td>
                <td>{result.psi:.4f}</td>
                <td>{ks_stat}</td>
                <td>{ks_pval}</td>
                <td class="{alert_class}">{result.alert_level.upper()}</td>
            </tr>"""
        
        html += f"""
        </table>
        
        <h2>Accuracy Metrics</h2>
        <table>
            <tr>
                <th>Window</th>
                <th>SMAPE</th>
                <th>MAE</th>
                <th>Delta (%)</th>
                <th>Alert Level</th>
            </tr>
            <tr>
                <td>{accuracy_metrics.window}</td>
                <td>{accuracy_metrics.smape:.2f}</td>
                <td>{accuracy_metrics.mae:.2f}</td>
                <td>{accuracy_metrics.delta_pct:+.1f}%</td>
                <td class="alert-{accuracy_metrics.alert_level}">{accuracy_metrics.alert_level.upper()}</td>
            </tr>
        </table>
        
        <h2>Coverage Metrics</h2>
        <table>
            <tr>
                <th>Alpha</th>
                <th>Empirical Coverage</th>
                <th>Nominal Coverage</th>
                <th>Gap (pt)</th>
                <th>Alert Level</th>
            </tr>
            <tr>
                <td>{coverage_metrics.alpha}</td>
                <td>{coverage_metrics.coverage:.3f}</td>
                <td>{coverage_metrics.nominal:.3f}</td>
                <td>{coverage_metrics.gap:.1f}</td>
                <td class="alert-{coverage_metrics.alert_level}">{coverage_metrics.alert_level.upper()}</td>
            </tr>
        </table>
        
        <h2>Recommendations</h2>
        <ul>"""
        
        # Add recommendations based on alerts
        if critical_count > 0:
            html += "<li><strong>Critical drift detected:</strong> Review Phase 4 features and consider retraining</li>"
        if accuracy_metrics.alert_level == "critical":
            html += f"<li><strong>Accuracy degradation:</strong> SMAPE increased by {accuracy_metrics.delta_pct:.1f}% - consider Phase 5 HPO</li>"
        if coverage_metrics.alert_level == "critical":
            html += f"<li><strong>Coverage gap:</strong> {coverage_metrics.gap:.1f}pt deviation - review Phase 6 calibration</li>"
        if critical_count == 0 and accuracy_metrics.alert_level == "ok" and coverage_metrics.alert_level == "ok":
            html += "<li>All metrics within acceptable ranges - continue monitoring</li>"
        
        html += """
        </ul>
        
        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
            Generated by nfops-monitor Phase 11
        </footer>
    </div>
</body>
</html>"""
        
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
        
        logger.success(f"Report saved: {output_path}")
