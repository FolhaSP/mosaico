from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.types import PositiveInt

from mosaico.assets.audio import AudioAsset
from mosaico.assets.factory import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.assets.subtitle import SubtitleAsset
from mosaico.assets.text import TextAssetParams
from mosaico.assets.types import Asset
from mosaico.assets.utils import convert_media_to_asset
from mosaico.audio_transcribers.protocol import AudioTranscriber
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.effects.factory import create_effect
from mosaico.media import Media
from mosaico.scene import Scene
from mosaico.script_generators.protocol import ScriptGenerator
from mosaico.script_generators.script import Shot
from mosaico.speech_synthesizers.protocol import SpeechSynthesizer
from mosaico.types import FilePath, FrameSize, ReadableBuffer, WritableBuffer
from mosaico.video.timeline import EventOrEventSequence, Timeline
from mosaico.video.types import AssetInputType, TimelineEvent


class VideoProjectConfig(BaseModel):
    """A dictionary representing the configuration of a project."""

    title: str = "Untitled Project"
    """The title of the project. Defaults to "Untitled Project"."""

    version: int = 1
    """The version of the project. Defaults to 1."""

    resolution: FrameSize = (1920, 1080)
    """The resolution of the project in pixels. Defaults to 1920x1080."""

    fps: PositiveInt = 30
    """The frames per second of the project. Defaults to 30."""

    model_config = ConfigDict(validate_assignment=True, extra="ignore")


