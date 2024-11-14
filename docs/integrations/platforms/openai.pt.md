# OpenAI

## Visão Geral

O Mosaico fornece integração robusta com os serviços da OpenAI através de dois componentes principais:

- Síntese de voz usando a API Text-to-Speech da OpenAI
- Transcrição de áudio usando a API Whisper da OpenAI

## Síntese de Voz

A classe `OpenAISpeechSynthesizer` fornece recursos de texto para voz:

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

### Opções de Configuração

- **Modelos**:
    - `tts-1`: Modelo de qualidade padrão
    - `tts-1-hd`: Modelo de alta definição
- **Vozes**:
    - alloy: Neutra e equilibrada
    - echo: Quente e clara
    - fable: Expressiva e dinâmica
    - onyx: Profunda e autoritária
    - nova: Energética e brilhante
    - shimmer: Suave e acolhedora
- **Velocidade**: Controle a taxa de fala de 0.25x a 4.0x

## Transcrição de Áudio

A classe `OpenAIWhisperTranscriber` fornece recursos de fala para texto:

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

### Recursos de Transcrição

- Timestamps em nível de palavra
- Suporte a múltiplos idiomas
- Controle de temperatura do modelo
- Configurações ajustáveis de timeout

## Padrões Comuns de Integração

### Pipeline de Fala-para-Texto-para-Fala
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

### Legendagem de Vídeo
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

### Narração Automatizada
```python
# Generate narration for entire project
project.add_narration(synthesizer)

# Or generate for specific scene
scene_with_narration = scene.with_narration(synthesizer)
project.add_timeline_events(scene_with_narration)
```

A integração OpenAI no Mosaico fornece ferramentas poderosas para processamento de áudio na produção de vídeos, permitindo transcrição automatizada, tradução e síntese de voz de alta qualidade. O design modular permite fácil integração com outros componentes do pipeline de produção de vídeo.
