# Video Projects

!!! note "Prerequisites"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Asset References__](asset-references-and-scenes.md#asset-references)
    - [__Scenes__](asset-references-and-scenes.md#scenes)
    - [__Script Generators__](script-generators.md)

## Overview

A video project in Mosaico represents a complete video composition that consists of three main components:

**Project Configuration**

- Basic project metadata and settings
- Video output specifications
- Technical parameters

**Asset Collection**

- Registry of all media elements
- Mapping between asset IDs and asset objects
- Asset validation and management

**Timeline**

- Sequence of events (scenes and asset references)
- Timing and synchronization
- Event organization

## Project Configuration

A video can be configured to a specific set of parameters that define its appearance and behavior. The `VideoProjectConfig` class defines the basic settings for your video:

```python
from mosaico.video.project import VideoProjectConfig

config = VideoProjectConfig(
    name="My Project",          # Project name
    version=1,                  # Project version
    resolution=(1920, 1080),    # Video dimensions
    fps=30                      # Frames per second
)
```

For instance, to change the project resolution, just update the `resolution` attribute...

```python
config.resolution = (1280, 720)
```

... and there you have it: the video project will be rendered at the new resolution.


## Creating Video Projects

There are three main ways to create a video project:

### Direct Creation

The user already knows the project structure, the assets configuration and their disposition in the timeline. In this case, the project can be created directly:

```python
from mosaico.video.project import VideoProject

project = VideoProject(
    config=VideoProjectConfig(
        name="Direct Creation Example",
        resolution=(1920, 1080)
    )
)
```

### Script-Based Generation

The user wants to generate a video project based on a script that defines the project structure. The script can be generated by a script generator, which is a class that implements the [`ScriptGenerator`](../api_reference/script-generators/index.md) protocol:

!!! note "About Script Generators"
    They are the main bridge between video projects and AI. The [`ScriptGenerator`](../api_reference/script-generators/index.md) protocol lies at the core of the video project generation process, as it defines the structure of the script that will be used to create the video project and spares the user from having to manually define the project structure.

```python
project = VideoProject.from_script_generator(
    script_generator=script_generator,  # ScriptGenerator instance
    media=media_files,                  # Sequence of Media objects
    config=video_config,                # Optional configuration
    speech_synthesizer=tts_engine,      # Optional speech synthesis
    audio_transcriber=transcriber,      # Optional transcription
    background_audio=bg_music           # Optional background music
)
```

### Loading from File

One of the main features of Mosaico is the ability to serialize and deserialize video projects to and from files. This allows users to save their projects and load them later, or share them with others.

Based on the YAML format, the [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) class provides methods to load and save projects:

```python
# Load from YAML
project = VideoProject.from_file("project.yml")

# Save to YAML
project.to_file("project.yml")
```

## Managing Project Assets

The [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) provides methods to manage assets, such as adding, removing, and retrieving them. The class is responsible for guaranteeing that all assets are correctly linked to the project, have valid references in the timeline and that they are available when needed.

### Adding Assets
```python
# Add single asset
project.add_assets(background_image)

# Add multiple assets
project.add_assets([
    main_video,
    background_music,
    subtitle_text
])

# Add with custom IDs
project.add_assets({
    "background": background_image,
    "music": background_music
})
```

### Retrieving Assets
```python
# Get asset by ID
asset = project.get_asset("background")
```

### Removing Assets
```python
# Remove asset
# This will also remove all references to the asset in the timeline
project.remove_asset("background")
```

## Timeline Management

The timeline consists of events (scenes and asset references) that define when and how assets appear in the video.

### Adding Timeline Events
```python
# Add a scene
project.add_timeline_events(
    Scene(
        title="Opening Scene",
        asset_references=[
            AssetReference.from_asset(background)
                .with_start_time(0)
                .with_end_time(5),
            AssetReference.from_asset(title_text)
                .with_start_time(1)
                .with_end_time(4)
        ]
    )
)

# Add individual asset reference
project.add_timeline_events(
    AssetReference.from_asset(background_music)
        .with_start_time(0)
        .with_end_time(project.duration)
)
```

### Removing Timeline Events
```python
# Remove event by index
project.remove_timeline_event(0)
```

### Timeline Navigation
```python
# Get total duration
duration = project.duration

# Get specific event
event = project.get_timeline_event(0)

# Iterate through timeline
for event in project.iter_timeline():
    print(f"Event at {event.start_time}s")
```

## Special Features

Here are some special capabilities that Mosaico provides to enhance video projects:

### Subtitle Generation

```python
# Add subtitles from transcription
project.add_subtitles_from_transcription(
    transcription=transcription,
    max_duration=5,  # Maximum subtitle duration
    params=TextAssetParams(
        font_size=36,
        font_color="white"
    )
)
```

### Subtitle Parameters Batch Updates

```python
# Update subtitle parameters globally
project.with_subtitle_params(
    TextAssetParams(
        font_size=48,
        stroke_width=2
    )
)
```

## Method Chaining

The [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) class supports method chaining, which allows you to call multiple methods on an object in a single line. This can make your code more concise and easier to read.

```python
project = (
    VideoProject(config=VideoProjectConfig())
    .add_assets([background_image, title_text, background_music])
    .add_timeline_events([
        AssetReference.from_asset(background_image)
            .with_start_time(0)
            .with_end_time(10),
        AssetReference.from_asset(title_text)
            .with_start_time(1)
            .with_end_time(9)
    ])
)
```

## Best Practices

**Asset Organization**

- Use meaningful asset IDs
- Group related assets together
- Keep track of asset dependencies

**Timeline Structure**

- Organize events chronologically
- Use scenes for related content
- Maintain clear timing relationships

**Project Management**

- Save projects regularly
- Version control project files
- Document project structure

## Conclusion

This documentation reflects the actual implementation of [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) in Mosaico, focusing on practical usage patterns and best practices. The examples are designed to work with the current codebase and demonstrate common video production workflows.