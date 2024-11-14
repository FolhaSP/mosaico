# ElevenLabs

## Visão Geral

O Mosaico integra-se com a API de texto para fala da ElevenLabs através da classe `ElevenLabsSpeechSynthesizer`, fornecendo síntese de voz de alta qualidade para narração de vídeo. Esta integração suporta múltiplos idiomas, personalização de voz e processamento em lote de texto.

## Configuração

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

## Modelos Suportados

- `eleven_turbo_v2_5` - Modelo turbo mais recente
- `eleven_turbo_v2` - Modelo de síntese rápida
- `eleven_multilingual_v2` - Suporte multi-idiomas
- `eleven_monolingual_v1` - Modelo apenas em inglês
- `eleven_multilingual_v1` - Multi-idiomas legado

## Síntese de Voz

### Uso Básico
```python
# Generate audio assets from text
audio_assets = synthesizer.synthesize(
    texts=["Hello world", "Welcome to Mosaico"]
)

# Use in video project
project.add_assets(audio_assets)
```

### Com Parâmetros Personalizados
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

## Recursos Avançados

### Consciência de Contexto
O sintetizador mantém o contexto entre segmentos de texto consecutivos para um fluxo natural:

```python
texts = [
    "This is the first sentence.",
    "This is the second sentence.",
    "This is the final sentence."
]

# Each segment will be synthesized with awareness of surrounding text
audio_assets = synthesizer.synthesize(texts)
```

### Personalização de Voz
Ajuste fino das características da voz:

```python
synthesizer = ElevenLabsSpeechSynthesizer(
    voice_id="voice-id",
    voice_stability=0.8,        # More consistent voice
    voice_similarity_boost=0.7, # Higher accuracy
    voice_style=0.6,           # Stronger style
    voice_speaker_boost=True    # Enhanced clarity
)
```

## Integração com Projetos de Vídeo

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

A integração com ElevenLabs permite síntese de voz de alta qualidade para seus projetos de vídeo, com extensas opções de personalização e suporte multi-idiomas. A integração gerencia a consciência de contexto e fornece incorporação perfeita no fluxo de trabalho de produção de vídeo do Mosaico.
