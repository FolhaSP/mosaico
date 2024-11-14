# Quick Start

## Creating Assets

=== "From factory function"

    ```python
    from mosaico.assets import create_asset

    # Create an image asset
    image = create_asset("image", path="background.jpg")

    # Create a text asset
    text = create_asset("text", data="Hello World")

    # Create an audio asset
    audio = create_asset("audio", path="narration.mp3")
    ```

    The `create_asset()` factory function creates different types of assets:

    - Each asset requires a type identifier ("image", "audio", "text", "subtitle")
    - Assets can be created from files using `path` or direct data using `data`
    - Assets automatically detect properties like dimensions, duration, etc.

=== "From asset classes"

      ```python
      from mosaico.assets import ImageAsset, TextAsset, AudioAsset

      # Create an image asset
      image = ImageAsset.from_path("background.jpg")

      # Create a text asset
      text = TextAsset.from_data("Hello World")

      # Create an audio asset
      audio = AudioAsset.from_path("narration.mp3")
      ```

      Alternatively, assets can be created directly using their respective classes:

      - Each asset class has specific properties and methods
      - Assets can be created from files using `from_path()` or direct data using `from_data()`
      - Assets automatically detect properties like dimensions, duration, etc.


## Creating Asset References

```python
from mosaico.assets.reference import AssetReference

# Create reference for background image
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)

# Create reference for text overlay
text_ref = AssetReference.from_asset(text).with_start_time(1).with_end_time(4)

# Create reference for audio narration
audio_ref = AssetReference.from_asset(audio).with_start_time(0).with_end_time(5)
```

Asset references determine when and how assets appear in the video:

- `from_asset()` creates a reference from an asset
- `with_start_time()` sets when the asset appears
- `with_end_time()` sets when the asset disappears
- Times are in seconds
- References can also include effects and custom parameters

## Creating a Scene

```python
from mosaico.scene import Scene

# Create a scene containing the assets
scene = Scene(asset_references=[image_ref, text_ref, audio_ref])
```

Scenes group related assets together:

- Takes a list of asset references
- Handles timing and synchronization
- Can include title and description
- Multiple scenes can be combined in a project

## Creating a Complete Project

```python
from mosaico.video.project import VideoProject, VideoProjectConfig

# Create project configuration
config = VideoProjectConfig(
    name="My First Video",
    resolution=(1920, 1080),
    fps=30
)

# Create, configure and add assets and scene to the project
project = (
    VideoProject(config=config)
    .add_assets([image, text, audio])
    .add_timeline_events(scene)
)
```

The `VideoProject` ties everything together:

- Configure project settings like resolution and framerate
- Add all assets used in the video
- Add scenes to the timeline
- Manages the complete video composition

## Export the Video Project

The project can be exported to a YAML file:

```python
project.to_file("my_first_video.yml")
```

## Optional: Adding Effects

```python
from mosaico.effects.factory import create_effect

# Create a zoom effect
zoom_effect = create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)

# Add effect to text reference
text_ref = text_ref.with_effects([zoom_effect])
```

Effects can be added to asset references:

- Various built-in effects (zoom, pan)
- Effects have configurable parameters
- Multiple effects can be combined
- Effects are applied during rendering

## Complete Example

```python
from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.effects.factory import create_effect

# 1. Create assets
image = create_asset("image", path="background.jpg")
text = create_asset("text", data="Hello World")
audio = create_asset("audio", path="narration.mp3")

# 2. Create effect
zoom_effect = create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)

# 3. Create asset references with timing
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)
text_ref = (
    AssetReference.from_asset(text)
    .with_start_time(1)
    .with_end_time(4)
    .with_effects([zoom_effect])
)
audio_ref = AssetReference.from_asset(audio).with_start_time(0).with_end_time(5)

# 4. Create scene
scene = Scene(
    title="Opening Scene",
    asset_references=[image_ref, text_ref, audio_ref]
)

# 5. Create, configure and add assets and events to the project
project = (
    VideoProject(
        config=VideoProjectConfig(
            name="My First Video",
            resolution=(1920, 1080),
            fps=30
        )
    )
    .add_assets([image, text, audio])
    .add_timeline_events(scene)
)

# 6. Save project
project.to_file("my_video.yml")
```

This creates a 5-second video with:

- A background image
- Text that fades in at 1s with a zoom effect
- Audio narration throughout
- HD resolution at 30fps

The project can be saved to a YAML file for later editing or rendering.
