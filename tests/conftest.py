"""pytest設定とfixture"""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """fixtureチE��レクトリのパス"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_spec_path(fixtures_dir):
    """サンプル仕様ファイルのパス"""
    return fixtures_dir / "sample_spec.yaml"
