"""reporter.py - 評価レポート生成"""
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import List
from nfops_eval.models import ComparisonResult, EvalMetrics


class Reporter:
    """Evaluation report generator"""
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def generate_html(
        self,
        comparisons: List[ComparisonResult],
        filename: str = "eval_report.html"
    ):
        """Generate HTML evaluation report"""
        logger.info("Generating evaluation report...")
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                  border: 1px solid #ddd; border-radius: 5px; min-width: 150px; }}
        .winner {{ background-color: #d4edda; }}
        .significant {{ font-weight: bold; color: #e74c3c; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Model Evaluation Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Number of comparisons:</strong> """ + str(len(comparisons)) + """</p>
        <p>Report generated successfully.</p>
    </div>
    <h2>Model Comparisons</h2>
"""
        for comp in comparisons:
            html += f"""
    <h3>{comp.model_a} vs {comp.model_b}</h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>{comp.model_a}</th>
            <th>{comp.model_b}</th>
        </tr>
        <tr>
            <td>SMAPE</td>
            <td>{comp.metrics_a.smape:.2f}</td>
            <td>{comp.metrics_b.smape:.2f}</td>
        </tr>
        <tr>
            <td>MAE</td>
            <td>{comp.metrics_a.mae:.2f}</td>
            <td>{comp.metrics_b.mae:.2f}</td>
        </tr>
        <tr>
            <td>RMSE</td>
            <td>{comp.metrics_a.rmse:.2f}</td>
            <td>{comp.metrics_b.rmse:.2f}</td>
        </tr>
    </table>
    <h4>Statistical Tests</h4>
    <table>
        <tr>
            <th>Test</th>
            <th>Statistic</th>
            <th>P-value</th>
            <th>Significant</th>
        </tr>
"""
            for test in comp.tests:
                sig_class = ' class="significant"' if test.significant else ''
                html += f"""
        <tr>
            <td>{test.test_name}</td>
            <td>{test.statistic:.4f}</td>
            <td{sig_class}>{test.pvalue:.4f}</td>
            <td>{'Yes' if test.significant else 'No'}</td>
        </tr>
"""
            html += """
    </table>
"""
        html += """
</body>
</html>"""
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
        logger.success(f"Report saved: {output_path}")
    def save_comparison_table(
        self,
        comparisons: List[ComparisonResult],
        filename: str = "compare_table.parquet"
    ):
        """Save comparison table"""
        records = []
        for comp in comparisons:
            records.append({
                'model_a': comp.model_a,
                'model_b': comp.model_b,
                'smape_a': comp.metrics_a.smape,
                'smape_b': comp.metrics_b.smape,
                'mae_a': comp.metrics_a.mae,
                'mae_b': comp.metrics_b.mae,
                'rmse_a': comp.metrics_a.rmse,
                'rmse_b': comp.metrics_b.rmse,
                'rank': comp.rank
            })
        df = pd.DataFrame(records)
        output_path = self.output_dir / filename
        df.to_parquet(output_path)
        logger.success(f"Comparison table saved: {output_path}")
