@echo off
REM ============================================================
REM Phase 1 全ファイル自動生成スクリプト
REM 実行: create_all_files.bat
REM ============================================================
setlocal enabledelayedexpansion

echo ============================================================
echo Phase 1 プロジェクトファイルを生成します
echo ============================================================
echo.

REM ============================================================
REM 1. ルートファイル作成
REM ============================================================
echo [1/15] ルートファイルを作成中...

REM .gitignore
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo env/
echo venv/
echo ENV/
echo build/
echo dist/
echo *.egg-info/
echo .pytest_cache/
echo .tox/
echo .coverage
echo htmlcov/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo desktop.ini
echo.
echo # Project specific
echo plan/*.json
echo plan/*.html
echo logs/*.log
echo artifacts/
echo mlruns/
echo.
echo # Secrets
echo .env
echo secrets.yaml
echo *.key
echo *.pem
) > .gitignore

REM pyproject.toml
(
echo [build-system]
echo requires = ["setuptools>=65.0", "wheel"]
echo build-backend = "setuptools.build_meta"
echo.
echo [project]
echo name = "nfops-planner"
echo version = "0.1.0"
echo description = "NeuralForecast HPO Planning System - Phase 1"
echo authors = [
echo     {name = "Project Team", email = "team@example.com"}
echo ]
echo readme = "README.md"
echo requires-python = ">=3.9"
echo license = {text = "MIT"}
echo keywords = ["mlops", "hyperparameter", "planning", "neuralforecast"]
echo dependencies = [
echo     "pydantic>=2.0.0",
echo     "pyyaml>=6.0",
echo     "pandas>=2.0.0",
echo     "numpy>=1.24.0",
echo     "loguru>=0.7.0",
echo     "mlflow>=2.8.0",
echo     "optuna>=3.4.0",
echo     "scikit-learn>=1.3.0",
echo     "jinja2>=3.1.0",
echo     "click>=8.1.0",
echo ]
echo.
echo [project.optional-dependencies]
echo dev = [
echo     "pytest>=7.4.0",
echo     "pytest-cov>=4.1.0",
echo     "pytest-mock>=3.12.0",
echo     "mypy>=1.6.0",
echo     "ruff>=0.1.0",
echo     "black>=23.10.0",
echo ]
echo.
echo [project.scripts]
echo planner = "nfops_planner.cli:main"
echo.
echo [tool.setuptools.packages.find]
echo where = ["."]
echo include = ["nfops_planner*"]
echo.
echo [tool.pytest.ini_options]
echo testpaths = ["tests"]
echo python_files = ["test_*.py"]
echo addopts = "-v --cov=nfops_planner --cov-report=term-missing"
echo.
echo [tool.mypy]
echo python_version = "3.9"
echo warn_return_any = true
echo.
echo [tool.ruff]
echo line-length = 100
echo target-version = "py39"
) > pyproject.toml

REM README.md
(
echo # nfops-planner - Phase 1 Planning System
echo.
echo NeuralForecast HPO基盤の計画フェーズ専用システム
echo.
echo ## セットアップ
echo.
echo ```bash
echo pip install -e .[dev]
echo pytest
echo ```
) > README.md

REM LICENSE
(
echo MIT License
echo.
echo Copyright ^(c^) 2025 Project Team
echo.
echo Permission is hereby granted, free of charge...
) > LICENSE

REM CHANGELOG.md
(
echo # Changelog
echo.
echo ## [0.1.0] - 2025-10-24
echo ### Added
echo - Initial project structure
) > CHANGELOG.md

echo   完了: ルートファイル

REM ============================================================
REM 2. nfops_planner/__init__.py
REM ============================================================
echo [2/15] nfops_planner/__init__.py を作成中...

(
echo """
echo nfops-planner - NeuralForecast HPO Planning System
echo """
echo from nfops_planner.__version__ import __version__
echo.
echo __all__ = ["__version__"]
) > nfops_planner\__init__.py

REM ============================================================
REM 3. nfops_planner/__version__.py
REM ============================================================
echo [3/15] nfops_planner/__version__.py を作成中...

(
echo """Version information"""
echo __version__ = "0.1.0"
) > nfops_planner\__version__.py

REM ============================================================
REM 4. nfops_planner/exceptions.py
REM ============================================================
echo [4/15] nfops_planner/exceptions.py を作成中...

(
echo """
echo カスタム例外定義
echo """
echo.
echo.
echo class NfopsPlannerError^(Exception^):
echo     """Base exception for nfops-planner"""
echo     pass
echo.
echo.
echo class SpecValidationError^(NfopsPlannerError^):
echo     """E-SPEC-xxx: Spec validation errors"""
echo     pass
echo.
echo.
echo class CircularDependencyError^(SpecValidationError^):
echo     """E-SPEC-101: Circular dependency detected"""
echo     pass
echo.
echo.
echo class InvalidTableError^(NfopsPlannerError^):
echo     """E-INV-xxx: Invalid table errors"""
echo     pass
echo.
echo.
echo class CombinationError^(NfopsPlannerError^):
echo     """E-COMB-xxx: Combination counting errors"""
echo     pass
echo.
echo.
echo class ZeroCombinationsError^(CombinationError^):
echo     """E-COMB-301: Total combinations is zero"""
echo     pass
echo.
echo.
echo class EstimationError^(NfopsPlannerError^):
echo     """E-EST-xxx: Estimation errors"""
echo     pass
echo.
echo.
echo class MlflowError^(NfopsPlannerError^):
echo     """E-MLF-xxx: MLflow connection errors"""
echo     pass
) > nfops_planner\exceptions.py

echo   完了: 基本ファイル

REM ============================================================
REM 5. nfops_planner/config.py
REM ============================================================
echo [5/15] nfops_planner/config.py を作成中...

call :create_config

REM ============================================================
REM 6. nfops_planner/cli.py
REM ============================================================
echo [6/15] nfops_planner/cli.py を作成中...

call :create_cli

REM ============================================================
REM 7. nfops_planner/core/__init__.py
REM ============================================================
echo [7/15] nfops_planner/core/__init__.py を作成中...

(
echo """Core modules for planning"""
echo from nfops_planner.core.spec_loader import SpecLoader, Spec, InvalidRule
echo from nfops_planner.core.comb_counter import CombCounter, CountResult
echo.
echo __all__ = [
echo     "SpecLoader",
echo     "Spec",
echo     "InvalidRule",
echo     "CombCounter",
echo     "CountResult",
echo ]
) > nfops_planner\core\__init__.py

REM ============================================================
REM 8. nfops_planner/core/spec_loader.py
REM ============================================================
echo [8/15] nfops_planner/core/spec_loader.py を作成中...

call :create_spec_loader

REM ============================================================
REM 9. nfops_planner/core/comb_counter.py
REM ============================================================
echo [9/15] nfops_planner/core/comb_counter.py を作成中...

call :create_comb_counter

REM ============================================================
REM 10. nfops_planner/utils/logging_config.py
REM ============================================================
echo [10/15] nfops_planner/utils/logging_config.py を作成中...

call :create_logging_config

REM ============================================================
REM 11. tests/conftest.py
REM ============================================================
echo [11/15] tests/conftest.py を作成中...

(
echo """pytest設定とfixture"""
echo import pytest
echo from pathlib import Path
echo.
echo.
echo @pytest.fixture
echo def fixtures_dir^(^):
echo     """fixtureディレクトリのパス"""
echo     return Path^(__file__^).parent / "fixtures"
echo.
echo.
echo @pytest.fixture
echo def sample_spec_path^(fixtures_dir^):
echo     """サンプル仕様ファイルのパス"""
echo     return fixtures_dir / "sample_spec.yaml"
) > tests\conftest.py

REM ============================================================
REM 12. tests/fixtures/sample_spec.yaml
REM ============================================================
echo [12/15] tests/fixtures/sample_spec.yaml を作成中...

(
echo # テスト用サンプル仕様
echo models:
echo   - name: TestModel
echo     active: true
echo     params:
echo       h: [24, 48]
echo       batch_size: [32, 64]
echo     conditions: []
echo.
echo common:
echo   freq: H
) > tests\fixtures\sample_spec.yaml

REM ============================================================
REM 13. examples/matrix_spec.yaml
REM ============================================================
echo [13/15] examples/matrix_spec.yaml を作成中...

(
echo # サンプル仕様ファイル
echo models:
echo   - name: AutoNHITS
echo     active: true
echo     params:
echo       h: [24, 48]
echo       input_size: [24, 48, 72]
echo       batch_size:
echo         type: int
echo         min: 32
echo         max: 256
echo         step: 32
echo       loss: [MQLoss, DistributionLoss]
echo     conditions:
echo       - if:
echo           loss: DistributionLoss
echo         then:
echo           distribution: [Normal, StudentT]
echo.
echo common:
echo   y_type: [raw, diff]
echo   freq: H
) > examples\matrix_spec.yaml

REM ============================================================
REM 14. examples/invalid_values.csv
REM ============================================================
echo [14/15] examples/invalid_values.csv を作成中...

(
echo model,param_a,operator,value,param_b,reason
echo AutoNHITS,batch_size,^>,192,h,メモリ不足の既知事例
echo AutoNHITS,input_size,^>,h,,input_sizeはh以下である必要がある
) > examples\invalid_values.csv

REM ============================================================
REM 15. docker/docker-compose.yml
REM ============================================================
echo [15/15] docker/docker-compose.yml を作成中...

(
echo version: '3.8'
echo.
echo services:
echo   mlflow:
echo     image: ghcr.io/mlflow/mlflow:v2.8.0
echo     ports:
echo       - "5000:5000"
echo     environment:
echo       - BACKEND_STORE_URI=sqlite:///mlflow.db
echo       - DEFAULT_ARTIFACT_ROOT=/mlruns
echo     volumes:
echo       - mlflow-data:/mlruns
echo     command: mlflow server --host 0.0.0.0 --port 5000
echo.
echo   postgres:
echo     image: postgres:15
echo     ports:
echo       - "5432:5432"
echo     environment:
echo       POSTGRES_USER: nfops
echo       POSTGRES_PASSWORD: nfops123
echo       POSTGRES_DB: nfops_planner
echo     volumes:
echo       - postgres-data:/var/lib/postgresql/data
echo.
echo volumes:
echo   mlflow-data:
echo   postgres-data:
) > docker\docker-compose.yml

echo.
echo ============================================================
echo すべてのファイル生成が完了しました！
echo ============================================================
echo.
echo 次のステップ:
echo   1. venv\Scripts\activate.bat
echo   2. pip install -e .[dev]
echo   3. pytest
echo.
pause
goto :eof

REM ============================================================
REM サブルーチン: config.py作成
REM ============================================================
:create_config
(
echo """設定管理"""
echo from pathlib import Path
echo from typing import Optional
echo from pydantic import BaseModel, Field
echo.
echo.
echo class PlannerConfig^(BaseModel^):
echo     """プランナー設定"""
echo     spec_dir: Path = Field^(default=Path^("data/specs"^)^)
echo     output_dir: Path = Field^(default=Path^("plan"^)^)
echo     log_dir: Path = Field^(default=Path^("logs"^)^)
echo     mlflow_tracking_uri: Optional[str] = Field^(default="http://localhost:5000"^)
echo     max_combos: int = Field^(default=500, ge=1^)
echo     time_budget_hours: float = Field^(default=12.0, gt=0^)
echo     gpu_type: str = Field^(default="A100"^)
echo     cost_per_gpu_hour: float = Field^(default=3.5, ge=0^)
) > nfops_planner\config.py
goto :eof

REM ============================================================
REM サブルーチン: cli.py作成
REM ============================================================
:create_cli
(
echo """CLI エントリーポイント"""
echo import click
echo from loguru import logger
echo from pathlib import Path
echo.
echo.
echo @click.command^(^)
echo @click.option^('--dry-run', is_flag=True, help='Dry-run mode'^)
echo @click.option^('--spec', type=click.Path^(exists=True^), required=True^)
echo @click.option^('--invalid', type=click.Path^(exists=True^)^)
echo @click.option^('--time-budget', default='12h'^)
echo @click.option^('--max-combos', default=500, type=int^)
echo @click.option^('--out-dir', default='plan/'^)
echo def main^(dry_run, spec, invalid, time_budget, max_combos, out_dir^):
echo     """nfops-planner CLI"""
echo     logger.info^("Starting planner..."^)
echo     logger.info^(f"Spec: {spec}"^)
echo     logger.info^(f"Max combos: {max_combos}"^)
echo     click.echo^("Planning completed ^(skeleton^)"^)
echo.
echo.
echo if __name__ == '__main__':
echo     main^(^)
) > nfops_planner\cli.py
goto :eof

REM ============================================================
REM サブルーチン: spec_loader.py作成
REM ============================================================
:create_spec_loader
(
echo """spec_loader.py - 仕様読込"""
echo from typing import Dict, List, Any, Optional
echo from pathlib import Path
echo import yaml
echo import pandas as pd
echo from pydantic import BaseModel, Field
echo from loguru import logger
echo.
echo.
echo class Spec^(BaseModel^):
echo     """仕様の内部表現"""
echo     models: List[Dict] = []
echo     common: Dict = {}
echo.
echo.
echo class InvalidRule^(BaseModel^):
echo     """無効値ルール"""
echo     model: str
echo     param_a: str
echo     operator: str
echo     value: Any
echo     reason: str
echo.
echo.
echo class SpecLoader:
echo     """仕様読込"""
echo     def load^(self, spec_path: Path, invalid_path: Optional[Path] = None^):
echo         logger.info^(f"Loading spec from {spec_path}"^)
echo         with open^(spec_path^) as f:
echo             raw = yaml.safe_load^(f^)
echo         spec = Spec^(**raw^)
echo         invalids = []
echo         if invalid_path:
echo             df = pd.read_csv^(invalid_path^)
echo             for _, row in df.iterrows^(^):
echo                 invalids.append^(InvalidRule^(**row.to_dict^(^)^)^)
echo         return spec, invalids
) > nfops_planner\core\spec_loader.py
goto :eof

REM ============================================================
REM サブルーチン: comb_counter.py作成
REM ============================================================
:create_comb_counter
(
echo """comb_counter.py - 組合せ数算出"""
echo from typing import Dict
echo from dataclasses import dataclass
echo from loguru import logger
echo.
echo.
echo @dataclass
echo class CountResult:
echo     """カウント結果"""
echo     total_combos: int
echo     per_model: Dict[str, int]
echo     computation_time_ms: float
echo.
echo.
echo class CombCounter:
echo     """組合せ数カウンター"""
echo     def __init__^(self, max_combos: int = 10000^):
echo         self.max_combos = max_combos
echo     
echo     def count^(self, spec, invalid_rules^):
echo         logger.info^("Counting combinations..."^)
echo         total = 0
echo         per_model = {}
echo         for model in spec.models:
echo             count = 1
echo             for param_name, param_def in model.get^('params', {}^).items^(^):
echo                 if isinstance^(param_def, list^):
echo                     count *= len^(param_def^)
echo             per_model[model['name']] = count
echo             total += count
echo         return CountResult^(total_combos=total, per_model=per_model, computation_time_ms=0.0^)
) > nfops_planner\core\comb_counter.py
goto :eof

REM ============================================================
REM サブルーチン: logging_config.py作成
REM ============================================================
:create_logging_config
(
echo """logging_config.py - ログ設定"""
echo from pathlib import Path
echo from loguru import logger
echo import sys
echo.
echo.
echo def setup_logging^(log_dir: Path = Path^("logs"^), level: str = "INFO"^):
echo     """ログ設定"""
echo     log_dir = Path^(log_dir^)
echo     log_dir.mkdir^(parents=True, exist_ok=True^)
echo     logger.remove^(^)
echo     logger.add^(sys.stdout, level=level^)
echo     logger.add^(log_dir / "planner_{time}.log", rotation="1 day"^)
echo     logger.info^("Logging configured"^)
) > nfops_planner\utils\logging_config.py
goto :eof