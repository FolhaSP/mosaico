# Geradores de Script

!!! note "Pré-requisitos"
    - [__Mídia__](media-and-assets.md#media-objects-raw-materials)
    - [__Sintetizadores de Fala__](speech-synthesis.md)

## Visão Geral

Os Geradores de Script no Mosaico fornecem uma maneira automatizada de criar roteiros de vídeo a partir de coleções de mídia. São particularmente úteis para converter conteúdo como artigos de notícias em roteiros de vídeo estruturados que podem ser usados para gerar projetos de vídeo completos.

## Sistema de Geração de Script

O sistema consiste em três componentes principais:

1. **Protocolo do Gerador de Script**: Define a interface para geradores de script
2. **Roteiro de Filmagem**: Representa a saída estruturada gerada pelo gerador de script
3. **Tomada**: Representa segmentos individuais do script

## O Protocolo [`ScriptGenerator`](../api_reference/script-generators/index.md)

Características principais:

- Protocolo verificável em tempo de execução
- Manipulação flexível de entrada
- Formato de saída padronizado
- Design extensível

```python
from mosaico.script_generators.protocol import ScriptGenerator
from mosaico.media import Media

@runtime_checkable
class ScriptGenerator(Protocol):
    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """Generate a shooting script from media."""
        ...
```

## Roteiros de Filmagem

Um [`ShootingScript`](../api_reference/script-generators/script.md) representa um roteiro de vídeo completo com múltiplas tomadas. A ideia é fornecer um formato estruturado que pode ser usado para gerar projetos de vídeo. O formato do roteiro de filmagem foi escolhido para ser simples e flexível, mantendo os elementos essenciais de um roteiro de vídeo.

Os principais componentes de um roteiro de filmagem são:

- __Título__: O título do roteiro
- __Descrição__: Uma descrição opcional do conteúdo do roteiro
- __Tomadas__: Coleção de tomadas que compõem o roteiro

Estes componentes fornecem uma visão geral do conteúdo do vídeo e dos segmentos individuais que serão incluídos no vídeo final.

## Tomadas

Tomadas individuais representam segmentos distintos no roteiro que podem ser usados para criar projetos de vídeo. Cada tomada tem as seguintes propriedades:

- __Número__: Um identificador único para a tomada
- __Descrição__: Uma breve descrição do conteúdo da tomada
- __Tempo Inicial__: O tempo de início da tomada no vídeo
- __Tempo Final__: O tempo final da tomada no vídeo
- __Legenda__: Legendas opcionais para a tomada
- __Referências de Mídia__: Referências à mídia usada na tomada
- __Efeitos__: Efeitos opcionais aplicados à tomada

!!! warning
    __Referências de mídia__ não são objetos como `AssetReference`, mas sim strings simples que podem ser usadas para identificar objetos de mídia em uma lista de mídia. Não devem ser confundidas com objetos de mídia reais ou objetos `AssetReference`.

## Usando Geradores de Script

### Geração Básica de Script
```python
# Create generator
generator = MyVideoScriptGenerator(
    context="News article content...",
    num_paragraphs=10
)

# Generate script from media
script = generator.generate(
    media=[
        image1_media,
        image2_media,
        video_media
    ]
)
```

### Criando Projetos de Vídeo
```python
from mosaico.video.project import VideoProject

# Generate project from script
project = VideoProject.from_script_generator(
    script_generator=generator,
    media=media_files,
    speech_synthesizer=tts_engine,
    audio_transcriber=transcriber
)
```

### Gerador de Script Personalizado
```python
class CustomScriptGenerator:
    """Custom implementation of ScriptGenerator."""

    def generate(self,
                media: Sequence[Media],
                **kwargs: Any) -> ShootingScript:
        # Custom script generation logic
        shots = [
            Shot(
                number=1,
                description="Opening shot",
                start_time=0,
                end_time=5,
                subtitle="Welcome",
                media_references=[0],
                effects=["zoom_in"]
            )
        ]

        return ShootingScript(
            title="Custom Video",
            shots=shots
        )
```

## Melhores Práticas

**Organização de Mídia**

- Fornecer descrições claras de mídia
- Ordenar mídia logicamente
- Incluir metadados relevantes

**Gerenciamento de Tomadas**

- Manter tomadas focadas e concisas
- Garantir transições lógicas
- Combinar mídia com conteúdo

## Trabalhando com Scripts Gerados

### Análise de Script
```python
# Analyze generated script
print(f"Script duration: {script.duration}s")
print(f"Number of shots: {script.shot_count}")

for shot in script.shots:
    print(f"Shot {shot.number}: {shot.duration}s")
    print(f"Media used: {shot.media_references}")
```

### Validação de Script
```python
def validate_script(script: ShootingScript) -> bool:
    """Validate script properties."""
    if script.duration > max_duration:
        return False

    if not all(shot.subtitle for shot in script.shots):
        return False

    return True
```

### Verificação de Referências de Mídia
```python
def check_media_references(
    script: ShootingScript,
    media: Sequence[Media]
) -> bool:
    """Verify all media references are valid."""
    media_count = len(media)

    for shot in script.shots:
        if any(ref >= media_count for ref in shot.media_references):
            return False

    return True
```

## Integração com Outros Componentes

### Síntese de Fala
```python
# Generate speech for subtitles
speech_assets = speech_synthesizer.synthesize(
    [shot.subtitle for shot in script.shots]
)
```

### Aplicação de Efeitos
```python
# Apply effects from script
for shot in script.shots:
    effects = [create_effect(effect) for effect in shot.effects]
    # Apply to corresponding assets
```

## Conclusão

Entender os geradores de script é crucial para a produção automatizada de vídeo no Mosaico. Eles fornecem uma ponte entre conteúdo bruto e projetos de vídeo estruturados, permitindo uma transformação eficiente do conteúdo enquanto mantêm o controle criativo e os padrões de qualidade.
