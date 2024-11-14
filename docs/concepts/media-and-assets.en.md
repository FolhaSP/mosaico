# Media and Assets

## Overview

In Mosaico, media and assets are the core building blocks of video production. They represent the raw materials and production-ready elements that make up a video composition. This guide explains the difference between media and assets, how they are used in video production, and the asset type system in Mosaico.

## Understanding the Production Pipeline

In video production with Mosaico, there are two distinct stages of content handling:

1. **Media Stage**: Raw Content Collection
2. **Asset Stage**: Production-Ready Elements

This two-stage approach mirrors professional video production workflows, where raw materials are prepared and transformed into production-ready elements. The glue between these stages are script generators, which will be covered in a later section.

### Media Objects: Raw Materials

Media objects represent the "raw materials" stage of your content:

- Raw video clips
- Unprocessed audio files
- Original images
- Plain text content

```python
from mosaico.media import Media

# Collecting raw materials
background = Media.from_path("media/background.png")
voice_over = Media.from_path("media/narration.wav")
graphics = Media.from_path("media/graphics.png")
script = Media.from_path("media/script.txt")
```

Think of Media objects as items in your "media library" before they're prepared for production.

### Assets: Production-Ready Elements

Assets are the fundamental building blocks of any video composition in Mosaico and represent the "production-ready" stage of a media. They represent different types of media elements that can be combined to create a video, such as images, audio clips, text overlays, and subtitles. Think of assets as the raw materials you need to build your video.

Each asset in Mosaico has essentially the same structure of a media object but with additional properties and capabilities, such as type-specific parameters and metadata. Assets are designed to be production-ready and can be directly used in video compositions:

- A unique identifier
- Core content (the actual media data)
- Type-specific parameters
- Metadata for additional information
- Built-in validation and processing capabilities

```python
from mosaico.assets import ImageAsset, AudioAsset

# Instantiating assets
background = ImageAsset.from_path("assets/background.png")
voice_over = AudioAsset.from_path("assets/narration.wav")
graphics = ImageAsset.from_path("assets/graphics.png")
subtitles = [SubtitleAsset.from_data(data) for data in subtitle_data]
```

### Key Differences

Here's a summary of the key differences between Media and Assets:

| Aspect | Media Objects | Assets |
|--------|--------------|---------|
| Purpose | Raw content storage and basic handling | Video production element handling |
| State | Unprocessed, original form | Processed, production-ready |
| Properties | Basic metadata and content access | Production parameters and behaviors |
| Usage | Content collection and storage | Timeline and composition |
| Integration | External system bridging | Video rendering system |

## The Asset Type System

Mosaico implements a flexible and type-safe asset system using a base class that other asset types extend. This hierarchical approach ensures consistency while allowing each asset type to have its specific features and parameters.

### Base Asset Structure

The base asset class defines the core structure for all asset types in Mosaico. It includes common properties like the asset type and parameters, which are then extended by specific asset types.

```python
from mosaico.assets.base import BaseAsset
from pydantic import BaseModel

class BaseAsset(Media, Generic[T]):
    type: str
    params: T
```

### Types of Assets

To create a video composition, you need different types of assets that represent various media elements. Here are some common asset types in __Mosaico__:

!!! note "Video Assets"
    While planned, video assets are not currently implemented in Mosaico as their integration architecture is still being discussed. They will be added soon in future releases.

#### Audio

Audio assets manage all sound elements in your video, including narration, music, sound effects, and voice-overs. They include basic properties like duration, sample rate, channels, volume, and cropping points. These help you control how audio plays in your video while keeping professional quality standards.

Example usage:

```python
from mosaico.assets import AudioAsset, AudioAssetParams

# Create an audio asset with specific volume
audio = AudioAsset.from_path(
    "narration.mp3",
    params=AudioAssetParams(volume=0.8)
)
```

#### Image

Image assets handle static visuals like backgrounds, overlays, logos, and photos in your video. They come with key properties to control how they appear: size (width and height), position, layer order (z-index), cropping, and background mode. These properties let you precisely control how images look and work together in your video.

