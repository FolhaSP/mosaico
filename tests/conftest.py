from pathlib import Path

import pytest

from mosaico.config import settings


settings.temp_dir = str(Path(__file__).parent / "temp")


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
