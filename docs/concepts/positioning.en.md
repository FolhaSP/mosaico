# Positioning System

!!! note "Prerequisites"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)

## Overview

The Positioning System in Mosaico provides a flexible way to place visual elements (like images and text) in your video composition. It offers three distinct positioning strategies, each suited for different use cases.

## Positioning Types

### Absolute Positioning (Pixel-Based)
Precise positioning using exact pixel coordinates from the top-left corner of the frame.

```python
from mosaico.positioning import AbsolutePosition

class AbsolutePosition:
    type: Literal["absolute"] = "absolute"
    x: NonNegativeInt = 0          # Pixels from left
    y: NonNegativeInt = 0          # Pixels from top
```

Example Usage:
```python
# Position an element 100 pixels from left, 50 from top
logo_position = AbsolutePosition(x=100, y=50)
```


### Relative Positioning (Percentage-Based)
Position elements using percentages of the frame dimensions.

```python
from mosaico.positioning import RelativePosition

class RelativePosition:
    type: Literal["relative"] = "relative"
    x: NonNegativeFloat = 0.5      # 0.0 to 1.0 (left to right)
    y: NonNegativeFloat = 0.5      # 0.0 to 1.0 (top to bottom)
```

Example Usage:
```python
# Center an element (50% from left and top)
centered_position = RelativePosition(x=0.5, y=0.5)

# Position at bottom-right corner
corner_position = RelativePosition(x=1.0, y=1.0)
```

Use Cases:

- Responsive layouts
- Resolution-independent positioning
- Dynamic compositions
- Adaptable designs

### Region Positioning (Named Regions)
Position elements using predefined regions of the frame.

```python
from mosaico.positioning import RegionPosition

class RegionPosition:
    type: Literal["region"] = "region"
    x: Literal["left", "center", "right"] = "center"
    y: Literal["top", "center", "bottom"] = "center"
```

Example Usage:
```python
# Position in bottom-center (typical for subtitles)
subtitle_position = RegionPosition(x="center", y="bottom")

# Position in top-right corner
title_position = RegionPosition(x="right", y="top")
```

Use Cases:

- Subtitles
- Lower thirds
- Standard video elements
- Quick positioning

## Position Conversion

Mosaico provides utilities to convert between position types:

```python
from mosaico.positioning.utils import convert_position_to_absolute

# Convert any position type to absolute coordinates
absolute_pos = convert_position_to_absolute(
    position=RegionPosition(x="center", y="bottom"),
    frame_size=(1920, 1080)
)
```

## Real-World Examples

### Logo Placement
```python
# Create an image asset with absolute positioning
logo = create_asset(
    "image",
    path="logo.png",
    params=ImageAssetParams(
        position=AbsolutePosition(x=50, y=30)
    )
)
```

### Centered Title
```python
# Create a centered text title
title = create_asset(
    "text",
    data="Welcome",
    params=TextAssetParams(
        position=RelativePosition(x=0.5, y=0.5),
        align="center"
    )
)
```

### Subtitles
```python
# Create subtitles in standard position
subtitle = create_asset(
    "subtitle",
    data="Hello world",
    params=TextAssetParams(
        position=RegionPosition(x="center", y="bottom")
    )
)
```

## Position Validation and Helpers

### Type Checking
```python
from mosaico.positioning.utils import (
    is_absolute_position,
    is_relative_position,
    is_region_position
)

# Check position types
if is_region_position(position):
    # Handle region position
    pass
elif is_relative_position(position):
    # Handle relative position
    pass
elif is_absolute_position(position):
    # Handle absolute position
    pass
```

### Region Position Creation
```python
# Create from string shorthand
position = RegionPosition.from_string("bottom")  # center-bottom
position = RegionPosition.from_string("right")   # right-center
```

## Best Practices

1. **Choosing the Right Position Type**
    - Use Absolute for pixel-perfect requirements
    - Use Relative for resolution-independent layouts
    - Use Region for standard video elements

2. **Resolution Considerations**
    ```python
    # Bad: Hard-coded absolute positions
    position = AbsolutePosition(x=1920, y=1080)

    # Good: Relative positioning for flexibility
    position = RelativePosition(x=1.0, y=1.0)
    ```

3. **Maintainable Layouts**
    ```python
    # Create reusable positions
    LOWER_THIRD_POSITION = RegionPosition(x="left", y="bottom")
    WATERMARK_POSITION = AbsolutePosition(x=50, y=50)
    ```

4. **Dynamic Positioning**
    ```python
    # Adjust position based on content
    def get_title_position(title_length: int) -> Position:
        if title_length > 50:
            return RegionPosition(x="center", y="top")
        return RelativePosition(x=0.5, y=0.3)
    ```

## Conclusion

Understanding and effectively using the positioning system is crucial for creating professional-looking video compositions. The flexibility of having three positioning strategies allows you to handle any layout requirement while maintaining clean and maintainable code.
