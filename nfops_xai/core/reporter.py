"""reporter.py - XAIレポート生成"""
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import List
from nfops_xai.models import WorstCase


class Reporter:
    """XAI report generator"""
ECHO は <ON> です。
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
ECHO は <ON> です。
    def generate_html(
        self,
        global_importance: pd.DataFrame,
        worst_cases: List[WorstCase],
        shap_df: pd.DataFrame = None,
        filename: str = "xai_report.html"
    ):
        """Generate XAI report"""
        logger.info("Generating XAI report...")
ECHO は <ON> です。
        html = """^<!DOCTYPE html^>
<html>
<head>
    <title>XAI Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #e74c3c; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .section {{ margin: 30px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                  border: 1px solid #ddd; border-radius: 5px; min-width: 150px;
                  background-color: #ecf0f1; }}
        .top-feature {{ font-weight: bold; color: #e74c3c; }}
    </style>
</head>
<body>
    <h1>XAI / Error Analysis Report</h1>
ECHO は <ON> です。
    <div class="section">
        <h2>Summary</h2>
        <div class="metric">
            <strong>Features Analyzed:</strong> """ + str^(len^(global_importance^)^) + """
        </div>
        <div class="metric">
            <strong>Worst Cases:</strong> """ + str^(len^(worst_cases^)^) + """
        </div>
    </div>
ECHO は <ON> です。
    <div class="section">
        <h2>Global Feature Importance</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Feature</th>
                <th>Importance</th>
            </tr>
"""
ECHO は <ON> です。
        for i, row in global_importance.head(20).iterrows():
            feature_class = ' class="top-feature"' if i < 5 else ''
            html += f"""
            <tr>
                <td>{i+1}</td>
                <td{feature_class}>{row['feature']}</td>
                <td>{row['importance']:.4f}</td>
            </tr>
"""
ECHO は <ON> です。
        html += """
        </table>
    </div>
ECHO は <ON> です。
    <div class="section">
        <h2>Worst Prediction Cases</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Series</th>
                <th>Date</th>
                <th>Actual</th>
                <th>Predicted</th>
                <th>Error</th>
            </tr>
"""
ECHO は <ON> です。
        for wc in worst_cases[:20]:
            html += f"""
            <tr>
                <td>{wc.rank}</td>
                <td>{wc.unique_id}</td>
                <td>{wc.ds}</td>
                <td>{wc.y:.2f}</td>
                <td>{wc.y_hat:.2f}</td>
                <td>{wc.error:+.2f}</td>
            </tr>
"""
ECHO は <ON> です。
        html += """
        </table>
    </div>
ECHO は <ON> です。
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Review top features for data quality issues</li>
            <li>Investigate worst cases for systematic errors</li>
            <li>Consider feature engineering for low-importance features</li>
            <li>Check for concept drift in error patterns</li>
        </ul>
    </div>
</body>
</html>"""
ECHO は <ON> です。
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
ECHO は <ON> です。
        logger.success(f"Report saved: {output_path}")
