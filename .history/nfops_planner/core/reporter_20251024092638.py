"""
reporter.py - HTML/MDレポート生成
"""
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template
from loguru import logger


class Reporter:
    """計画レポートの生成"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, results: Dict[str, Any]) -> Path:
        """HTMLレポートを生成"""
        logger.info("Generating planning report...")
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Planning Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f0f0f0; padding: 15px; }
                .metric { display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <h1>Phase 1 Planning Report</h1>
            <div class="summary">
                <div class="metric">
                    <strong>Total Combinations:</strong> {{ total_combos }}
                </div>
                <div class="metric">
                    <strong>Estimated Time:</strong> {{ est_hours }}h
                </div>
                <div class="metric">
                    <strong>Status:</strong> {{ status }}
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(**results)
        
        output_path = self.output_dir / "plan_report.html"
        output_path.write_text(html_content, encoding='utf-8')
        
        logger.success(f"Report generated: {output_path}")
        return output_path