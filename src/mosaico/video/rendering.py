from __future__ import annotations

import multiprocessing
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from moviepy.audio.AudioClip import AudioClip
from moviepy.video.compositing.concatenate import CompositeAudioClip, CompositeVideoClip
from moviepy.video.VideoClip import VideoClip

from mosaico.assets.audio import AudioAsset
from mosaico.assets.reference import AssetReference
from mosaico.clip_makers.factory import make_clip


if TYPE_CHECKING:
    from mosaico.assets.types import Asset
    from mosaico.types import FrameSize
    from mosaico.video.project import VideoProject
    from mosaico.video.types import TimelineEvent


def render_video(
    project: VideoProject,
    output_dir: str | Path,
    *,
    storage_options: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Path:
    """
    Renders a video based on a project.

    :param project: The project to render.
    :param output_dir: The output directory.
    :param storage_options: Optional storage options to pass to the clip.
    :param overwrite: Whether to overwrite the output file if it already exists.
    :return: The path to the rendered video.
    """
    output_dir = Path(output_dir).resolve()
    output_path = output_dir / f"{project.config.title}.mp4"

    if not output_dir.exists():
        msg = f"Output directory does not exist: {output_dir}"
        raise FileNotFoundError(msg)

    if output_path.exists() and not overwrite:
        msg = f"Output file already exists: {output_path}"
        raise FileExistsError(msg)

    video_clips = []
    audio_clips = []

    for event in project.timeline:
        event_asset_ref_pairs = _get_event_assets_and_refs(event, project)
        event_video_clips, event_audio_clips = _render_event_clips(
            event_asset_ref_pairs, project.config.resolution, storage_options
        )
        video_clips.extend(event_video_clips or [])
        audio_clips.extend(event_audio_clips or [])

    video: VideoClip = (
        CompositeVideoClip(video_clips, size=project.config.resolution)
        .set_fps(project.config.fps)
        .set_duration(project.duration)
    )

    if audio_clips:
        audio = CompositeAudioClip(audio_clips).set_duration(project.duration)
        video = video.set_audio(audio)

    video.write_videofile(
        output_path.as_posix(),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile_path=output_path.parent.as_posix(),
        threads=multiprocessing.cpu_count(),
    )
    video.close()

    return output_path


def _get_event_assets_and_refs(event: TimelineEvent, project: VideoProject) -> list[tuple[Asset, AssetReference]]:
    """
    Get the assets for a timeline event.
    """
    asset_refs = _get_event_asset_refs(event)
    event_asset_ref_pairs = []
    for asset_ref in asset_refs:
        asset = project.get_asset(asset_ref.asset_id)
        if asset_ref.asset_params is not None:
            asset = asset.with_params(asset_ref.asset_params)  # type: ignore
        event_asset_ref_pairs.append((asset, asset_ref))
    return event_asset_ref_pairs


def _get_event_asset_refs(event: TimelineEvent) -> list[AssetReference]:
    """
    Get the asset references for a timeline event.
    """
    if isinstance(event, AssetReference):
        return [event]
    return event.asset_references


def _render_event_clips(
    asset_and_ref_pairs: Sequence[tuple[Asset, AssetReference]],
    video_resolution: FrameSize,
    storage_options: dict[str, Any] | None = None,
) -> tuple[list[VideoClip], list[AudioClip]]:
    """
    Compose a video clip from the given assets.
    """
    audio_clips = []
    video_clips = []

    for asset, asset_ref in asset_and_ref_pairs:
        clip = make_clip(
            asset, asset_ref.duration, video_resolution, asset_ref.effects, storage_options=storage_options
        )
        clip = clip.set_start(asset_ref.start_time)

        if hasattr(asset.params, "z_index"):
            layer = getattr(asset.params, "z_index")
            clip = clip.set_layer(layer)

        if isinstance(asset, AudioAsset):
            audio_clips.append(clip)
        else:
            video_clips.append(clip)

    return video_clips, audio_clips
