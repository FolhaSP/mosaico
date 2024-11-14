# OpenAI

## Overview

Mosaico provides robust integration with OpenAI's services through two main components:

- Speech synthesis using OpenAI's Text-to-Speech API
- Audio transcription using OpenAI's Whisper API

## Speech Synthesis

The `OpenAISpeechSynthesizer` class provides text-to-speech capabilities:

```python
from mosaico.speech_synthesizers.openai import OpenAISpeechSynthesizer

synthesizer = OpenAISpeechSynthesizer(
    api_key="your-api-key",
    model="tts-1",              # or "tts-1-hd" for higher quality
    voice="alloy",              # available: alloy, echo, fable, onyx, nova, shimmer
    speed=1.0                   # 0.25 to 4.0
)

# Generate speech assets
audio_assets = synthesizer.synthesize(
    texts=["Text to convert to speech"],
    audio_params=AudioAssetParams(volume=1.0)
)
```

### Configuration Options

- **Models**:
    - `tts-1`: Standard quality model
    - `tts-1-hd`: High-definition model
- **Voices**:
    - alloy: Neutral and balanced
    - echo: Warm and clear
    - fable: Expressive and dynamic
    - onyx: Deep and authoritative
    - nova: Energetic and bright
    - shimmer: Gentle and welcoming
- **Speed**: Control speech rate from 0.25x to 4.0x

## Audio Transcription

The `OpenAIWhisperTranscriber` class provides speech-to-text capabilities:

```python
from mosaico.audio_transcribers.openai import OpenAIWhisperTranscriber

transcriber = OpenAIWhisperTranscriber(
    api_key="your-api-key",
    model="whisper-1",
    language="en",          # Optional language code
    temperature=0          # Model temperature (0-1)
)

# Transcribe audio
transcription = transcriber.transcribe(audio_asset)
```

### Transcription Features

- Word-level timestamps
- Multiple language support
- Temperature control for model output
- Configurable timeout settings

## Common Integration Patterns

### Speech-to-Text-to-Speech Pipeline
```python
# Create project
project = VideoProject()

# Add audio asset to project
project.add_assets(original_audio)

# Add to scene
scene = Scene(asset_references=[
    AssetReference.from_asset(original_audio)
        .with_start_time(0)
        .with_end_time(original_audio.duration)
])

# Add scene to project
project.add_timeline_events(scene)

# Add captions from transcription
project.add_captions_from_transcriber(transcriber, max_duration=5)

# Add narration in new language
project.add_narration(synthesizer)
```

### Video Subtitling
```python
# Add captions directly from audio
project.add_captions_from_transcriber(
    transcriber,
    max_duration=5,
    params=TextAssetParams(
        font_size=48,
        font_color="white"
    )
)

# Or add captions from existing transcription
project.add_captions(
    transcription,
    max_duration=5,
    scene_index=0  # Add to specific scene
)
```

### Automated Narration
```python
# Generate narration for entire project
project.add_narration(synthesizer)

# Or generate for specific scene
scene_with_narration = scene.with_narration(synthesizer)
project.add_timeline_events(scene_with_narration)
```

The OpenAI integration in Mosaico provides powerful tools for audio processing in video production, enabling automated transcription, translation, and high-quality speech synthesis. The modular design allows for easy integration with other components of the video production pipeline.
