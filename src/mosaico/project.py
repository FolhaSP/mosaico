from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field

from mosaico.assets.audio import AudioAsset
from mosaico.assets.clip import AssetClip
from mosaico.assets.factory import create_asset
from mosaico.assets.subtitle import SubtitleAsset
from mosaico.assets.text import TextAssetParams
from mosaico.assets.types import Asset
from mosaico.assets.utils import convert_media_to_asset
from mosaico.audio_transcribers.protocol import AudioTranscriber
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.effects.factory import create_effect
from mosaico.exceptions import AssetNotFoundError, DuplicatedAssetError, EmptyTimelineError, TrackNotFoundError
from mosaico.media import Media
from mosaico.rendering.types import RenderingOptions
from mosaico.script_generators.protocol import ScriptGenerator
from mosaico.script_generators.script import ShotMediaReference
from mosaico.speech_synthesizers.protocol import SpeechSynthesizer
from mosaico.timeline import Timeline
from mosaico.track import Track
from mosaico.types import FilePath, FrameSize, ReadableBuffer, WritableBuffer


class ProjectConfig(BaseModel):
    """A dictionary representing the configuration of a project."""

    title: str = "Untitled Project"
    """The title of the project. Defaults to "Untitled Project"."""

    version: int = 1
    """The version of the project. Defaults to 1."""

    rendering_options: RenderingOptions = Field(default_factory=RenderingOptions)
    """The rendering options of the project."""

    model_config = ConfigDict(validate_assignment=True, extra="ignore")


