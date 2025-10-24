@echo off
REM ============================================================
REM Phase 2 データ品質検査システム 全自動構築スクリプト
REM 実行: setup_phase2.bat
REM ============================================================
setlocal enabledelayedexpansion

echo ============================================================
echo Phase 2 データ品質検査システムを構築します
echo ============================================================
echo.

REM ============================================================
REM 1. ディレクトリ構造作成
REM ============================================================
echo [1/20] ディレクトリ構造を作成中...

mkdir nfops_data_quality 2>nul
mkdir nfops_data_quality\core 2>nul
mkdir nfops_data_quality\detectors 2>nul
mkdir nfops_data_quality\utils 2>nul
mkdir tests\phase2 2>nul
mkdir tests\phase2\unit 2>nul
mkdir tests\phase2\integration 2>nul
mkdir tests\phase2\fixtures 2>nul
mkdir configs 2>nul
mkdir profile 2>nul
mkdir snapshots 2>nul
mkdir examples\phase2 2>nul

echo   完了: ディレクトリ構造

REM ============================================================
REM 2. nfops_data_quality/__init__.py
REM ============================================================
echo [2/20] nfops_data_quality/__init__.py を作成中...

(
echo """
echo nfops-data-quality - Data Quality Inspection System
echo """
echo from nfops_data_quality.__version__ import __version__
echo.
echo __all__ = ["__version__"]
) > nfops_data_quality\__init__.py

REM ============================================================
REM 3. nfops_data_quality/__version__.py
REM ============================================================
echo [3/20] nfops_data_quality/__version__.py を作成中...

(
echo """Version information"""
echo __version__ = "0.2.0"
) > nfops_data_quality\__version__.py

REM ============================================================
REM 4. nfops_data_quality/exceptions.py
REM ============================================================
echo [4/20] nfops_data_quality/exceptions.py を作成中...

call :create_dq_exceptions

REM ============================================================
REM 5. nfops_data_quality/models.py
REM ============================================================
echo [5/20] nfops_data_quality/models.py を作成中...

call :create_dq_models

REM ============================================================
REM 6. nfops_data_quality/core/__init__.py
REM ============================================================
echo [6/20] nfops_data_quality/core/__init__.py を作成中...

(
echo """Core data quality modules"""
echo from nfops_data_quality.core.schema_loader import SchemaLoader, SchemaSpec
echo from nfops_data_quality.core.contract_validator import ContractValidator
echo from nfops_data_quality.core.profiler import Profiler
echo.
echo __all__ = ["SchemaLoader", "SchemaSpec", "ContractValidator", "Profiler"]
) > nfops_data_quality\core\__init__.py

REM ============================================================
REM 7. schema_loader.py
REM ============================================================
echo [7/20] schema_loader.py を作成中...

call :create_schema_loader

REM ============================================================
REM 8. contract_validator.py
REM ============================================================
echo [8/20] contract_validator.py を作成中...

call :create_contract_validator

REM ============================================================
REM 9. type_caster.py
REM ============================================================
echo [9/20] type_caster.py を作成中...

call :create_type_caster

REM ============================================================
REM 10. missing_imputer.py
REM ============================================================
echo [10/20] missing_imputer.py を作成中...

call :create_missing_imputer

REM ============================================================
REM 11. outlier_detector.py
REM ============================================================
echo [11/20] outlier_detector.py を作成中...

call :create_outlier_detector

REM ============================================================
REM 12. freq_gap_inspector.py
REM ============================================================
echo [12/20] freq_gap_inspector.py を作成中...

call :create_freq_gap_inspector

REM ============================================================
REM 13. profiler.py
REM ============================================================
echo [13/20] profiler.py を作成中...

call :create_profiler

REM ============================================================
REM 14. dq_runner.py (CLI)
REM ============================================================
echo [14/20] dq_runner.py を作成中...

call :create_dq_runner

REM ============================================================
REM 15. configs/schema.json
REM ============================================================
echo [15/20] configs/schema.json を作成中...

call :create_schema_json

REM ============================================================
REM 16. examples/phase2/sample_data.py
REM ============================================================
echo [16/20] サンプルデータ生成スクリプトを作成中...

call :create_sample_data_generator

REM ============================================================
REM 17. tests/phase2/conftest.py
REM ============================================================
echo [17/20] tests/phase2/conftest.py を作成中...

