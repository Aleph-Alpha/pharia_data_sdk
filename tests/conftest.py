import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all integration tests when API credentials are not available."""
    if os.getenv("PHARIA_DATA_API_BASE_URL") and os.getenv("PHARIA_API_KEY"):
        return
    skip = pytest.mark.skip(reason="PHARIA_DATA_API_BASE_URL and PHARIA_API_KEY not set")
    for item in items:
        item.add_marker(skip)
