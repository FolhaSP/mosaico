from pathlib import Path

import pytest


@pytest.fixture
def samples_dir() -> Path:
    """
    Returns the path to the samples directory.
    """
    return Path(__file__).parent / "samples"
