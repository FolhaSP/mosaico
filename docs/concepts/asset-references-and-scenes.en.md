# Asset References and Scenes

!!! note "Prerequisites"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)

## Overview

Asset references are a core concept in Mosaico that allow you to control how assets appear in your video timeline. They provide a way to manage different types of media efficiently, control how media appears in your video, maintain type safety and validation, create complex video compositions, and extend functionality as needed. A group of asset references can be combined into a scene to create a logical section of your video.

In summary, the asset system in Mosaico consists of two main components:

- **Asset References**: Define when and how assets appear in the timeline
- **Scenes**: Group related asset references together

These components form the building blocks of your video timeline and control the presentation of your media assets.

## Asset References

Asset references are crucial for controlling how assets appear in your video timeline. They act as instructions for:

- When assets appear and disappear
- How long they're visible
- What effects are applied
- Any parameter overrides

Think of them as the "stage directions" for your assets:

```python
from mosaico.assets.reference import AssetReference

# Control asset timing and effects
asset_ref = (
    AssetReference.from_asset(image)
    .with_start_time(0)
    .with_end_time(5)
    .with_effects([fade_in_effect])
)
```

### Structure

The basic structure of an asset reference consists of the following components:

```python
from mosaico.assets.reference import AssetReference

#Basic structure of an asset reference
reference = AssetReference(
    asset_id="background_01",           # Asset identifier
    asset_params=ImageAssetParams(...), # Optional parameter overrides
    start_time=0,                       # When asset appears
    end_time=10,                        # When asset disappears
    effects=[]                          # Optional effects
)
```

### Creating Asset References

There are two main ways to create asset references:

1. **From an Existing Asset**
```python
# Create reference from asset
logo_ref = AssetReference.from_asset(
    asset=logo_asset,
    start_time=0,
    end_time=30
)

# Using builder pattern
title_ref = AssetReference.from_asset(title_asset)\
    .with_start_time(5)\
    .with_end_time(10)\
    .with_params(TextAssetParams(font_size=48))\
    .with_effects([fade_in_effect])
```

2. **Direct Construction**
```python
# Manual reference creation
music_ref = AssetReference(
    asset_id="background_music",
    start_time=0,
    end_time=60,
    asset_params=AudioAssetParams(volume=0.8)
)
```


## Scenes

Scenes are a way to group assets together in your video timeline. They allow you to organize your video into logical sections and apply effects to multiple assets at once. Scenes can be used to create transitions, apply global effects, or group related assets together:

!!! warning
    Scene's implementation of transitions and global effects is not yet supported in Mosaico but will be added in future releases.

```python
from mosaico.scenes.scene import Scene

# Create a scene with multiple assets
scene = Scene(
    asset_references=[
        AssetReference.from_asset(image1),
        AssetReference.from_asset(image2),
    ],
)
```

### Common Patterns

#### Background with Overlay

```python
scene = Scene(
    title="Title Scene",
    asset_references=[
        # Background layer
        AssetReference.from_asset(background)
            .with_start_time(0)
            .with_end_time(10),

        # Text overlay
        AssetReference.from_asset(title)
            .with_start_time(2)
            .with_end_time(8)
    ]
)
```

#### Audio-Visual Sync

```python
narration_ref = AssetReference.from_asset(narration)
    .with_start_time(0)
    .with_end_time(narration.duration)

scene = Scene(
    asset_references=[
        # Visual content matches narration timing
        AssetReference.from_asset(visual)
            .with_start_time(narration_ref.start_time)
            .with_end_time(narration_ref.end_time),
        narration_ref
    ]
)
```

#### Sequential Content

```python
def create_sequence_scene(assets: list[BaseAsset], duration_per_asset: float) -> Scene:
    """Create a scene with sequential assets."""
    references = []
    current_time = 0

    for asset in assets:
        references.append(
            AssetReference.from_asset(asset)
                .with_start_time(current_time)
                .with_end_time(current_time + duration_per_asset)
        )
        current_time += duration_per_asset

    return Scene(asset_references=references)
```

## Best Practices

**Asset Reference Organization**

- Keep related assets together in scenes
- Use meaningful timing relationships
- Apply effects judiciously

**Scene Structure**

- Group logically related content
- Maintain clear timing hierarchies
- Add descriptive titles and descriptions

**Timeline Management**

- Verify asset existence before referencing
- Check timing consistency
- Handle transitions between scenes

## Conclusion

This comprehensive asset system allows you to manage different types of media efficiently, control how media appears in your video, maintain type safety and validation, create complex video compositions, and extend functionality as needed.
