# Transcrição de Áudio

!!! note "Pré-requisitos"
    - [__Media__](media-and-assets.md#media-objects-raw-materials)
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Video Projects__](video-projects.md)

## Visão Geral

O Mosaico fornece componentes de transcrição de áudio para converter fala em texto, que podem ser usados para geração de legendas e sincronização de conteúdo. O sistema usa uma abordagem baseada em protocolo permitindo que diferentes serviços de transcrição sejam integrados através de uma interface comum.

## Protocolo de Transcrição de Áudio

O sistema de transcrição é construído em torno do protocolo `AudioTranscriber`:

```python
from mosaico.audio_transcribers.protocol import AudioTranscriber
from mosaico.assets.audio import AudioAsset
from mosaico.audio_transcribers.transcription import Transcription

class MyTranscriber(AudioTranscriber):
    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        # Implement transcription logic
        ...
```

## Estrutura de Transcrição

As transcrições são representadas usando a classe `Transcription`:

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

## Usando Transcrições em Projetos

Transcritores podem ser usados para gerar legendas para projetos de vídeo:

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

## Formatos de Transcrição

### Formato VTT
```python
# Convert to WebVTT
vtt_content = transcription.as_vtt()

# Create from VTT
transcription = Transcription.from_vtt(vtt_content)
```

### Formato SRT
```python
# Create from SRT
transcription = Transcription.from_srt(srt_content)
```

## Melhores Práticas

### Lidando com Conteúdo Longo

- Dividir transcrições longas em partes gerenciáveis
- Considerar o uso de memória para arquivos grandes
- Usar durações apropriadas para legendas

### Sincronização de Tempo

- Verificar sincronização de áudio/legendas
- Lidar com falas sobrepostas
- Considerar pausas e intervalos

### Processamento de Texto

- Limpar o texto da transcrição
- Lidar corretamente com pontuação
- Formatar números e caracteres especiais

## Casos de Uso Comuns

### Legendas de Vídeo
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

### Legendagem de Entrevistas
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

### Suporte Multi-idioma
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

## Conclusão

O sistema de transcrição no Mosaico fornece uma base flexível para adicionar legendas aos seus vídeos, com suporte para diferentes formatos e opções de processamento.