class Project(BaseModel):
    """Represents a project with various properties and methods to manipulate its data."""

    config: ProjectConfig = Field(default_factory=ProjectConfig)
    """The configuration of the project."""

    asset_map: dict[str, Asset] = Field(default_factory=dict)
    """A dictionary mapping assets keys to Asset objects."""

    timeline: Timeline = Field(default_factory=Timeline)
    """The timeline of assets and scenes of the video."""

    model_config = ConfigDict(validate_assignment=True)

    @property
    def duration(self) -> float:
        """
        The total duration of the project in seconds.
        """
        return self.timeline.duration

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """
        Create a Project object from a dictionary.

        :param data: The dictionary containing the project data.
        :return: A Project object instance.
        """
        config = data.get("config", ProjectConfig())
        project = cls(config=config)

        if "asset_map" in data:
            project.add_assets(list(data["asset_map"].values()))

        if "timeline" in data and "tracks" in data["timeline"]:
            project.add_tracks(data["timeline"]["tracks"])

        return project

    @classmethod
    def from_file(cls, file: FilePath | ReadableBuffer[str]) -> Project:
        """
        Create a Project object from a YAML file.

        :param file: The path to the YAML file.
        :return: A Project object instance.
        """
        if isinstance(file, (str, Path)):
            project_str = Path(file).read_text(encoding="utf-8")
        else:
            file.seek(0)
            project_str = file.read()

        project_dict = yaml.safe_load(project_str)
        return cls.from_dict(project_dict)

    @classmethod
    def from_script_generator(
        cls,
        script_generator: ScriptGenerator,
        media: Sequence[Media],
        *,
        config: ProjectConfig | None = None,
        **kwargs: Any,
    ) -> Project:
        """
        Create a Project object from a script generator.

        :param generator: The script generator to use.
        :param media: The media files to use.
        :param config: The configuration of the project.
        :param kwargs: Additional keyword arguments to pass to the script generator.
        :return: A Project object instance.
        """
        config = config if config is not None else ProjectConfig()
        project = cls(config=config)

        script = script_generator.generate(media, **kwargs)

        def process_media_reference(media_reference: ShotMediaReference) -> tuple[Asset, AssetClip]:
            referenced_media = next(m for m in media if m.id == media_reference.media_id)
            media_asset = convert_media_to_asset(referenced_media)
            asset_clip = (
                AssetClip.from_asset(media_asset)
                .with_start_time(media_ref.start_time)
                .with_duration(media_ref.duration)
            )
            if media_asset.type == "image" and media_ref.effects:
                asset_clip = asset_clip.with_effects([create_effect(effect) for effect in media_ref.effects])
            return media_asset, asset_clip

        for shot in script.shots:
            subtitle = SubtitleAsset.from_data(shot.subtitle)
            subtitle_clip = AssetClip.from_asset(subtitle).with_start_time(shot.start_time).with_duration(shot.duration)
            track = Track().with_description(shot.description).add_clips(subtitle_clip)
            project = project.add_assets(subtitle)

            for media_ref in shot.media_references:
                media_asset, asset_clip = process_media_reference(media_ref)
                project = project.add_assets(media_asset)
                track = track.add_clips(asset_clip)

            project = project.add_tracks(track)

        return project

    def to_file(self, file: FilePath | WritableBuffer[str]) -> None:
        """
        Write the Project object to a YAML file.

        :param file: The path to the YAML file.
        """
        project = self.model_dump(mode="json", exclude_none=True)
        project_yaml = yaml.safe_dump(project, allow_unicode=True, sort_keys=False)

        if isinstance(file, (str, Path)):
            Path(file).write_text(project_yaml, encoding="utf-8")
        else:
            file.write(project_yaml)

    def add_assets(
        self, assets: Asset | MutableMapping[str, Any] | Sequence[Asset] | Sequence[MutableMapping[str, Any]]
    ) -> Project:
        """
        Add one or more assets to the project.

        :param assets: The asset or list of assets to add.
        :return: The updated project.
        """
        new_assets = assets if isinstance(assets, Sequence) else [assets]

        for new_asset in new_assets:
            asset = create_asset(**new_asset) if isinstance(new_asset, MutableMapping) else new_asset

            if asset.id in self.asset_map:
                raise DuplicatedAssetError(asset.id)

            self.asset_map[asset.id] = asset

        return self

    def add_tracks(
        self, tracks: Track | MutableMapping[str, Any] | Sequence[Track] | Sequence[MutableMapping[str, Any]]
    ) -> Project:
        """
        Add one or more tracks to the timeline.

        :param events: The event or list of events to add.
        :return: The updated project.
        :raises ValueError: If an asset referenced in the events does not exist in the project.
        """

        def validate_asset_id(asset_id: str) -> None:
            if asset_id not in self.asset_map:
                raise AssetNotFoundError(asset_id)

        def validate_track_assets(track: Track) -> None:
            """Helper to validate assets referenced in a scene"""
            for clip in track.clips:
                validate_asset_id(clip.asset_reference.id)

        new_tracks = tracks if isinstance(tracks, Sequence) else [tracks]

        for track in new_tracks:
            if isinstance(track, MutableMapping):
                track = Track.model_validate(track)

            validate_track_assets(track)
            self.timeline = self.timeline.add_tracks(track)

        return self

    # def add_narration(self, text: str, speech_synthesizer: SpeechSynthesizer) -> Project:
    #     narration_asset = speech_synthesizer.synthesize(text)
    #     narration_clip = AssetClip.from_asset(narration_asset, start_time=0)
    #     narration_track = Track(title="Narration", clips=[narration_clip])

    #     for track_index in range(len(self.timeline)):
    #         num_clips = len(self.timeline[track_index].clips)
    #         for clip_index in range(num_clips):
    #             pass

    #     return self.add_assets(narration_asset).add_tracks(narration_track)

    def add_narration(self, speech_synthesizer: SpeechSynthesizer) -> Project:
        """
        Add narration to subtitles inside Scene objects by generating speech audio from subtitle text.

        Updates asset timings within each Scene to match narration duration, dividing time equally
        between multiple images.

        :param speech_synthesizer: The speech synthesizer to use for generating narration audio
        :return: The updated project with narration added
        """
        current_time = None

        for track_index, track in enumerate(self.timeline.tracks):
            # Get subtitle content from scene
            subtitle_clips = track.get_clips_by_type("subtitle")

            if not subtitle_clips:
                continue

            # Get subtitle assets and their text content
            subtitle_assets = [cast(SubtitleAsset, self.get_asset(clip.asset_reference.id)) for clip in subtitle_clips]

            # Generate narration for subtitle content
            texts = [subtitle.to_string() for subtitle in subtitle_assets]
            narration_assets = speech_synthesizer.synthesize(texts)

            # Add narration assets to project
            self.add_assets(narration_assets)

            # Calculate total narration duration for this scene
            total_narration_duration = sum(narration.duration for narration in narration_assets)

            # Get non-subtitle assets to adjust timing
            image_clips = track.get_clips_by_type("image")
            other_clips = track.get_clips_by_type(["subtitle", "image"], negate=True)

            if current_time is None:
                current_time = track.start_time

            new_clips = []

            # Adjust image timings - divide narration duration equally
            if image_clips:
                time_per_image = total_narration_duration / len(image_clips)
                for image_index, image_clip in enumerate(image_clips):
                    new_start = current_time + (image_index * time_per_image)
                    new_end = new_start + time_per_image
                    new_clip = image_clip.model_copy().with_start_time(new_start).with_end_time(new_end)
                    new_clips.append(new_clip)

            # Add other non-image assets with full narration duration
            for image_clip in other_clips:
                new_clip = (
                    image_clip.model_copy()
                    .with_start_time(current_time)
                    .with_end_time(current_time + total_narration_duration)
                )
                new_clips.append(new_clip)

            # Add subtitle references spanning full narration duration
            for image_clip in subtitle_clips:
                new_clip = (
                    image_clip.model_copy()
                    .with_start_time(current_time)
                    .with_end_time(current_time + total_narration_duration)
                )
                new_clips.append(new_clip)

            # Add narration references
            for narration in narration_assets:
                narration_clip = (
                    AssetClip.from_asset(narration)
                    .with_start_time(current_time)
                    .with_end_time(current_time + narration.duration)
                )
                new_clips.append(narration_clip)

            # Update current_time for next scene
            current_time += total_narration_duration

            # Create new scene with updated references
            new_scene = track.model_copy(update={"clips": new_clips})
            self.timeline.tracks[track_index] = new_scene

        return self

    def add_captions(
        self,
        transcription: Transcription,
        *,
        max_duration: int = 5,
        params: TextAssetParams | None = None,
        track_index: int | None = None,
        overwrite: bool = False,
    ) -> Project:
        """
        Add subtitles to the project from a transcription.

        :param transcription: The transcription to add subtitles from.
        :param max_duration: The maximum duration of each subtitle.
        :param params: The parameters for the subtitle assets.
        :param scene_index: The index of the scene to add the subtitles to.
        :param overwrite: Whether to overwrite existing subtitles in the scene.
        :return: The updated project.
        """
        assets = []
        clips = []

        phrases = _group_transcript_into_sentences(transcription, max_duration=max_duration)

        track = self.timeline.tracks[track_index] if track_index is not None else Track()

        if track.has_subtitles and not overwrite:
            msg = f"Track at index {track_index} already has subtitles. Use `overwrite=True` to replace."
            raise ValueError(msg)

        # Remove existing subtitles
        for clip in track.clips:
            if clip.asset_reference.type == "subtitle":
                self.remove_asset(clip.asset_reference.id)

        # Calculate time scale factor if needed
        current_time = track.start_time

        for phrase in phrases:
            subtitle_text = " ".join(word.text for word in phrase)
            subtitle_asset = SubtitleAsset.from_data(subtitle_text)

            # Calculate scaled duration
            phrase_duration = phrase[-1].end_time - phrase[0].start_time

            start_time = current_time
            end_time = start_time + phrase_duration

            subtitle_clip = AssetClip.from_asset(
                asset=subtitle_asset,
                params=params,
                start_time=start_time,
                end_time=end_time,
            )
            assets.append(subtitle_asset)
            clips.append(subtitle_clip)

            current_time = end_time

        self.add_assets(assets)
        track = track.add_clips(clips)

        if track_index is None:
            self.timeline.tracks.append(track)
        else:
            self.timeline.tracks[track_index] = track

        return self

    def add_captions_from_transcriber(
        self,
        audio_transcriber: AudioTranscriber,
        *,
        max_duration: int = 5,
        params: TextAssetParams | None = None,
        overwrite: bool = False,
    ) -> Project:
        """
        Add subtitles to the project from audio assets using an audio transcriber.

        :param audio_transcriber: The audio transcriber to use for transcribing audio assets.
        :param max_duration: The maximum duration of each subtitle.
        :param params: The parameters for the subtitle assets.
        :param overwrite: Whether to overwrite existing subtitles in the scene.
        :return: The updated project.
        """
        for track_index, track in enumerate(self.timeline.tracks):
            if not track.has_audio:
                continue

            for clip in track.clips:
                if clip.asset_reference.type != "audio":
                    continue

                audio_asset = self.get_asset(clip.asset_reference.id)
                audio_asset = cast(AudioAsset, audio_asset)
                audio_transcription = audio_transcriber.transcribe(audio_asset)

                self.add_captions(
                    audio_transcription,
                    max_duration=max_duration,
                    params=params,
                    track_index=track_index,
                    overwrite=overwrite,
                )

        return self

    def with_config(self, config: ProjectConfig | Mapping[str, Any]) -> Project:
        """
        Override the video project configuration.

        :param config: The configuration to set.
        :return: The updated project.
        """
        if isinstance(config, Mapping):
            config = ProjectConfig.model_validate(config)
        self.config = config
        return self

    def with_subtitle_params(self, params: TextAssetParams | MutableMapping[str, Any]) -> Project:
        """
        Override the subtitle parameters for the assets in the project.

        :param params: The subtitle parameters to set.
        :return: The updated project.
        """
        if not self.timeline.tracks:
            raise EmptyTimelineError

        params = TextAssetParams.model_validate(params)

        for track_index in range(len(self.timeline.tracks)):
            self.timeline.tracks[track_index].with_subtitle_params(params)

        return self

    def with_title(self, title: str) -> Project:
        """
        Override the title of the project.

        :param title: The title to set.
        :return: The updated project.
        """
        self.config.title = title
        return self

    def with_version(self, version: int) -> Project:
        """
        Override the project version.

        :param version: The version to set.
        :return: The updated project.
        """
        self.config.version = version
        return self

    def with_fps(self, fps: int) -> Project:
        """
        Override the FPS of the project.

        :param fps: The FPS to set.
        :return: The updated project.
        """
        self.config.rendering_options.fps = fps
        return self

    def with_resolution(self, resolution: FrameSize) -> Project:
        """
        Override the resolution of the project.

        :param resolution: The resolution to set.
        :return: The updated project.
        """
        self.config.rendering_options.resolution = resolution
        return self

    def get_asset(self, asset_id: str) -> Asset:
        """
        Get an asset by its ID.

        :param asset_id: The ID of the asset.
        :return: The Asset object.
        :raises ValueError: If the asset is not found in the project assets.
        """
        try:
            return self.asset_map[asset_id]
        except KeyError:
            raise AssetNotFoundError(asset_id) from None

    def remove_asset(self, asset_id: str) -> Project:
        """
        Remove an asset from the project.

        :param asset_id: The ID of the asset to remove.
        :return: The updated project.
        """
        try:
            for track_index, track in enumerate(self.timeline.tracks):
                self.timeline.tracks[track_index] = track.remove_clips_by_asset_id(asset_id)
            del self.asset_map[asset_id]
            return self
        except KeyError:
            raise AssetNotFoundError(asset_id) from None

    def get_track(self, index: int) -> Track:
        """
        Get a timeline event by its index.

        :param index: The index of the timeline event.
        :return: The TimelineEvent object.
        :raises ValueError: If the index is out of range.
        """
        if abs(index) >= len(self.timeline.tracks):
            raise TrackNotFoundError
        return self.timeline.tracks[index]

    def remove_track(self, index: int) -> Project:
        """
        Remove a timeline event from the project.

        :param index: The index of the timeline event to remove.
        :return: The updated project.
        """
        if abs(index) >= len(self.timeline.tracks):
            raise TrackNotFoundError
        del self.timeline.tracks[index]
        return self


