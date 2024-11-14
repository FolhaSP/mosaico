from typing import Annotated, Literal

from pydantic import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import BaseZoomEffect, ZoomInEffect
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


class CustomZoomOutEffect(BaseZoomEffect):
    """Zoom-in effect for video clips."""

    type: Literal["zoom_in"] = "zoom_in"
    """Effect type. Must be "zoom_in"."""

    start_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.0
    """Starting zoom scale (1.0 is original size)."""

    end_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.1
    """Ending zoom scale."""

    @model_validator(mode="after")
    def _validate_zoom_in(self) -> Self:
        if self.start_zoom >= self.end_zoom:
            raise ValueError("For zoom-in, start_zoom must be less than end_zoom")
        return self


# Create assets
images = [
    create_asset("image", path="photo_1.jpg"),
    create_asset("image", path="photo_2.jpg"),
]

image_refs = [
    AssetReference.from_asset(images[0])
    .with_start_time(0)
    .with_end_time(5)
    .with_effects(effects=[ZoomInEffect(), PanLeftEffect()]),
    AssetReference.from_asset(images[1])
    .with_start_time(5)
    .with_end_time(10)
    .with_effects(effects=[CustomZoomOutEffect(), PanRightEffect()]),
]

# Create scene
scene = Scene(asset_references=image_refs)

# Create project
project = VideoProject(config=VideoProjectConfig()).add_assets(images).add_timeline_events(scene)
