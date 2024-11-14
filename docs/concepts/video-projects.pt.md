# Projetos de Vídeo

!!! note "Pré-requisitos"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Referências de Asset__](asset-references-and-scenes.md#asset-references)
    - [__Cenas__](asset-references-and-scenes.md#scenes)
    - [__Geradores de Script__](script-generators.md)

## Visão Geral

Um projeto de vídeo no Mosaico representa uma composição completa de vídeo que consiste em três componentes principais:

**Configuração do Projeto**

- Metadados básicos e configurações do projeto
- Especificações de saída do vídeo
- Parâmetros técnicos

**Coleção de Assets**

- Registro de todos os elementos de mídia
- Mapeamento entre IDs de assets e objetos
- Validação e gerenciamento de assets

**Linha do Tempo**

- Sequência de eventos (cenas e referências de assets)
- Sincronização de tempo
- Organização de eventos

## Configuração do Projeto

Um vídeo pode ser configurado com um conjunto específico de parâmetros que definem sua aparência e comportamento. A classe `VideoProjectConfig` define as configurações básicas para seu vídeo:

```python
from mosaico.video.project import VideoProjectConfig

config = VideoProjectConfig(
    name="My Project",          # Project name
    version=1,                  # Project version
    resolution=(1920, 1080),    # Video dimensions
    fps=30                      # Frames per second
)
```

Por exemplo, para alterar a resolução do projeto, basta atualizar o atributo `resolution`...

```python
config.resolution = (1280, 720)
```

... e pronto: o projeto de vídeo será renderizado na nova resolução.

## Criando Projetos de Vídeo

Existem três maneiras principais de criar um projeto de vídeo:

### Criação Direta

O usuário já conhece a estrutura do projeto, a configuração dos assets e sua disposição na linha do tempo. Neste caso, o projeto pode ser criado diretamente:

```python
from mosaico.video.project import VideoProject

project = VideoProject(
    config=VideoProjectConfig(
        name="Direct Creation Example",
        resolution=(1920, 1080)
    )
)
```

### Geração Baseada em Script

O usuário deseja gerar um projeto de vídeo baseado em um script que define a estrutura do projeto. O script pode ser gerado por um gerador de script, que é uma classe que implementa o protocolo [`ScriptGenerator`](../api_reference/script-generators/index.md):

!!! note "Sobre Geradores de Script"
    Eles são a principal ponte entre projetos de vídeo e IA. O protocolo [`ScriptGenerator`](../api_reference/script-generators/index.md) está no centro do processo de geração de projetos de vídeo, pois define a estrutura do script que será usado para criar o projeto de vídeo e evita que o usuário tenha que definir manualmente a estrutura do projeto.

```python
project = VideoProject.from_script_generator(
    script_generator=script_generator,  # ScriptGenerator instance
    media=media_files,                  # Sequence of Media objects
    config=video_config,                # Optional configuration
    speech_synthesizer=tts_engine,      # Optional speech synthesis
    audio_transcriber=transcriber,      # Optional transcription
    background_audio=bg_music           # Optional background music
)
```

### Carregando de Arquivo

Uma das principais características do Mosaico é a capacidade de serializar e desserializar projetos de vídeo para e de arquivos. Isso permite que os usuários salvem seus projetos e os carreguem posteriormente, ou os compartilhem com outros.

Baseado no formato YAML, a classe [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) fornece métodos para carregar e salvar projetos:

```python
# Load from YAML
project = VideoProject.from_file("project.yml")

# Save to YAML
project.to_file("project.yml")
```

## Gerenciando Assets do Projeto

O [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) fornece métodos para gerenciar assets, como adicionar, remover e recuperá-los. A classe é responsável por garantir que todos os assets estejam corretamente vinculados ao projeto, tenham referências válidas na linha do tempo e estejam disponíveis quando necessário.

### Adicionando Assets
```python
# Add single asset
project.add_assets(background_image)

# Add multiple assets
project.add_assets([
    main_video,
    background_music,
    subtitle_text
])

# Add with custom IDs
project.add_assets({
    "background": background_image,
    "music": background_music
})
```

### Recuperando Assets
```python
# Get asset by ID
asset = project.get_asset("background")
```

### Removendo Assets
```python
# Remove asset
# This will also remove all references to the asset in the timeline
project.remove_asset("background")
```

## Gerenciamento da Linha do Tempo

A linha do tempo consiste em eventos (cenas e referências de assets) que definem quando e como os assets aparecem no vídeo.

### Adicionando Eventos na Linha do Tempo
```python
# Add a scene
project.add_timeline_events(
    Scene(
        title="Opening Scene",
        asset_references=[
            AssetReference.from_asset(background)
                .with_start_time(0)
                .with_end_time(5),
            AssetReference.from_asset(title_text)
                .with_start_time(1)
                .with_end_time(4)
        ]
    )
)

# Add individual asset reference
project.add_timeline_events(
    AssetReference.from_asset(background_music)
        .with_start_time(0)
        .with_end_time(project.duration)
)
```

### Removendo Eventos da Linha do Tempo
```python
# Remove event by index
project.remove_timeline_event(0)
```

### Navegação na Linha do Tempo
```python
# Get total duration
duration = project.duration

# Get specific event
event = project.get_timeline_event(0)

# Iterate through timeline
for event in project.iter_timeline():
    print(f"Event at {event.start_time}s")
```

## Recursos Especiais

Aqui estão alguns recursos especiais que o Mosaico oferece para aprimorar projetos de vídeo:

### Geração de Legendas

```python
# Add subtitles from transcription
project.add_subtitles_from_transcription(
    transcription=transcription,
    max_duration=5,  # Maximum subtitle duration
    params=TextAssetParams(
        font_size=36,
        font_color="white"
    )
)
```

### Atualização em Lote de Parâmetros de Legendas

```python
# Update subtitle parameters globally
project.with_subtitle_params(
    TextAssetParams(
        font_size=48,
        stroke_width=2
    )
)
```

## Encadeamento de Métodos

A classe [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) suporta encadeamento de métodos, o que permite chamar vários métodos em um objeto em uma única linha. Isso pode tornar seu código mais conciso e fácil de ler.

```python
project = (
    VideoProject(config=VideoProjectConfig())
    .add_assets([background_image, title_text, background_music])
    .add_timeline_events([
        AssetReference.from_asset(background_image)
            .with_start_time(0)
            .with_end_time(10),
        AssetReference.from_asset(title_text)
            .with_start_time(1)
            .with_end_time(9)
    ])
)
```

## Melhores Práticas

**Organização de Assets**

- Use IDs significativos para assets
- Agrupe assets relacionados
- Mantenha o controle das dependências dos assets

**Estrutura da Linha do Tempo**

- Organize eventos cronologicamente
- Use cenas para conteúdo relacionado
- Mantenha relações claras de tempo

**Gerenciamento de Projetos**

- Salve projetos regularmente
- Use controle de versão para arquivos do projeto
- Documente a estrutura do projeto

## Conclusão

Esta documentação reflete a implementação atual do [`VideoProject`](../api_reference/video/project.md#mosaico.video.project.VideoProject) no Mosaico, focando em padrões práticos de uso e melhores práticas. Os exemplos são projetados para funcionar com o código atual e demonstrar fluxos de trabalho comuns de produção de vídeo.
