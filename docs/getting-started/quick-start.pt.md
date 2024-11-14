# Início rápido

## Criando Assets

=== "From factory function"

    ```python
    from mosaico.assets import create_asset

    # Create an image asset
    image = create_asset("image", path="background.jpg")

    # Create a text asset
    text = create_asset("text", data="Hello World")

    # Create an audio asset
    audio = create_asset("audio", path="narration.mp3")
    ```

    O `create_asset()` cria tipos diferentes de assets:

    - Cada tipo de asset requer um identificador unico ("image", "audio", "text", "subtitle")
    - Os ativos podem ser criados a partir de arquivos usando `path` ou dados diretos usando `data`
    - Os ativos detectam automaticamente propriedades como dimensões, duração, etc.

=== "From asset classes"

      ```python
      from mosaico.assets import ImageAsset, TextAsset, AudioAsset

      # Create an image asset
      image = ImageAsset.from_path("background.jpg")

      # Create a text asset
      text = TextAsset.from_data("Hello World")

      # Create an audio asset
      audio = AudioAsset.from_path("narration.mp3")
      ```

      Alternativamente, os ativos podem ser criados diretamente usando suas respectivas classes:

      - Cada classe de ativos tem propriedades e métodos específicos
      - Os ativos podem ser criados a partir de arquivos usando `from_path()` ou dados diretos usando `from_data()`
      - Os ativos detectam automaticamente propriedades como dimensões, duração, etc.


## Criando referências de assets

```python
from mosaico.assets.reference import AssetReference

# Create reference for background image
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)

# Create reference for text overlay
text_ref = AssetReference.from_asset(text).with_start_time(1).with_end_time(4)

# Create reference for audio narration
audio_ref = AssetReference.from_asset(audio).with_start_time(0).with_end_time(5)
```

As referências de ativos determinam quando e como os ativos aparecem no vídeo:

- `from_asset()` cria uma referência a partir de um ativo
- `with_start_time()` define quando o ativo aparece
- `with_end_time()` define quando o ativo desaparece
- Os tempos estão em segundos
- As referências também podem incluir efeitos e parâmetros personalizados

## Criando uma cena

```python
from mosaico.scene import Scene

# Create a scene containing the assets
scene = Scene(asset_references=[image_ref, text_ref, audio_ref])
```

Cenas agrupam ativos relacionados:

- Pega uma lista de referências de ativos
- Lida com tempo e sincronização
- Pode incluir título e descrição
- Várias cenas podem ser combinadas em um projeto

## Criando um Projeto Completo

```python
from mosaico.video.project import VideoProject, VideoProjectConfig

# Create project configuration
config = VideoProjectConfig(
    name="My First Video",
    resolution=(1920, 1080),
    fps=30
)

# Create, configure and add assets and scene to the project
project = (
    VideoProject(config=config)
    .add_assets([image, text, audio])
    .add_timeline_events(scene)
)
```

O `VideoProject` une tudo:

- Configurar as configurações do projeto, como resolução e taxa de quadros
- Adicione todos os ativos usados ​​no vídeo
- Adicionar cenas à linha do tempo
- Gerencia a composição completa do vídeo

## Exportar o Projeto de Vídeo

O projeto pode ser exportado para um arquivo YAML:

```python
project.to_file("my_first_video.yml")
```

## Opcional: Adicionando efeitos

```python
from mosaico.effects.factory import create_effect

# Create a zoom effect
zoom_effect = create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)

# Add effect to text reference
text_ref = text_ref.with_effects([zoom_effect])
```

Efeitos podem ser adicionados às referências de Assets:

- Vários efeitos integrados (zoom, pan)
- Os efeitos têm parâmetros configuráveis
- Vários efeitos podem ser combinados
- Os efeitos são aplicados durante a renderização

## Exemplo completo

```python
from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.effects.factory import create_effect

# 1. Create assets
image = create_asset("image", path="background.jpg")
text = create_asset("text", data="Hello World")
audio = create_asset("audio", path="narration.mp3")

# 2. Create effect
zoom_effect = create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)

# 3. Create asset references with timing
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)
text_ref = (
    AssetReference.from_asset(text)
    .with_start_time(1)
    .with_end_time(4)
    .with_effects([zoom_effect])
)
audio_ref = AssetReference.from_asset(audio).with_start_time(0).with_end_time(5)

# 4. Create scene
scene = Scene(
    title="Opening Scene",
    asset_references=[image_ref, text_ref, audio_ref]
)

# 5. Create, configure and add assets and events to the project
project = (
    VideoProject(
        config=VideoProjectConfig(
            name="My First Video",
            resolution=(1920, 1080),
            fps=30
        )
    )
    .add_assets([image, text, audio])
    .add_timeline_events(scene)
)

# 6. Save project
project.to_file("my_video.yml")
```

Isso cria um vídeo de 5 segundos com:

- Uma imagem de fundo
- Texto que aparece aos 1s com um efeito de zoom
- Narração em áudio durante todo o vídeo
- Resolução HD a 30fps

O projeto pode ser salvo em um arquivo YAML para edição ou renderização posterior.
