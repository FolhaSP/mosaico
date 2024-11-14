# Effects

!!! note "Prerequisites"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Asset References__](media-and-assets.md#asset-references)

## Overview

The Effects System in Mosaico provides a way to add dynamic animations and visual effects to your video elements. Effects can be applied to any asset reference and can be combined to create complex animations.

## Interface

At the core of the effects system is the Effect protocol:

```python
from moviepy.Clip import Clip
from typing import Protocol, TypeVar

ClipType = TypeVar("ClipType", bound=Clip)

class Effect(Protocol[ClipType]):
    """Base protocol for all effects."""

    def apply(self, clip: ClipType) -> ClipType:
        """Apply the effect to a clip."""
        ...
```

The user can create custom effects by implementing the `apply` method. The `apply` method takes a `Clip` object and returns a modified `Clip` object with the effect applied.

## Built-in Effects

Mosaico provides a set of built-in effects that can be used to create dynamic animations in your video compositions. These effects fall into two main categories: pan effects for camera-like movements and zoom effects for dynamic scaling.

Here's a complete list of available effects:

| Effect | Type | Parameters | Description |
|--------|------|------------|-------------|
| PanLeftEffect | `pan_left` | `zoom_factor: float = 1.1` | Move from right to left across the frame |
| PanRightEffect | `pan_right` | `zoom_factor: float = 1.1` | Move from left to right across the frame |
| PanUpEffect | `pan_up` | `zoom_factor: float = 1.1` | Move from bottom to top across the frame |
| PanDownEffect | `pan_down` | `zoom_factor: float = 1.1` | Move from top to bottom across the frame |
| ZoomInEffect | `zoom_in` | `start_zoom: float = 1.0`<br>`end_zoom: float = 1.1` | Zoom into the frame |
| ZoomOutEffect | `zoom_out` | `start_zoom: float = 1.5`<br>`end_zoom: float = 1.4` | Zoom out of the frame |

Here are some examples of how to use these effects:

```python
from mosaico.effects.factory import create_effect

# Pan effect example
pan_right = create_effect(
    "pan_right",
    zoom_factor=1.2
)
image_ref = AssetReference.from_asset(image)\
    .with_effects([pan_right])

# Zoom effect example
zoom_in = create_effect(
    "zoom_in",
    start_zoom=1.0,
    end_zoom=1.3
)
image_ref = AssetReference.from_asset(image)\
    .with_effects([zoom_in])

# Combining pan and zoom
combined_effect = [
    create_effect("pan_right", zoom_factor=1.1),
    create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)
]
image_ref = AssetReference.from_asset(image)\
    .with_effects(combined_effect)
```
## Creating Custom Effects

You can create custom effects by implementing the Effect protocol:

```python
from moviepy.video.VideoClip import VideoClip

class CustomFadeEffect:
    """Custom fade effect implementation."""

    def __init__(self, fade_duration: float = 1.0):
        self.fade_duration = fade_duration

    def apply(self, clip: VideoClip) -> VideoClip:
        """Apply custom fade effect."""
        def modify_frame(t):
            # Custom frame modification logic
            frame = clip.get_frame(t)
            alpha = min(1.0, t / self.fade_duration)
            return frame * alpha

        return clip.fl(modify_frame)
```

## Combining Effects

Effects can be combined to create complex animations:

```python
# Create multiple effects
pan_right = create_effect("pan_right")
zoom_in = create_effect("zoom_in")

# Apply both effects to an asset
image_ref = AssetReference.from_asset(image)\
    .with_effects([pan_right, zoom_in])
```

## Real-World Examples

### Ken Burns Effect
```python
# Create a subtle Ken Burns effect
ken_burns = [
    create_effect(
        "zoom_in",
        start_zoom=1.0,
        end_zoom=1.2
    ),
    create_effect("pan_right")
]

# Apply to background image
background_ref = AssetReference.from_asset(background)\
    .with_effects(ken_burns)
```

### Title Animation
```python
# Create title entrance effect
title_effects = [
    create_effect("zoom_in", start_zoom=0.8, end_zoom=1.0),
    create_effect("pan_up")
]

# Apply to title
title_ref = AssetReference.from_asset(title)\
    .with_effects(title_effects)
```

## Best Practices

1. **Effect Timing**
```python
# Consider clip duration when setting effect parameters
if clip_duration < 2:
    zoom_factor = 1.1  # Subtle for short clips
else:
    zoom_factor = 1.3  # More dramatic for longer clips
```

2. **Performance Considerations**
```python
# Limit number of simultaneous effects
MAX_EFFECTS = 2

if len(effects) > MAX_EFFECTS:
    warnings.warn("Too many effects may impact performance")
```

3. **Effect Combinations**
```python
# Create reusable effect combinations
def create_entrance_effects():
    return [
        create_effect("zoom_in", start_zoom=0.8),
        create_effect("pan_up")
    ]
```

## Conclusion

The Effects System in Mosaico provides a powerful way to add dynamic elements to your video compositions. By understanding and properly using effects, you can create professional-looking videos with engaging visual elements. Whether using built-in effects or creating custom ones, the system's flexibility allows for creative and impactful video productions.
