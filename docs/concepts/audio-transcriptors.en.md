# Audio Transcriptors

!!! note "Prerequisites"
    - [__Media__](media-and-assets.md#media-objects-raw-materials)
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Video Projects__](video-projects.md)

## Overview

Mosaico provides audio transcriptor components to convert speech into text, which can be used for subtitle generation and content synchronization. The system uses a protocol-based approach allowing different transcriptor services to be integrated through a common interface.

## Audio Transcriptor Protocol

The transcriptor system is built around the `AudioTranscriber` protocol:

```python
from mosaico.audio_transcribers.protocol import AudioTranscriber
from mosaico.assets.audio import AudioAsset
from mosaico.audio_transcribers.transcription import Transcription

class MyTranscriber(AudioTranscriber):
    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        # Implement transcription logic
        ...
```

## Transcription Structure

Transcriptions are represented using the `Transcription` class:

```python
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord

words = [
    TranscriptionWord(
        start_time=0.0,
        end_time=0.5,
        text="Hello"
    ),
    TranscriptionWord(
        start_time=0.6,
        end_time=1.0,
        text="world"
    )
]

transcription = Transcription(words=words)
```

## Using Transcriptors in Projects

Transcriptors can be used to generate subtitles for video projects:

```python
# Create transcriptor
transcriber = MyTranscriber()

# Transcribe audio asset
transcription = transcriber.transcribe(audio_asset)

# Add subtitles from transcription
project = project.add_captions_from_transcriber(
    transcription,
    max_duration=5,  # Maximum subtitle duration
    params=TextAssetParams(
        font_size=36,
        font_color="white"
    )
)
```

## Transcription Formats

### VTT Format
```python
# Convert to WebVTT
vtt_content = transcription.as_vtt()

# Create from VTT
transcription = Transcription.from_vtt(vtt_content)
```

### SRT Format
```python
# Create from SRT
transcription = Transcription.from_srt(srt_content)
```

## Best Practices

### Handling Long Content

- Break long transcriptions into manageable chunks
- Consider memory usage for large files
- Use appropriate subtitle durations

### Timing Synchronization

- Verify audio/subtitle sync
- Handle overlapping speech
- Account for pauses and breaks

### Text Processing

- Clean up transcription text
- Handle punctuation properly
- Format numbers and special characters

## Common Use Cases

### Video Subtitles
```python
# Create news video with transcribed subtitles
project = (
    VideoProject.from_script_generator(news_generator, media_files)
    .add_captions_from_transcriber(
        transcriber,
        max_duration=5,
        params=TextAssetParams(
            font_size=24,
            font_color="yellow"
        )
    )
)
```

### Interview Captioning
```python
# Process interview audio
transcription = transcriber.transcribe(interview_audio)

# Add captions to video
project = project.add_captions(
    transcription,
    params=TextAssetParams(
        position=RegionPosition(x="center", y="bottom")
    )
)
```

### Multi-language Support
```python
# Create subtitles in different languages
for language in languages:
    translated_transcription = translate_transcription(
        transcription,
        target_language=language
    )
    project.add_captions(
        translated_transcription,
        params=subtitle_params[language]
    )
```

## Conclusion

The transcriptor system in Mosaico provides a flexible foundation for adding subtitles and captions to your videos, with support for different formats and processing options.
