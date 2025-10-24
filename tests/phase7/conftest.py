"""conftest.py"""
import pytest
from pathlib import Path

@pytest.fixture
def phase7_fixtures():
    return Path(__file__).parent / "fixtures"
