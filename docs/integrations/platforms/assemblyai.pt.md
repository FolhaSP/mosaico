# AssemblyAI

## Visão Geral

A integração do AssemblyAI no Mosaico fornece recursos automatizados de transcrição de fala para texto para ativos de áudio. Essa integração permite transcrição precisa com temporização em nível de palavra, essencial para geração de legendas e sincronização de conteúdo.

## Requisitos

- Pacote Python AssemblyAI (`pip install assemblyai`)
- Chave de API válida do AssemblyAI
- Áudio em formato suportado (MP3, WAV, etc.)

## Uso

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

## Opções de Configuração

O `AssemblyAIAudioTranscriber` suporta várias opções de configuração:

- `api_key`: Sua chave de API do AssemblyAI (obrigatório)
- `model`: Modelo de transcrição a ser usado (`best` ou `nano`)
- `language`: Especificação opcional de idioma
- `custom_spelling`: Dicionário de correções ortográficas personalizadas

## Recursos

### Detecção de Idioma
```python
# Automatic language detection
transcriber = AssemblyAIAudioTranscriber(
    api_key="your_api_key",
    language=None  # Enables automatic detection
)
```

### Ortografia Personalizada
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

## Integração com Projetos de Vídeo

A transcrição pode ser usada de várias maneiras com projetos de vídeo:

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
