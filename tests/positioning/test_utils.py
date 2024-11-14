import pytest

from mosaico.positioning.absolute import AbsolutePosition
from mosaico.positioning.region import RegionPosition
from mosaico.positioning.relative import RelativePosition
from mosaico.positioning.types import Position
from mosaico.positioning.utils import (
    convert_position_to_absolute,
    is_absolute_position,
    is_region_position,
    is_relative_position,
)


def test_convert_absolute_position():
    position = AbsolutePosition(x=100, y=200)
    frame_size = (1920, 1080)
    result = convert_position_to_absolute(position, frame_size)
    assert result == position


def test_convert_relative_position():
    position = RelativePosition(x=0.5, y=0.5)
    frame_size = (1920, 1080)
    expected_position = AbsolutePosition(x=960, y=540)
    result = convert_position_to_absolute(position, frame_size)
    assert result == expected_position


def test_convert_region_position():
    position = RegionPosition(x="left", y="top")
    frame_size = (1920, 1080)
    expected_position = AbsolutePosition(x=0, y=0)
    result = convert_position_to_absolute(position, frame_size)
    assert result == expected_position


def test_convert_invalid_position():
    position = "invalid_position"
    frame_size = (1920, 1080)
    with pytest.raises(AttributeError, match="object has no attribute 'x'"):
        convert_position_to_absolute(position, frame_size)


@pytest.mark.parametrize(
    "position,expected",
    [
        (RegionPosition(x="left", y="top"), True),
        (RelativePosition(x=0.5, y=0.5), False),
        (AbsolutePosition(x=100, y=200), False),
    ],
    ids=["region", "relative", "absolute"],
)
def test_is_region_position(position: Position, expected: bool) -> None:
    result = is_region_position(position)
    assert result == expected


@pytest.mark.parametrize(
    "position,expected",
    [
        (RelativePosition(x=0.5, y=0.5), True),
        (RegionPosition(x="left", y="top"), False),
        (AbsolutePosition(x=100, y=200), False),
    ],
    ids=["region", "relative", "absolute"],
)
def test_is_relative_position(position: Position, expected: bool) -> None:
    result = is_relative_position(position)
    assert result == expected


@pytest.mark.parametrize(
    "position,expected",
    [
        (AbsolutePosition(x=100, y=200), True),
        (RelativePosition(x=0.5, y=0.5), False),
        (RegionPosition(x="left", y="top"), False),
    ],
    ids=["region", "relative", "absolute"],
)
def test_is_absolute_position(position: Position, expected: bool) -> None:
    result = is_absolute_position(position)
    assert result == expected
