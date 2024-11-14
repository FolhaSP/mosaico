# Mosaico

Mosaico is a Python library for programmatically creating and managing video compositions. It provides a high-level interface for working with media assets, positioning elements, applying effects, and generating video scripts.

## Installation

```bash
pip install mosaico
```

## Features

- AI-powered script generation for videos
- Rich media asset management (audio, images, text, subtitles)
- Flexible positioning system (absolute, relative, region-based)
- Built-in effects (pan, zoom) with extensible effect system
- Text-to-speech synthesis integration
- Integration with popular ML frameworks, such as [Haystack](https://haystack.deepset.ai/) and [LangChain](https://www.langchain.com/)

## Quick Start

```python
from mosaico.assets import create_asset
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig

# Create assets
image = create_asset("image", path="background.jpg")
text = create_asset("text", data="Hello World")
audio = create_asset("audio", path="narration.mp3")

# Create asset references with timing
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)
text_ref = AssetReference.from_asset(text).with_start_time(1).with_end_time(4)
audio_ref = AssetReference.from_asset(audio).with_start_time(0).with_end_time(5)

# Create scene
scene = Scene(asset_references=[image_ref, text_ref, audio_ref])

# Create project
project = (
    VideoProject(config=VideoProjectConfig())
    .add_assets([image, text, audio])
    .add_timeline_events(scene)
)
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

- [Getting Started](https://folhasp.github.io/mosaico/getting_started.html): Installation, setup, and basic usage
- [Concepts](https://folhasp.github.io/mosaico/concepts.html): Overview of key concepts and terminology
- [Cookbook](https://folhasp.github.io/mosaico/cookbook.html): Examples and tutorials for common tasks
- [API Reference](https://folhasp.github.io/mosaico/api.html): Detailed reference for all classes and functions
- [Development](https://folhasp.github.io/mosaico/development.html): Information for contributors and developers
- [Roadmap](https://folhasp.github.io/mosaico/roadmap.html): Future plans and features

## References

- [MoviePy](https://github.com/Zulko/moviepy)
