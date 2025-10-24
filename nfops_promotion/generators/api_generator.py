"""api_generator.py - API生成"""
from pathlib import Path
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from typing import Dict


class APIGenerator:
    """FastAPI code generator"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir))
        )
    
    def generate(
        self,
        model_name: str,
        version: int,
        stage: str,
        run_id: str,
        output_dir: Path,
        quantiles: list = [0.1, 0.5, 0.9]
    ) -> Dict[str, Path]:
        """Generate FastAPI code"""
        logger.info(f"Generating API for {model_name} v{version}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Render main.py
        main_template = self.env.get_template('main.py.j2')
        main_content = main_template.render(
            model_name=model_name,
            version=version,
            stage=stage,
            run_id=run_id,
            api_version="1.0.0",
            quantiles=quantiles
        )
        
        main_path = output_dir / "main.py"
        main_path.write_text(main_content, encoding='utf-8')
        logger.success(f"Generated: {main_path}")
        
        # Render requirements.txt
        req_template = self.env.get_template('requirements.txt.j2')
        req_content = req_template.render()
        
        req_path = output_dir / "requirements.txt"
        req_path.write_text(req_content, encoding='utf-8')
        logger.success(f"Generated: {req_path}")
        
        logger.success("API generation completed")
        
        return {
            "main": main_path,
            "requirements": req_path
        }
