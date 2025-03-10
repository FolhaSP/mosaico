from pathlib import Path
from typing import Any, ClassVar, Protocol, TypeVar, runtime_checkable

from mosaico.assets.base import BaseAsset
from mosaico.assets.clip import AssetClip
from mosaico.assets.types import Asset, AssetType
from mosaico.effects.types import EffectType
from mosaico.project import Project
from mosaico.rendering.adapters.effect import EffectAdapter
from mosaico.rendering.types import RenderingOptions
from mosaico.track import Track


T_contra = TypeVar("T_contra", bound=BaseAsset, contravariant=True)


@runtime_checkable
class AssetClipRenderer(Protocol[T_contra]):
    """Clip renderer."""

    def render(self, clip: AssetClip, asset: T_contra, options: RenderingOptions) -> Any:
        """Render a clip with its associated asset"""
        ...


@runtime_checkable
class RenderingEngine(Protocol):
    """Rendering engine."""

    clip_renderers: ClassVar[dict[AssetType, type[AssetClipRenderer]]]
    effect_adapters: ClassVar[dict[EffectType, type[EffectAdapter]]]

    def render_clip(self, clip: AssetClip, asset: Asset, options: RenderingOptions) -> Any:
        """Render a clip with its associated asset"""
        renderer = self.clip_renderers.get(asset.type)
        if renderer is None:
            raise ValueError
        rendered = renderer().render(clip, asset, options)
        if clip.effects:
            for effect in clip.effects:
                adapter = self.effect_adapters[effect.type]
                rendered = adapter().apply(rendered, effect)
        return rendered

    def render_track(self, track: Track, asset_map: dict[str, Asset], options: RenderingOptions) -> Any:
        """Render a track with its associated assets"""
        ...

    def render_project(
        self, project: Project, output_path: str | Path, *, overwrite: bool = False, **kwargs: Any
    ) -> Path:
        """Render a whole video project."""
        ...
