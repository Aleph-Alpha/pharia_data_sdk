import os

import pytest


_INTEGRATION_FILES = frozenset({"test_integration.py", "test_create_stage.py"})


def pytest_collection_modifyitems(config, items):
    """Skip integration tests when API credentials are not available."""
    if os.getenv("PHARIA_DATA_API_BASE_URL") and os.getenv("PHARIA_API_KEY"):
        return
    skip = pytest.mark.skip(reason="PHARIA_DATA_API_BASE_URL and PHARIA_API_KEY not set")
    for item in items:
        if item.path.name in _INTEGRATION_FILES:
            item.add_marker(skip)
