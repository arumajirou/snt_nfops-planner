"""pytest險ュ螳壹→fixture"""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """fixture繝・ぅ繝ャ繧ッ繝医Μ縺ョ繝代せ"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_spec_path(fixtures_dir):
    """繧オ繝ウ繝励Ν莉墓ァ倥ヵ繧。繧、繝ォ縺ョ繝代せ"""
    return fixtures_dir / "sample_spec.yaml"