call :create_phase2_conftest

REM ============================================================
REM 18. tests/phase2/unit/test_contract_validator.py
REM ============================================================
echo [18/20] test_contract_validator.py を作成中...

call :create_test_contract_validator

REM ============================================================
REM 19. pyproject.toml更新
REM ============================================================
echo [19/20] pyproject.toml を更新中...

call :update_pyproject_toml

REM ============================================================
REM 20. README_PHASE2.md
REM ============================================================
echo [20/20] README_PHASE2.md を作成中...

call :create_readme_phase2

echo.
echo ============================================================
echo Phase 2 セットアップ完了！
echo ============================================================
echo.
echo 次のステップ:
echo   1. サンプルデータ生成: python examples\phase2\sample_data.py
echo   2. 品質検査実行: python -m nfops_data_quality.dq_runner --schema configs\schema.json --input examples\phase2\sample_train.parquet --profile
echo   3. テスト実行: pytest tests\phase2 -v
echo.
pause
goto :eof

REM ============================================================
REM サブルーチン: exceptions.py
REM ============================================================
:create_dq_exceptions
(
echo """Data Quality カスタム例外"""
echo.
echo.
echo class DataQualityError^(Exception^):
echo     """Base exception for data quality"""
echo     pass
echo.
echo.
echo class SchemaError^(DataQualityError^):
echo     """E-DQ-xxx: Schema validation errors"""
echo     pass
echo.
echo.
echo class ContractViolation^(DataQualityError^):
echo     """E-DQ-001: Contract violation"""
echo     pass
echo.
echo.
echo class MissingColumnError^(ContractViolation^):
echo     """E-DQ-001: Required column missing"""
echo     pass
echo.
echo.
echo class DuplicateKeyError^(ContractViolation^):
echo     """E-DQ-011: Duplicate key detected"""
echo     pass
echo.
echo.
echo class MonotonicViolation^(ContractViolation^):
echo     """E-DQ-021: ds order violation"""
echo     pass
echo.
echo.
echo class RangeViolation^(DataQualityError^):
echo     """E-DQ-101: Value range violation"""
echo     pass
echo.
echo.
echo class MissingExcessiveError^(DataQualityError^):
echo     """E-DQ-201: Missing rate exceeds threshold"""
echo     pass
echo.
echo.
echo class FutureCoverageError^(DataQualityError^):
echo     """E-DQ-251: Future exog coverage insufficient"""
echo     pass
) > nfops_data_quality\exceptions.py
goto :eof

REM ============================================================
REM サブルーチン: models.py
REM ============================================================
:create_dq_models
(
echo """Data models"""
echo from typing import Dict, List, Any, Optional
echo from dataclasses import dataclass
echo from datetime import datetime
echo.
echo.
echo @dataclass
echo class Violation:
echo     """契約違反レコード"""
echo     unique_id: str
echo     ds: datetime
echo     column: str
echo     rule_id: str
echo     reason: str
echo     value: Any = None
echo.
echo.
echo @dataclass
echo class QualityMetrics:
echo     """品質メトリクス"""
echo     n_rows: int
echo     n_series: int
echo     n_features: int
echo     date_range: List[str]
echo     freq: str
echo     missing_rate: float
echo     outlier_rate: float
echo     ds_gap_count: int
echo     ds_dup_count: int
echo     unknown_cat_rate: float
echo     futr_coverage: float
echo     contract_passed: bool
echo     
echo     def to_dict^(self^) -^> Dict:
echo         return {
echo             "n_rows": self.n_rows,
echo             "n_series": self.n_series,
echo             "n_features": self.n_features,
echo             "date_range": self.date_range,
echo             "freq": self.freq,
echo             "missing_rate": self.missing_rate,
echo             "outlier_rate": self.outlier_rate,
echo             "ds_gap_count": self.ds_gap_count,
echo             "ds_dup_count": self.ds_dup_count,
echo             "unknown_cat_rate": self.unknown_cat_rate,
echo             "futr_coverage": self.futr_coverage,
echo             "contract_passed": self.contract_passed
echo         }
) > nfops_data_quality\models.py
goto :eof

