"""conftest.py"""
import pytest
from pathlib import Path

@pytest.fixture
def phase6_fixtures():
    return Path(__file__).parent / "fixtures"
