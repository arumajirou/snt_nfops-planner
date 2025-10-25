import pytest
def pytest_collection_modifyitems(config, items):
    for it in items:
        nid = it.nodeid
        if any(s in nid for s in ("phase5", "phase6", "phase11")):
            it.add_marker(pytest.mark.slow)
