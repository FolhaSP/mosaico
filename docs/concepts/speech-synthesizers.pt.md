# Sintetizadores de Voz

!!! note "Pré-requisitos"
    - [__Media__](media-and-assets.md#media-objects-raw-materials)
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Video Projects__](video-projects.md)

## Visão Geral

Os Sintetizadores de Voz no Mosaico são componentes que convertem texto em fala natural para narração de vídeo. O sistema suporta múltiplas implementações de sintetizadores e oferece opções flexíveis de configuração.

## Trabalhando com Sintetizadores

```python
from mosaico.speech_synthesizers import OpenAISpeechSynthesizer

# Create synthesizer with configuration
tts = OpenAISpeechSynthesizer(
    model="tts-1",              # TTS model to use
    voice="alloy",              # Voice selection
    speed=1.0,                  # Speech speed
    api_key="your_api_key"      # Optional API key
)

# Generate speech
audio_assets = tts.synthesize(
    texts=["Welcome to our video", "This is a demo"],
    audio_params=AudioAssetParams(volume=0.8)
)
```

## Integração com Projetos de Vídeo

### Integração Básica
```python
# Create project with speech
project = (
    VideoProject.from_script_generator(
        script_generator=generator,
        media=media_files,
    )
    .add_narration(tts_engine)
)
```

### Adição Manual de Fala
```python
# Generate speech for specific text
speech_asset = tts.synthesize(["Welcome message"])[0]

# Add to project
project = (
    project
    .add_assets(speech_asset)
    .add_timeline_events(
        AssetReference.from_asset(speech_asset)
            .with_start_time(0)
            .with_end_time(speech_asset.duration)
    )
)
```

## Parâmetros Personalizados de Fala

### Configuração de Áudio
```python
# Configure audio parameters
params = AudioAssetParams(
    volume=0.8,         # Set volume level
    crop=(0, 30)       # Use specific segment
)

# Generate with parameters
assets = tts.synthesize(
    texts=["Narration text"],
    audio_params=params
)
```

### Personalização de Voz
```python
# OpenAI customization
openai_tts = OpenAISpeechSynthesizer(
    model="tts-1-hd",    # High-definition model
    voice="nova",        # Different voice
    speed=1.2           # Faster speech
)

# ElevenLabs customization
elevenlabs_tts = ElevenLabsSpeechSynthesizer(
    voice_id="custom_voice",
    voice_stability=0.7,
    voice_similarity_boost=0.8,
    voice_speaker_boost=True
)
```

## Casos de Uso Comuns

### Narração de Vídeo
```python
# Generate news narration
news_tts = OpenAISpeechSynthesizer(
    voice="nova",     # Clear, professional voice
    speed=1.1        # Slightly faster for news
)

narration = news_tts.synthesize(
    [shot.subtitle for shot in news_script.shots]
)
```

### Voz para Tutorial
```python
# Tutorial narration with pauses
tutorial_tts = ElevenLabsSpeechSynthesizer(
    voice_id="tutorial_voice",
    voice_stability=0.8,    # More consistent
    voice_style=0.3        # Less emotional
)

# Add pauses between steps
tutorial_texts = [f"{text}..." for text in tutorial_steps]
tutorial_audio = tutorial_tts.synthesize(tutorial_texts)
```

### Suporte Multi-Idioma
```python
# Create synthesizers for different languages
tts_en = OpenAISpeechSynthesizer(language_code="en")
tts_es = OpenAISpeechSynthesizer(language_code="es")
tts_fr = OpenAISpeechSynthesizer(language_code="fr")

# Generate multi-language audio
audio_en = tts_en.synthesize(texts_en)
audio_es = tts_es.synthesize(texts_es)
audio_fr = tts_fr.synthesize(texts_fr)
```

## Conclusão

Entender os sintetizadores de voz no Mosaico permite a criação de narrações de qualidade profissional para vários tipos de vídeo. O sistema flexível de sintetizadores e as opções de configuração permitem uma saída de voz personalizada adequada para diferentes necessidades de conteúdo.
