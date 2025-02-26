from __future__ import annotations

import multiprocessing
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import VideoClip

from mosaico.assets.audio import AudioAsset
from mosaico.assets.reference import AssetReference
from mosaico.clip_makers.factory import make_clip


if TYPE_CHECKING:
    from mosaico.assets.types import Asset
    from mosaico.types import FrameSize
    from mosaico.video.project import VideoProject
    from mosaico.video.types import TimelineEvent

_CODEC_FILE_EXTENSION_MAP = {
    "libx264": ".mp4",
    "mpeg4": ".mp4",
    "rawvideo": ".avi",
    "png": ".avi",
    "libvorbis": ".ogv",
    "libvpx": ".webm",
}


def render_video(
    project: VideoProject,
    output_path: str | Path,
    *,
    overwrite: bool = False,
    **kwargs: Any,
) -> Path:
    """
    Renders a video based on a project.

    :param project: The project to render.
    :param output_path: The output path. If a directory is provided, the output file will be saved in the directory
        with the project title as the filename. Otherwise, be sure that the file extension matches the codec used.
        By default, the output file will be an MP4 file (H.264 codec). The available codecs are:

        - libx264: .mp4
        - mpeg4: .mp4
        - rawvideo: .avi
        - png: .avi
        - libvorbis: .ogv
        - libvpx: .webm

    :param overwrite: Whether to overwrite the output file if it already exists.
    :param kwargs: Additional keyword arguments to pass to Moviepy clip video writer.
    :return: The path to the rendered video.
    """
    output_path = Path(output_path).resolve()
    output_codec = kwargs.get("codec") or _guess_codec_from_file_path(output_path) or "libx264"
    output_file_ext = _CODEC_FILE_EXTENSION_MAP[output_codec]

    if output_path.is_dir():
        output_path /= f"{project.config.title}.{output_file_ext}"

    if output_path.suffix != output_file_ext:
        raise ValueError(f"Output file must be an '{output_file_ext}' file.")

    if not output_path.parent.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path.parent}")

    if output_path.exists() and not overwrite:
        msg = f"Output file already exists: {output_path}"
        raise FileExistsError(msg)

    video_clips = []
    audio_clips = []

    for event in project.timeline:
        event_asset_ref_pairs = _get_event_assets_and_refs(event, project)
        event_video_clips, event_audio_clips = _render_event_clips(event_asset_ref_pairs, project.config.resolution)
        video_clips.extend(event_video_clips or [])
        audio_clips.extend(event_audio_clips or [])

    video: VideoClip = (
        CompositeVideoClip(video_clips, size=project.config.resolution)
        .with_fps(project.config.fps)
        .with_duration(project.duration)
    )

    if audio_clips:
        audio = CompositeAudioClip(audio_clips).with_duration(project.duration)
        video = video.with_audio(audio)

    kwargs["codec"] = output_codec
    kwargs["audio_codec"] = kwargs.get("audio_codec", "aac")
    kwargs["threads"] = kwargs.get("threads", multiprocessing.cpu_count())
    kwargs["temp_audiofile_path"] = kwargs.get("temp_audiofile_path", output_path.parent.as_posix())

    video.write_videofile(output_path.as_posix(), **kwargs)
    video.close()

    return output_path


def _guess_codec_from_file_path(file_path: Path) -> str | None:
    """
    Guess video codec from file path.
    """
    for codec, file_ext in _CODEC_FILE_EXTENSION_MAP.items():
        if file_path.name.endswith(file_ext):
            return codec


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
    asset_and_ref_pairs: Sequence[tuple[Asset, AssetReference]], video_resolution: FrameSize
) -> tuple[list[VideoClip], list[AudioClip]]:
    """
    Compose a video clip from the given assets.
    """
    audio_clips = []
    video_clips = []

    for asset, asset_ref in asset_and_ref_pairs:
        clip = make_clip(asset, asset_ref.duration, video_resolution, asset_ref.effects)
        clip = clip.with_start(asset_ref.start_time)

        if hasattr(asset.params, "z_index"):
            layer = getattr(asset.params, "z_index")
            clip = clip.with_layer_index(layer)

        if isinstance(asset, AudioAsset):
            audio_clips.append(clip)
        else:
            video_clips.append(clip)

    return video_clips, audio_clips
