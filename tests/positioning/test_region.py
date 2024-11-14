import pytest

from mosaico.positioning.region import RegionPosition


def test_from_string_valid_x_positions() -> None:
    assert RegionPosition.from_string("left") == RegionPosition(x="left", y="center")
    assert RegionPosition.from_string("center") == RegionPosition(x="center", y="center")
    assert RegionPosition.from_string("right") == RegionPosition(x="right", y="center")


def test_from_string_valid_y_positions() -> None:
    assert RegionPosition.from_string("top") == RegionPosition(x="center", y="top")
    assert RegionPosition.from_string("bottom") == RegionPosition(x="center", y="bottom")


def test_from_string_invalid_positions() -> None:
    with pytest.raises(ValueError, match="Invalid region position"):
        RegionPosition.from_string("invalid")
    with pytest.raises(ValueError, match="Invalid region position"):
        RegionPosition.from_string("left-top")
    with pytest.raises(ValueError, match="Invalid region position"):
        RegionPosition.from_string("bottom-right")
