# Mosaico

[![License](https://img.shields.io/github/license/folhasp/mosaico?style=flat-square&color=blue)](https://github.com/folhasp/mosaico/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/mosaico?style=flat-square&color=blue&logo=python&logoColor=gold)](https://pypi.org/project/mosaico/)
[![PyPI](https://img.shields.io/pypi/v/mosaico?style=flat-square&color=blue&logo=pypi&logoColor=gold)](https://pypi.org/project/mosaico/)
[![Downloads](https://img.shields.io/pypi/dm/mosaico?style=flat-square&color=green&logo=pypi&logoColor=gold)](https://pypi.org/project/mosaico/)
[![Stars](https://img.shields.io/github/stars/folhasp/mosaico?style=flat-square&color=yellow&logo=github)](https://github.com/folhasp/mosaico)

Mosaico is a Python library for programmatically creating and managing video compositions. It provides a high-level interface for working with media assets, positioning elements, applying effects, and generating video scripts.

## Installation

```bash
pip install mosaico
```

For additional dependencies, see the [additional dependencies](https://folhasp.github.io/mosaico/getting-started/installation#additional-dependencies) section in the documentation.

## Features

- AI-powered script generation for videos
- Rich media asset management (audio, images, text, subtitles)
- Flexible positioning system (absolute, relative, region-based)
- Built-in effects (pan, zoom) with extensible effect system
- Text-to-speech synthesis integration
- Integration with popular ML frameworks, such as [Haystack](https://haystack.deepset.ai/) and [LangChain](https://www.langchain.com/)

## Quick Start

Install Mosaico and additional dependencies for news video generation:

```bash
pip install "mosaico[assemblyai,elevenlabs]"
```

Easily create and render a video project from a script generator:

```python
import os

from mosaico.audio_transcribers.assemblyai import AssemblyAIAudioTranscriber
from mosaico.script_generators.news import NewsVideoScriptGenerator
from mosaico.speech_synthesizers.elevenlabs import ElevenLabsSpeechSynthesizer
from mosaico.video.project import VideoProject
from mosaico.video.rendering import render_video


# Set your API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


# Import your media
media = [
    Media.from_path("background.jpg", metadata={"description": "Background image"}),
    Media.from_path("image1.jpg", metadata={"description": "Image 1"}),
    Media.from_path("image2.jpg", metadata={"description": "Image 2"}),
    Media.from_path("image3.jpg", metadata={"description": "Image 3"}),
]

# Textual context for the video
context = "..."

# Create script generator
script_generator = NewsVideoScriptGenerator(
    context=context,
    language="pt",
    num_paragraphs=8,
    api_key=ANTHROPIC_API_KEY,
)

# Create speech synthesizer
speech_synthesizer = ElevenLabsSpeechSynthesizer(
    voice_id="Xb7hH8MSUJpSbSDYk0k2",
    voice_stability=0.8,
    voice_similarity_boost=0.75,
    voice_speaker_boost=False,
    api_key=ELEVENLABS_API_KEY,
)

# Create audio transcriber for captions
audio_transcriber = AssemblyAIAudioTranscriber(api_key=ASSEMBLYAI_API_KEY)

# Create project
project = (
    VideoProject.from_script_generator(script_generator, media)
    .with_title("My Breaking News Video")
    .with_fps(30)
    .with_resolution((1920, 1080))
    .add_narration(speech_synthesizer)
    .add_captions_from_transcriber(audio_transcriber, overwrite=True)
)

# Render project
render_video(project, "path/to/dir")
```

Or create a video project from scratch:

```python
from mosaico.video.project import VideoProject
from mosaico.assets import ImageAsset, TextAsset, AudioAsset, AssetReference

# Import your media as production-ready assets
assets = [
    ImageAsset.from_path("background.jpg", metadata={"description": "Background image"}),
    ImageAsset.from_path("image1.jpg", metadata={"description": "Image 1"}),
    ImageAsset.from_path("image2.jpg", metadata={"description": "Image 2"}),
    ImageAsset.from_path("image3.jpg", metadata={"description": "Image 3"}),
    TextAsset.from_data("Subtitle 1"),
    TextAsset.from_data("Subtitle 2"),
    TextAsset.from_data("Subtitle 3"),
    AudioAsset.from_path("narration.mp3"),
]

asset_references = [
    AssetReference.from_asset(background, start_time=0, end_time=10),
    AssetReference.from_asset(image1, start_time=10, end_time=20),
    AssetReference.from_asset(image2, start_time=20, end_time=30),
    AssetReference.from_asset(image3, start_time=30, end_time=40),
    AssetReference.from_asset(subtitle1, start_time=40, end_time=50),
    AssetReference.from_asset(subtitle2, start_time=50, end_time=60),
    AssetReference.from_asset(subtitle3, start_time=60, end_time=70),
    AssetReference.from_asset(narration, start_time=70, end_time=80),
]

scene = Scene(description="My Scene").add_asset_references(asset_references)

project = (
    VideoProject()
    .with_title("My Breaking News Video")
    .with_fps(30)
    .with_resolution((1920, 1080))
    .add_assets(assets)
    # Add the asset references as scene events to the timeline
    .add_timeline_events(scene)
    # Or add asset references directly to the timeline
    # .add_timeline_events(asset_references)
)

# Render project
render_video(project, "path/to/dir")
```

## Cookbook

For common usage patterns and examples, see our [Cookbook](docs/cookbook/index.en.md). Some examples include:

- Creating basic videos with background and text
- Building photo slideshows with music
- Generating news videos from articles
- Working with different asset types
- Applying effects and animations
- Using AI for script generation

## Documentation

Comprehensive documentation is available [here](https://folhasp.github.io/mosaico). Documentation includes:

- [Getting Started](https://folhasp.github.io/mosaico): Installation, setup, and basic usage
- [Concepts](https://folhasp.github.io/mosaico/concepts): Overview of key concepts and terminology
- [Cookbook](https://folhasp.github.io/mosaico/cookbook): Examples and tutorials for common tasks
- [API Reference](https://folhasp.github.io/mosaico/api-reference): Detailed reference for all classes and functions
- [Development](https://folhasp.github.io/mosaico/development): Information for contributors and developers
- [Roadmap](https://folhasp.github.io/mosaico/roadmap): Future plans and features

## References

- [MoviePy](https://github.com/Zulko/moviepy)