Example usage:
```python
from mosaico.assets import ImageAsset, ImageAssetParams

# Create an image asset with positioning
image = ImageAsset.from_path(
    "background.jpg",
    params=ImageAssetParams(
        position=AbsolutePosition(x=100, y=100),
        as_background=True
    )
)
```

#### Text

Text assets let you add titles, captions, and other text elements to your videos. They include styling options like fonts, colors, alignments, and effects such as shadows and strokes. This gives you full control over how text looks and appears in your video while maintaining professional quality.

Example usage:
```python
from mosaico.assets import TextAsset, TextAssetParams

# Create styled text
text = TextAsset.from_data(
    "Welcome to My Video",
    params=TextAssetParams(
        font_size=48,
        font_color=Color("white"),
        align="center"
    )
)
```

#### Subtitles

Subtitle assets are specialized text assets designed for video captioning. They handle dialog subtitles, closed captions, translations, and timed text overlays. You can adjust their positioning, font sizes, and background colors. They include features for readability and multi-language support to create accessible videos.

Example usage:
```python
from mosaico.assets import SubtitleAsset

# Create a subtitle with proper positioning
subtitle = SubtitleAsset.from_data(
    "This is a subtitle",
    params=TextAssetParams(
        position=RegionPosition(x="center", y="bottom"),
        font_size=36
    )
)
```

## Working with Assets

Given that you already have a collection of assets, you can now start working with them to create your video composition.

A common pipeline for working with assets in Mosaico involves loading, managing, and combining assets to create a video sequence. The later will be covered in another section, but here is how you can perform basic operations with assets solely.

### Loading Assets

For the video composition process to start, you need to load your media into assets. If you already know where and how a certain content should be displayed, you can directly create the corresponding assets by calling the asset type class methods or using the asset factory system.

=== "From files"

    ```python
    from mosaico.assets import ImageAsset

    image = ImageAsset.from_path("logo.png")
    ```

=== "From raw data"

    ```python
    from mosaico.assets import TextAsset

    text = TextAsset.from_data("Hello World")
    ```

=== "From factory"

    ```python
    from mosaico.assets import create_asset

    asset = create_asset("image", path="logo.png")
    ```

=== "From existing media"

    ```python
    from mosaico.assets.utils import convert_media_to_asset

    asset = convert_media_to_asset(media_object)
    ```

### Managing Asset Parameters

All assets have parameters that control their appearance and behavior. You can update these parameters to customize how assets are displayed in your video composition.

```python
# Update text styling
text_asset = text_asset.with_params({
    "font_size": 48,
    "font_color": "#FFFFFF",
    "align": "center"
})
```

### Best Practices

When working with assets, consider the following best practices to ensure your video composition is well-organized and efficient:

1. **Organization**
    - Use meaningful asset IDs
    - Group related assets together
    - Maintain clear asset hierarchies

2. **Performance**
    - Optimize image sizes before loading
    - Use appropriate audio formats
    - Clean up unused assets

3. **Maintainability**
    - Document asset metadata
    - Use consistent naming conventions
    - Keep asset parameters organized

4. **Reusability**
    - Create reusable asset templates
    - Share common parameters
    - Use asset references effectively


## Workflow Benefits

This two-stage approach provides several advantages:

1. **Clean Separation of Concerns**
    - Media handling is separated from production logic
    - Clear distinction between raw and processed content
    - Easier content management

2. **Flexible Content Pipeline**
    - Raw content can be processed differently for different uses
    - Same media can create different types of assets
    - Easy integration with external content sources

3. **Professional Workflow**
    - Mirrors professional video production processes
    - Clear stages for content preparation
    - Organized asset management

4. **Resource Optimization**
    - Raw content is processed only when needed
    - Multiple assets can reference same media
    - Efficient resource usage

## Conclusion

Understanding this distinction between Media and Assets is fundamental to working effectively with Mosaico, as it reflects the natural progression from raw content to finished video production.