REM ============================================================
REM サブルーチン: schema_loader.py
REM ============================================================
:create_schema_loader
(
echo """schema_loader.py - スキーマ読込・検証"""
echo from typing import Dict, List, Any, Optional
echo from pathlib import Path
echo import json
echo from pydantic import BaseModel, Field, validator
echo from loguru import logger
echo.
echo.
echo class ColumnSpec^(BaseModel^):
echo     """列仕様"""
echo     type: str
echo     nullable: bool = True
echo     tz: Optional[str] = None
echo     freq: Optional[str] = None
echo.
echo.
echo class ExogSpec^(BaseModel^):
echo     """外生変数仕様"""
echo     hist: List[str] = []
echo     futr: List[str] = []
echo     stat: List[str] = []
echo.
echo.
echo class ConstraintsSpec^(BaseModel^):
echo     """制約仕様"""
echo     unique: List[List[str]] = []
echo     monotonic: List[List[str]] = []
echo     ranges: Dict[str, List[Optional[float]]] = {}
echo     allowed_categories: Dict[str, List[str]] = {}
echo     no_negative: List[str] = []
echo     no_zero: List[str] = []
echo.
echo.
echo class SchemaSpec^(BaseModel^):
echo     """スキーマ全体仕様"""
echo     columns: Dict[str, ColumnSpec]
echo     exog: ExogSpec = ExogSpec^(^)
echo     constraints: ConstraintsSpec = ConstraintsSpec^(^)
echo     version: str = "1.0"
echo.
echo.
echo class SchemaLoader:
echo     """スキーマ読込・検証"""
echo     
echo     def load^(self, schema_path: Path^) -^> SchemaSpec:
echo         """スキーマを読み込み"""
echo         logger.info^(f"Loading schema from {schema_path}"^)
echo         
echo         with open^(schema_path, encoding='utf-8'^) as f:
echo             raw = json.load^(f^)
echo         
echo         # 必須キー検証
echo         if 'columns' not in raw:
echo             raise ValueError^("E-DQ-001: Missing 'columns' key"^)
echo         
echo         # 必須列検証
echo         required_cols = {'unique_id', 'ds', 'y'}
echo         if not required_cols.issubset^(raw['columns'].keys^(^)^):
echo             missing = required_cols - set^(raw['columns'].keys^(^)^)
echo             raise ValueError^(f"E-DQ-001: Missing required columns: {missing}"^)
echo         
echo         spec = SchemaSpec^(**raw^)
echo         logger.success^(f"Schema loaded: {len^(spec.columns^)} columns"^)
echo         return spec
) > nfops_data_quality\core\schema_loader.py
goto :eof