class VideoProject(BaseModel):
    """Represents a project with various properties and methods to manipulate its data."""

    config: VideoProjectConfig = Field(default_factory=VideoProjectConfig)
    """The configuration of the project."""

    assets: dict[str, Asset] = Field(default_factory=dict)
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
    def from_dict(cls, data: dict[str, Any]) -> VideoProject:
        """
        Create a Project object from a dictionary.

        :param data: The dictionary containing the project data.
        :return: A Project object instance.
        """
        config = data.get("config", VideoProjectConfig())
        project = cls(config=config)

        if "assets" in data:
            project.add_assets(data["assets"])

        if "timeline" in data:
            project.add_timeline_events(data["timeline"])

        return project

    @classmethod
    def from_file(cls, file: FilePath | ReadableBuffer[str]) -> VideoProject:
        """
        Create a Project object from a YAML file.

        :param file: The path to the YAML file.
        :return: A Project object instance.
        """
        if isinstance(file, (str, Path)):
            project_str = Path(file).read_text()
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
        config: VideoProjectConfig | None = None,
        **kwargs: Any,
    ) -> VideoProject:
        """
        Create a Project object from a script generator.

        :param generator: The script generator to use.
        :param media: The media files to use.
        :param config: The configuration of the project.
        :param kwargs: Additional keyword arguments to pass to the script generator.
        :return: A Project object instance.
        """
        config = config if config is not None else VideoProjectConfig()
        project = cls(config=config)

        # Generate assets and scenes from a scene generator.
        script = script_generator.generate(media, **kwargs)

        # Create assets and scenes from the script.
        for shot in script.shots:
            # Create subtitle asset
            shot_subtitle = SubtitleAsset.from_data(shot.subtitle)

            # Create scene with initial subtitle reference
            scene = Scene(description=shot.description).add_asset_references(
                AssetReference.from_asset(shot_subtitle).with_start_time(shot.start_time).with_end_time(shot.end_time)
            )

            # Add subtitle asset to project
            project = project.add_assets(shot_subtitle)

            # Process each media reference in the shot
            for media_ref in shot.media_references:
                # Find the referenced media
                referenced_media = next(m for m in media if m.id == media_ref.media_id)

                # Convert media to asset
                media_asset = convert_media_to_asset(referenced_media)

                # Create asset reference with timing and effects
                asset_ref = (
                    AssetReference.from_asset(media_asset)
                    .with_start_time(media_ref.start_time)
                    .with_end_time(media_ref.end_time)
                )

                # Add effects if it's an image asset
                if media_asset.type == "image" and media_ref.effects:
                    asset_ref = asset_ref.with_effects([create_effect(effect) for effect in media_ref.effects])

                # Add media asset and its reference to the scene
                project = project.add_assets(media_asset)
                scene = scene.add_asset_references(asset_ref)

            # Add completed scene to project timeline
            project = project.add_timeline_events(scene)

        return project

    def to_file(self, file: FilePath | WritableBuffer[str]) -> None:
        """
        Write the Project object to a YAML file.

        :param file: The path to the YAML file.
        """
        project = self.model_dump(exclude_none=True)
        project["assets"] = {asset_id: asset.model_dump() for asset_id, asset in self.assets.items()}
        project["timeline"] = [event.model_dump() for event in self.timeline]
        project_yaml = yaml.safe_dump(project, allow_unicode=True, sort_keys=False)

        if isinstance(file, (str, Path)):
            Path(file).write_text(project_yaml)
        else:
            file.write(project_yaml)

    def add_assets(self, assets: AssetInputType) -> VideoProject:
        """
        Add one or more assets to the project.

        :param assets: The asset or list of assets to add.
        :return: The updated project.
        """
        _assets = assets if isinstance(assets, Sequence) else [assets]

        for asset in _assets:
            if not isinstance(asset, Mapping):
                self.assets[asset.id] = asset
                continue

            if not isinstance(asset, Mapping):
                msg = f"Invalid asset type: {type(asset)}"
                raise ValueError(msg)

            if "type" not in asset:
                self.assets.update({a.id: a for a in _process_asset_dicts(asset)})
                continue

            asset = _process_single_asset_dict(asset)
            self.assets[asset.id] = asset

        return self

    def add_timeline_events(self, events: EventOrEventSequence) -> VideoProject:
        """
        Add one or more events to the timeline.

        :param events: The event or list of events to add.
        :return: The updated project.
        :raises ValueError: If an asset referenced in the events does not exist in the project.
        """

        def validate_asset_id(asset_id: str, context: str = "") -> None:
            """Helper to validate asset ID exists"""
            if asset_id not in self.assets:
                msg = f"Asset with ID '{asset_id}' {context}not found in project assets."
                raise IndexError(msg)

        def validate_scene_assets(scene_event: Scene | Mapping[str, Any]) -> None:
            """Helper to validate assets referenced in a scene"""
            if isinstance(scene_event, Scene):
                for ref in scene_event.asset_references:
                    validate_asset_id(ref.asset_id, "referenced in scene ")
            else:
                for ref in scene_event["asset_references"]:
                    if isinstance(ref, AssetReference):
                        validate_asset_id(ref.asset_id, "referenced in scene ")
                    else:
                        validate_asset_id(ref["asset_id"], "referenced in scene ")

        # Convert single event to list
        _events = events if isinstance(events, Sequence) else [events]

        # Validate all asset references exist
        for event in _events:
            if isinstance(event, Scene):
                validate_scene_assets(event)
            elif isinstance(event, AssetReference):
                validate_asset_id(event.asset_id)
            elif isinstance(event, Mapping):
                if "asset_references" in event:
                    validate_scene_assets(event)
                else:
                    validate_asset_id(event["asset_id"])

        self.timeline = self.timeline.add_events(events).sort()

        return self

    def add_narration(self, speech_synthesizer: SpeechSynthesizer) -> VideoProject:
        """
        Add narration to subtitles inside Scene objects by generating speech audio from subtitle text.

        Updates asset timings within each Scene to match narration duration, dividing time equally
        between multiple images.

        :param speech_synthesizer: The speech synthesizer to use for generating narration audio
        :return: The updated project with narration added
        """
        current_time = None

        for i, scene in enumerate(self.timeline.sort()):
            if not isinstance(scene, Scene):
                continue

            # Get subtitle content from scene
            subtitle_refs = [ref for ref in scene.asset_references if ref.asset_type == "subtitle"]

            if not subtitle_refs:
                continue

            # Get subtitle assets and their text content
            subtitle_assets = [cast(SubtitleAsset, self.get_asset(ref.asset_id)) for ref in subtitle_refs]

            # Generate narration for subtitle content
            texts = [subtitle.to_string() for subtitle in subtitle_assets]
            narration_assets = speech_synthesizer.synthesize(texts)

            # Add narration assets to project
            self.add_assets(narration_assets)

            # Calculate total narration duration for this scene
            total_narration_duration = sum(narration.duration for narration in narration_assets)

            # Get non-subtitle assets to adjust timing
            non_subtitle_refs = [ref for ref in scene.asset_references if ref.asset_type != "subtitle"]
            image_refs = [ref for ref in non_subtitle_refs if ref.asset_type == "image"]
            other_refs = [ref for ref in non_subtitle_refs if ref.asset_type != "image"]

            if current_time is None:
                current_time = scene.asset_references[0].start_time

            new_refs = []

            # Adjust image timings - divide narration duration equally
            if image_refs:
                time_per_image = total_narration_duration / len(image_refs)
                for idx, ref in enumerate(image_refs):
                    new_start = current_time + (idx * time_per_image)
                    new_end = new_start + time_per_image
                    new_ref = ref.model_copy().with_start_time(new_start).with_end_time(new_end)
                    new_refs.append(new_ref)

            # Add other non-image assets with full narration duration
            for ref in other_refs:
                new_ref = (
                    ref.model_copy()
                    .with_start_time(current_time)
                    .with_end_time(current_time + total_narration_duration)
                )
                new_refs.append(new_ref)

            # Add subtitle references spanning full narration duration
            for ref in subtitle_refs:
                new_ref = (
                    ref.model_copy()
                    .with_start_time(current_time)
                    .with_end_time(current_time + total_narration_duration)
                )
                new_refs.append(new_ref)

            # Add narration references
            for narration in narration_assets:
                narration_ref = (
                    AssetReference.from_asset(narration)
                    .with_start_time(current_time)
                    .with_end_time(current_time + narration.duration)
                )
                new_refs.append(narration_ref)

            # Update current_time for next scene
            current_time += total_narration_duration

            # Create new scene with updated references
            new_scene = scene.model_copy(update={"asset_references": new_refs})
            self.timeline[i] = new_scene

        return self

    def add_captions(
        self,
        transcription: Transcription,
        *,
        max_duration: int = 5,
        params: TextAssetParams | None = None,
        scene_index: int | None = None,
        overwrite: bool = False,
    ) -> VideoProject:
        """
        Add subtitles to the project from a transcription.

        :param transcription: The transcription to add subtitles from.
        :param max_duration: The maximum duration of each subtitle.
        :param params: The parameters for the subtitle assets.
        :param scene_index: The index of the scene to add the subtitles to.
        :param overwrite: Whether to overwrite existing subtitles in the scene.
        :return: The updated project.
        """
        subtitles = []
        references = []

        phrases = _group_transcript_into_sentences(transcription, max_duration=max_duration)

        if scene_index is not None:
            scene = self.timeline[scene_index]

            if scene.has_subtitles and not overwrite:
                msg = f"Scene at index {scene_index} already has subtitles. Use `overwrite=True` to replace."
                raise ValueError(msg)

            # Remove existing subtitles
            for ref in scene.asset_references:
                if ref.asset_type == "subtitle":
                    self.remove_asset(ref.asset_id)

            # Calculate time scale factor if needed
            current_time = scene.start_time

            for phrase in phrases:
                subtitle_text = " ".join(word.text for word in phrase)
                subtitle = SubtitleAsset.from_data(subtitle_text)

                # Calculate scaled duration
                phrase_duration = phrase[-1].end_time - phrase[0].start_time

                start_time = current_time
                end_time = start_time + phrase_duration

                # Ensure we don't exceed scene bounds
                end_time = min(end_time, scene.end_time)

                subtitle_ref = AssetReference.from_asset(
                    asset=subtitle,
                    asset_params=params,
                    start_time=start_time,
                    end_time=end_time,
                )
                subtitles.append(subtitle)
                references.append(subtitle_ref)

                current_time = end_time

            self.add_assets(subtitles)
            scene = scene.add_asset_references(references)
            self.timeline[scene_index] = scene
        else:
            # Handle non-scene case
            for phrase in phrases:
                subtitle_text = " ".join(word.text for word in phrase)
                subtitle = SubtitleAsset.from_data(subtitle_text)

                subtitle_ref = AssetReference.from_asset(
                    asset=subtitle,
                    asset_params=params,
                    start_time=phrase[0].start_time,
                    end_time=phrase[-1].end_time,
                )
                subtitles.append(subtitle)
                references.append(subtitle_ref)

            self.add_assets(subtitles)
            self.add_timeline_events(references)

        return self

    def add_captions_from_transcriber(
        self,
        audio_transcriber: AudioTranscriber,
        *,
        max_duration: int = 5,
        params: TextAssetParams | None = None,
        overwrite: bool = False,
    ) -> VideoProject:
        """
        Add subtitles to the project from audio assets using an audio transcriber.

        :param audio_transcriber: The audio transcriber to use for transcribing audio assets.
        :param max_duration: The maximum duration of each subtitle.
        :param params: The parameters for the subtitle assets.
        :param overwrite: Whether to overwrite existing subtitles in the scene.
        :return: The updated project.
        """
        for i, event in enumerate(self.timeline):
            if not isinstance(event, Scene) or not event.has_audio:
                continue

            for asset_ref in event.asset_references:
                if asset_ref.asset_type != "audio":
                    continue

                audio_asset = self.get_asset(asset_ref.asset_id)
                audio_asset = cast(AudioAsset, audio_asset)
                audio_transcription = audio_transcriber.transcribe(audio_asset)

                self.add_captions(
                    audio_transcription,
                    max_duration=max_duration,
                    params=params,
                    scene_index=i,
                    overwrite=overwrite,
                )

        return self

    def with_subtitle_params(self, params: TextAssetParams | Mapping[str, Any]) -> VideoProject:
        """
        Override the subtitle parameters for the assets in the project.

        :param params: The subtitle parameters to set.
        :return: The updated project.
        """
        if not self.timeline:
            msg = "The project timeline is empty."
            raise ValueError(msg)

        params = TextAssetParams.model_validate(params)

        for i, event in enumerate(self.timeline):
            if isinstance(event, Scene):
                self.timeline[i].with_subtitle_params(params)
            elif isinstance(event, AssetReference):
                self.timeline[i].asset_params = params

        return self

    def with_title(self, title: str) -> VideoProject:
        """
        Override the title of the project.

        :param title: The title to set.
        :return: The updated project.
        """
        self.config.title = title
        return self

    def with_version(self, version: int) -> VideoProject:
        """
        Override the project version.

        :param version: The version to set.
        :return: The updated project.
        """
        self.config.version = version
        return self

    def with_fps(self, fps: int) -> VideoProject:
        """
        Override the FPS of the project.

        :param fps: The FPS to set.
        :return: The updated project.
        """
        self.config.fps = fps
        return self

    def with_resolution(self, resolution: FrameSize) -> VideoProject:
        """
        Override the resolution of the project.

        :param resolution: The resolution to set.
        :return: The updated project.
        """
        self.config.resolution = resolution
        return self

    def get_asset(self, asset_id: str) -> Asset:
        """
        Get an asset by its ID.

        :param asset_id: The ID of the asset.
        :return: The Asset object.
        :raises ValueError: If the asset is not found in the project assets.
        """
        try:
            return self.assets[asset_id]
        except KeyError:
            msg = f"Asset with ID '{asset_id}' not found in the project assets."
            raise KeyError(msg) from None

    def get_timeline_event(self, index: int) -> TimelineEvent:
        """
        Get a timeline event by its index.

        :param index: The index of the timeline event.
        :return: The TimelineEvent object.
        :raises ValueError: If the index is out of range.
        """
        try:
            return self.timeline[index]
        except IndexError:
            msg = "Index out of range."
            raise IndexError(msg) from None

    def remove_asset(self, asset_id: str) -> VideoProject:
        """
        Remove an asset from the project.

        :param asset_id: The ID of the asset to remove.
        :return: The updated project.
        """
        try:
            for i, event in enumerate(self.timeline):
                if isinstance(event, Scene):
                    self.timeline[i] = event.remove_references_by_asset_id(asset_id)
                elif isinstance(event, AssetReference) and event.asset_id == asset_id:
                    del self.timeline[i]
            del self.assets[asset_id]
            return self
        except KeyError:
            msg = f"Asset with ID '{asset_id}' not found in the project assets."
            raise KeyError(msg) from None

    def remove_timeline_event(self, index: int) -> VideoProject:
        """
        Remove a timeline event from the project.

        :param index: The index of the timeline event to remove.
        :return: The updated project.
        """
        try:
            del self.timeline[index]
            return self
        except IndexError:
            msg = "Timeline event index out of range."
            raise IndexError(msg) from None