def _group_transcript_into_sentences(
    transcription: Transcription, max_duration: float = 5.0
) -> list[list[TranscriptionWord]]:
    """
    Group words into phrases based on the duration of the words.
    """
    phrases: list[list[TranscriptionWord]] = []
    current_phrase: list[TranscriptionWord] = []
    current_duration = 0.0
    number_pattern = re.compile(r"\d+([.,]\d+)*")

    def is_part_of_number(word: str) -> bool:
        return bool(number_pattern.match(word)) or word in {",", "."}

    i = 0

    while i < len(transcription.words):
        word = transcription.words[i]
        word_duration = word.end_time - word.start_time

        # Check if this word is part of a number
        if is_part_of_number(word.text):
            number_phrase = [word]
            number_duration = word_duration
            j = i + 1
            while j < len(transcription.words) and is_part_of_number(transcription.words[j].text):
                number_phrase.append(transcription.words[j])
                number_duration += transcription.words[j].end_time - transcription.words[j].start_time
                j += 1

            # If adding the entire number would exceed max_duration, start a new phrase
            if current_duration + number_duration > max_duration and current_phrase:
                phrases.append(current_phrase)
                current_phrase = []
                current_duration = 0

            current_phrase.extend(number_phrase)
            current_duration += number_duration
            i = j
        else:
            # Regular word processing
            if current_duration + word_duration > max_duration and current_phrase:
                phrases.append(current_phrase)
                current_phrase = []
                current_duration = 0

            current_phrase.append(word)
            current_duration += word_duration
            i += 1

        # If we've reached max_duration or end of transcription, start a new phrase
        if current_duration >= max_duration or i == len(transcription.words) and current_phrase:
            phrases.append(current_phrase)
            current_phrase = []
            current_duration = 0

    if current_phrase:
        phrases.append(current_phrase)

    return phrases