REM ============================================================
REM サブルーチン: contract_validator.py
REM ============================================================
:create_contract_validator
(
echo """contract_validator.py - 契約検証"""
echo from typing import List
echo import pandas as pd
echo from loguru import logger
echo from nfops_data_quality.core.schema_loader import SchemaSpec
echo from nfops_data_quality.models import Violation
echo from nfops_data_quality.exceptions import ContractViolation
echo.
echo.
echo class ContractValidator:
echo     """データ契約の検証"""
echo     
echo     def __init__^(self, spec: SchemaSpec^):
echo         self.spec = spec
echo     
echo     def validate^(self, df: pd.DataFrame^) -^> List[Violation]:
echo         """契約を検証"""
echo         logger.info^("Validating data contract..."^)
echo         violations = []
echo         
echo         # 1. 必須列の存在確認
echo         violations.extend^(self._check_required_columns^(df^)^)
echo         
echo         # 2. キー重複チェック
echo         violations.extend^(self._check_duplicates^(df^)^)
echo         
echo         # 3. Monotonic チェック
echo         violations.extend^(self._check_monotonic^(df^)^)
echo         
echo         # 4. NULL チェック
echo         violations.extend^(self._check_nulls^(df^)^)
echo         
echo         logger.info^(f"Found {len^(violations^)} violations"^)
echo         return violations
echo     
echo     def _check_required_columns^(self, df: pd.DataFrame^) -^> List[Violation]:
echo         """必須列の存在確認"""
echo         violations = []
echo         required = {'unique_id', 'ds', 'y'}
echo         missing = required - set^(df.columns^)
echo         
echo         if missing:
echo             raise ContractViolation^(
echo                 f"E-DQ-001: Missing required columns: {missing}"
echo             ^)
echo         
echo         return violations
echo     
echo     def _check_duplicates^(self, df: pd.DataFrame^) -^> List[Violation]:
echo         """キー重複検出"""
echo         violations = []
echo         
echo         for constraint in self.spec.constraints.unique:
echo             dups = df[df.duplicated^(subset=constraint, keep=False^)]
echo             
echo             for _, row in dups.iterrows^(^):
echo                 violations.append^(Violation^(
echo                     unique_id=str^(row.get^('unique_id', 'N/A'^)^),
echo                     ds=row.get^('ds'^),
echo                     column=','.join^(constraint^),
echo                     rule_id="DUPLICATE_KEY",
echo                     reason=f"Duplicate key: {constraint}"
echo                 ^)^)
echo         
echo         return violations
echo     
echo     def _check_monotonic^(self, df: pd.DataFrame^) -^> List[Violation]:
echo         """Monotonic 検証"""
echo         violations = []
echo         
echo         for constraint in self.spec.constraints.monotonic:
echo             if constraint == ['unique_id', 'ds']:
echo                 for uid, group in df.groupby^('unique_id'^):
echo                     if not group['ds'].is_monotonic_increasing:
echo                         # 逆転箇所を特定
echo                         diffs = group['ds'].diff^(^)
echo                         backsteps = group[diffs ^< pd.Timedelta^(0^)]
echo                         
echo                         for _, row in backsteps.iterrows^(^):
echo                             violations.append^(Violation^(
echo                                 unique_id=str^(uid^),
echo                                 ds=row['ds'],
echo                                 column='ds',
echo                                 rule_id="MONOTONIC_VIOLATION",
echo                                 reason="ds is not monotonic increasing"
echo                             ^)^)
echo         
echo         return violations
echo     
echo     def _check_nulls^(self, df: pd.DataFrame^) -^> List[Violation]:
echo         """NULL検証"""
echo         violations = []
echo         
echo         # y列のNULL禁止
echo         if 'y' in df.columns:
echo             null_mask = df['y'].isna^(^)
echo             null_rows = df[null_mask]
echo             
echo             for _, row in null_rows.iterrows^(^):
echo                 violations.append^(Violation^(
echo                     unique_id=str^(row.get^('unique_id', 'N/A'^)^),
echo                     ds=row.get^('ds'^),
echo                     column='y',
echo                     rule_id="NO_NULL_Y",
echo                     reason="y cannot be null"
echo                 ^)^)
echo         
echo         return violations
) > nfops_data_quality\core\contract_validator.py
goto :eof

REM ============================================================
REM サブルーチン: type_caster.py
REM ============================================================
:create_type_caster
(
echo """type_caster.py - 型変換・正規化"""
echo import pandas as pd
echo from loguru import logger
echo from nfops_data_quality.core.schema_loader import SchemaSpec
echo.
echo.
echo class TypeCaster:
echo     """型変換・タイムゾーン・カテゴリ正規化"""
echo     
echo     def __init__^(self, spec: SchemaSpec^):
echo         self.spec = spec
echo     
echo     def cast^(self, df: pd.DataFrame^) -^> pd.DataFrame:
echo         """型変換実行"""
echo         logger.info^("Casting types..."^)
echo         df = df.copy^(^)
echo         
echo         for col_name, col_spec in self.spec.columns.items^(^):
echo             if col_name not in df.columns:
echo                 continue
echo             
echo             if col_spec.type == 'datetime':
echo                 df[col_name] = pd.to_datetime^(df[col_name]^)
echo                 if col_spec.tz:
echo                     df[col_name] = df[col_name].dt.tz_localize^(col_spec.tz, ambiguous='infer'^)
echo             
echo             elif col_spec.type == 'number':
echo                 df[col_name] = pd.to_numeric^(df[col_name], errors='coerce'^)
echo             
echo             elif col_spec.type == 'string':
echo                 df[col_name] = df[col_name].astype^(str^)
echo             
echo             elif col_spec.type == 'category':
echo                 df[col_name] = df[col_name].astype^('category'^)
echo         
echo         logger.success^("Type casting completed"^)
echo         return df
) > nfops_data_quality\core\type_caster.py
goto :eof

REM ============================================================
REM 他のサブルーチンは文字数制限のため次のコメントで続行
REM ============================================================

pause
goto :eof