def _process_asset_dicts(asset_data: Mapping[str, Any]) -> list[Asset]:
    """
    Process a list of asset dictionaries.
    """
    processed: list[Asset] = []
    for key, value in asset_data.items():
        asset = _process_single_asset_dict(value)
        if asset.id is None:
            asset.id = key
        processed.append(asset)
    return processed


def _process_single_asset_dict(asset_data: Mapping[str, Any]) -> Asset:
    """
    Process a single asset dictionary.
    """
    if "type" not in asset_data:
        msg = "Asset type must be specified."
        raise ValueError(msg)
    asset_type = asset_data["type"]
    return create_asset(asset_type, **{k: v for k, v in asset_data.items() if k != "type"})


def _create_shot_subtitle_assets(
    shot: Shot,
    speech_asset: AudioAsset | None = None,
    transcriber: AudioTranscriber | None = None,
) -> tuple[list[SubtitleAsset], list[AssetReference]]:
    """
    Create subtitle assets for a given shot.
    """
    if shot.subtitle is None:
        return [], []

    if speech_asset is None or transcriber is None:
        subtitle = SubtitleAsset.from_data(shot.subtitle)
        reference = AssetReference.from_asset(subtitle, start_time=shot.start_time, end_time=shot.end_time)
        return [subtitle], [reference]

    transcription = transcriber.transcribe(speech_asset)

    subtitles = []
    references = []

    phrases = _group_transcript_into_sentences(transcription)

    for i, phrase in enumerate(phrases):
        subtitle_text = " ".join(word.text for word in phrase)
        subtitle_asset = SubtitleAsset.from_data(subtitle_text)
        subtitle_start_time = shot.start_time + phrase[0].start_time
        subtitle_end_time = shot.end_time if i == len(phrases) - 1 else shot.start_time + phrase[-1].end_time
        subtitle_asset_ref = AssetReference.from_asset(
            subtitle_asset, start_time=subtitle_start_time, end_time=subtitle_end_time
        )
        subtitles.append(subtitle_asset)
        references.append(subtitle_asset_ref)

    return subtitles, references


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
        return bool(number_pattern.match(word)) or word in [",", "."]

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
