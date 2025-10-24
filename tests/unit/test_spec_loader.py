"""test_spec_loader.py"""
import pytest
from pathlib import Path
from nfops_planner.core import SpecLoader


class TestSpecLoader:
    def test_load_valid_spec(self, sample_spec_path):
        loader = SpecLoader()
        spec, invalids = loader.load(sample_spec_path)
        assert spec is not None
        assert len(spec.models) > 0
    def test_missing_models_key(self, tmp_path):
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("common:\n  freq: H", encoding='utf-8')
        loader = SpecLoader()
        with pytest.raises(ValueError, match="E-SPEC-001"):
            loader.load(invalid_file)
