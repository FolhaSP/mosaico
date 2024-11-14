# AssemblyAI

## Overview

AssemblyAI integration in Mosaico provides automated speech-to-text transcription capabilities for audio assets. This integration enables accurate transcription with word-level timing, which is essential for subtitle generation and content synchronization.

## Requirements

- AssemblyAI Python package (`pip install assemblyai`)
- Valid AssemblyAI API key
- Audio in a supported format (MP3, WAV, etc.)

## Usage

```python
from mosaico.audio_transcribers import AssemblyAIAudioTranscriber
from mosaico.assets.audio import AudioAsset
from mosaico.video.project import VideoProject

# Initialize transcriber
transcriber = AssemblyAIAudioTranscriber(
    api_key="your_api_key",
    model="best",  # or "nano" for faster processing
    language="en"  # optional language specification
)

# Create audio asset
audio = AudioAsset.from_path("narration.mp3")

# Transcribe audio
transcription = transcriber.transcribe(audio)

# Access transcription results
for word in transcription.words:
    print(f"{word.text}: {word.start_time} - {word.end_time}")
```

## Configuration Options

The `AssemblyAIAudioTranscriber` supports several configuration options:

- `api_key`: Your AssemblyAI API key (required)
- `model`: Transcription model to use (`best` or `nano`)
- `language`: Optional language specification
- `custom_spelling`: Dictionary of custom spelling corrections

## Features

### Language Detection
```python
# Automatic language detection
transcriber = AssemblyAIAudioTranscriber(
    api_key="your_api_key",
    language=None  # Enables automatic detection
)
```

### Custom Spelling
```python
# Add custom spelling corrections
transcriber = AssemblyAIAudioTranscriber(
    api_key="your_api_key",
    custom_spelling={
        "mosaico": "Mosaico",
        "ai": ["AI", "A.I."]
    }
)
```

## Integration with Video Projects

The transcription can be used in multiple ways with video projects:

```python
# Create video project
project = VideoProject()

# Add audio asset
project.add_assets(audio_asset)

# Add captions from transcriber
project = project.add_captions_from_transcriber(
    transcriber,
    max_duration=5,  # Maximum subtitle duration
    params=TextAssetParams(
        font_size=36,
        font_color="white"
    ),
    overwrite=False  # Don't overwrite existing captions
)

# Or manually add captions from transcription
project = project.add_captions(
    transcription,
    max_duration=5,
    params=TextAssetParams(
        font_size=36,
        font_color="white"
    ),
    scene_index=0,  # Add to specific scene
    overwrite=True  # Replace existing captions
)
```
