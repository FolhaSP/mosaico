# ElevenLabs

## Overview

Mosaico integrates with ElevenLabs' text-to-speech API through the `ElevenLabsSpeechSynthesizer` class, providing high-quality voice synthesis for video narration. This integration supports multiple languages, voice customization, and batch processing of text.

## Configuration

```python
from mosaico.speech_synthesizers import ElevenLabsSpeechSynthesizer

synthesizer = ElevenLabsSpeechSynthesizer(
    api_key="your-api-key",            # ElevenLabs API key
    voice_id="voice-id",               # Selected voice ID
    model="eleven_multilingual_v2",    # Model to use
    language_code="en",                # Language code

    # Voice customization
    voice_stability=0.5,               # Voice consistency (0-1)
    voice_similarity_boost=0.5,        # Voice matching accuracy (0-1)
    voice_style=0.5,                   # Style intensity (0-1)
    voice_speaker_boost=True           # Enhanced speaker clarity
)
```

## Supported Models

- `eleven_turbo_v2_5` - Latest turbo model
- `eleven_turbo_v2` - Fast synthesis model
- `eleven_multilingual_v2` - Multi-language support
- `eleven_monolingual_v1` - English-only model
- `eleven_multilingual_v1` - Legacy multi-language

## Voice Synthesis

### Basic Usage
```python
# Generate audio assets from text
audio_assets = synthesizer.synthesize(
    texts=["Hello world", "Welcome to Mosaico"]
)

# Use in video project
project.add_assets(audio_assets)
```

### With Custom Parameters
```python
from mosaico.assets.audio import AudioAssetParams

# Configure audio parameters
audio_params = AudioAssetParams(
    volume=0.8,
    crop=(0, 10)  # Crop first 10 seconds
)

# Generate audio with parameters
audio_assets = synthesizer.synthesize(
    texts=["Narration text"],
    audio_params=audio_params
)
```

## Advanced Features

### Context Awareness
The synthesizer maintains context between consecutive text segments for natural flow:

```python
texts = [
    "This is the first sentence.",
    "This is the second sentence.",
    "This is the final sentence."
]

# Each segment will be synthesized with awareness of surrounding text
audio_assets = synthesizer.synthesize(texts)
```

### Voice Customization
Fine-tune voice characteristics:

```python
synthesizer = ElevenLabsSpeechSynthesizer(
    voice_id="voice-id",
    voice_stability=0.8,        # More consistent voice
    voice_similarity_boost=0.7, # Higher accuracy
    voice_style=0.6,           # Stronger style
    voice_speaker_boost=True    # Enhanced clarity
)
```

## Integration with Video Projects

```python
from mosaico.video.project import VideoProject

# Create project from script generator
project = VideoProject.from_script_generator(
    script_generator=news_generator,
    media=media_files
)

# Add narration to scenes with subtitles
project.add_narration(synthesizer)

# Or add specific narration
scene = project.get_timeline_event(0)
narration_assets = synthesizer.synthesize([scene.subtitle])
project.add_assets(narration_assets)
```

The ElevenLabs integration enables high-quality voice synthesis for your video projects, with extensive customization options and multi-language support. The integration handles context awareness and provides seamless incorporation into the Mosaico video production workflow.
