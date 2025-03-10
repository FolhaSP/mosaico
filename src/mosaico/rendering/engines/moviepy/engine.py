import multiprocessing
from pathlib import Path

from moviepy.audio.AudioClip import CompositeAudioClip as MPCompositeAudioClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip as MPCompositeVideoClip

from mosaico.assets.types import Asset
from mosaico.exceptions import AssetNotFoundError, EmptyTrackError
from mosaico.rendering.engines.moviepy.effects.fade import MoviepyCrossFadeEffectAdapter, MoviepyFadeEffectAdapter
from mosaico.rendering.engines.moviepy.effects.pan import MoviepyPanEffectAdapter
from mosaico.rendering.engines.moviepy.effects.zoom import MoviepyZoomEffectAdapter
from mosaico.rendering.engines.moviepy.renderers.audio import MoviepyAudioClipRenderer
from mosaico.rendering.engines.moviepy.renderers.image import MoviepyImageClipRenderer
from mosaico.rendering.engines.moviepy.renderers.subtitle import MoviepySubtitleClipRenderer
from mosaico.rendering.engines.moviepy.renderers.text import MoviepyTextClipRenderer
from mosaico.rendering.engines.protocol import RenderingEngine


_CODEC_FILE_EXTENSION_MAP = {
    "libx264": ".mp4",
    "mpeg4": ".mp4",
    "rawvideo": ".avi",
    "png": ".avi",
    "libvorbis": ".ogv",
    "libvpx": ".webm",
}


class MoviepyRenderingEngine(RenderingEngine):
    """Moviepy-based rendering engine."""

    clip_renderers = {
        "audio": MoviepyAudioClipRenderer,
        "image": MoviepyImageClipRenderer,
        "text": MoviepyTextClipRenderer,
        "subtitle": MoviepySubtitleClipRenderer,
    }

    effect_adapters = {
        "zoom_in": MoviepyZoomEffectAdapter,
        "zoom_out": MoviepyZoomEffectAdapter,
        "fade_in": MoviepyFadeEffectAdapter,
        "fade_out": MoviepyFadeEffectAdapter,
        "cross_fade_in": MoviepyCrossFadeEffectAdapter,
        "cross_fade_out": MoviepyCrossFadeEffectAdapter,
        "pan_up": MoviepyPanEffectAdapter,
        "pan_down": MoviepyPanEffectAdapter,
        "pan_left": MoviepyPanEffectAdapter,
        "pan_right": MoviepyPanEffectAdapter,
        "pan_center": MoviepyPanEffectAdapter,
    }

    def render_track(self, track, asset_map, options):
        """
        Render a track using Moviepy.

        This method takes a track, a mapping of asset IDs to assets, and a video project configuration.
        It returns a Moviepy clip representing the rendered track.

        :param track: The track to render.
        :param asset_map: A mapping of asset IDs to assets.
        :param options: Rendering options.
        :return: A Moviepy clip representing the rendered track.
        """
        if not track.clips:
            raise EmptyTrackError

        audio_clips = []
        video_clips = []

        def _get_asset(asset_id: str) -> Asset:
            if asset_id not in asset_map:
                raise AssetNotFoundError(asset_id)
            return asset_map[asset_id]

        for clip in track.clips:
            asset = _get_asset(clip.asset_reference.id)
            rendered = self.render_clip(clip, asset, options)

            if asset.type == "audio":
                audio_clips.append(rendered)
            else:
                video_clips.append(rendered)

        video = (
            MPCompositeVideoClip(video_clips, size=options.resolution)
            .with_fps(options.fps)
            .with_duration(track.duration)
        )

        if audio_clips:
            audio = MPCompositeAudioClip(audio_clips)
            video = video.with_audio(audio)  # type: ignore

        return video

    def render_project(self, project, output_path, *, overwrite=False, **kwargs):
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
            raise FileExistsError(f"Output file already exists: {output_path}")

        rendering_options = project.config.rendering_options
        rendered_videos = []

        for track in project.timeline.tracks:
            rendered_track_video = self.render_track(track, project.asset_map, rendering_options)
            rendered_videos.append(rendered_track_video)

        video = (
            MPCompositeVideoClip(rendered_videos, size=rendering_options.resolution)
            .with_fps(rendering_options.fps)
            .with_duration(project.duration)
        )

        video.preview()

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
