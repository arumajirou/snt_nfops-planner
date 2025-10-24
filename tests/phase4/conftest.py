"""conftest.py"""
import pytest
from pathlib import Path

@pytest.fixture
def phase4_fixtures():
    return Path(__file__).parent / "fixtures"
