import pytest

from mosaico.positioning.absolute import AbsolutePosition
from mosaico.positioning.region import RegionPosition
from mosaico.positioning.relative import RelativePosition


@pytest.mark.parametrize(
    "relative_position, frame_size, expected_x, expected_y",
    [
        (RelativePosition(x=0.5, y=0.5), (1920, 1080), 960, 540),
        (RelativePosition(x=0.0, y=0.0), (1920, 1080), 0, 0),
        (RelativePosition(x=1.0, y=1.0), (1920, 1080), 1920, 1080),
        (RelativePosition(x=0.25, y=0.75), (1280, 720), 320, 540),
    ],
)
def test_from_relative(
    relative_position: RelativePosition, frame_size: tuple[int, int], expected_x: int, expected_y: int
) -> None:
    absolute_position = AbsolutePosition.from_relative(relative_position, frame_size)
    assert absolute_position.x == expected_x
    assert absolute_position.y == expected_y


@pytest.mark.parametrize(
    "region_position, frame_size, expected_x, expected_y",
    [
        (RegionPosition(x="left", y="top"), (1920, 1080), 0, 0),
        (RegionPosition(x="center", y="center"), (1920, 1080), 960, 540),
        (RegionPosition(x="right", y="bottom"), (1920, 1080), 1920, 1080),
        (RegionPosition(x="left", y="bottom"), (1280, 720), 0, 720),
        (RegionPosition(x="right", y="top"), (1280, 720), 1280, 0),
    ],
)
def test_from_region(
    region_position: RegionPosition, frame_size: tuple[int, int], expected_x: int, expected_y: int
) -> None:
    absolute_position = AbsolutePosition.from_region(region_position, frame_size)
    assert absolute_position.x == expected_x
    assert absolute_position.y == expected_y
