# Efeitos

!!! note "Pré-requisitos"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)
    - [__Asset References__](media-and-assets.md#asset-references)

## Visão Geral

O Sistema de Efeitos do Mosaico fornece uma maneira de adicionar animações dinâmicas e efeitos visuais aos seus elementos de vídeo. Os efeitos podem ser aplicados a qualquer referência de asset e podem ser combinados para criar animações complexas.

## Interface

No núcleo do sistema de efeitos está o protocolo Effect:

```python
from moviepy.Clip import Clip
from typing import Protocol, TypeVar

ClipType = TypeVar("ClipType", bound=Clip)

class Effect(Protocol[ClipType]):
    """Base protocol for all effects."""

    def apply(self, clip: ClipType) -> ClipType:
        """Apply the effect to a clip."""
        ...
```

O usuário pode criar efeitos personalizados implementando o método `apply`. O método `apply` recebe um objeto `Clip` e retorna um objeto `Clip` modificado com o efeito aplicado.

## Efeitos Integrados

O Mosaico fornece um conjunto de efeitos integrados que podem ser usados para criar animações dinâmicas em suas composições de vídeo. Esses efeitos se dividem em duas categorias principais: efeitos de movimento de câmera (pan) e efeitos de escala dinâmica (zoom).

Aqui está uma lista completa dos efeitos disponíveis:

| Efeito | Tipo | Parâmetros | Descrição |
|--------|------|------------|-------------|
| PanLeftEffect | `pan_left` | `zoom_factor: float = 1.1` | Move da direita para a esquerda através do quadro |
| PanRightEffect | `pan_right` | `zoom_factor: float = 1.1` | Move da esquerda para a direita através do quadro |
| PanUpEffect | `pan_up` | `zoom_factor: float = 1.1` | Move de baixo para cima através do quadro |
| PanDownEffect | `pan_down` | `zoom_factor: float = 1.1` | Move de cima para baixo através do quadro |
| ZoomInEffect | `zoom_in` | `start_zoom: float = 1.0`<br>`end_zoom: float = 1.1` | Aproxima o quadro |
| ZoomOutEffect | `zoom_out` | `start_zoom: float = 1.5`<br>`end_zoom: float = 1.4` | Afasta o quadro |

Aqui estão alguns exemplos de como usar esses efeitos:

```python
from mosaico.effects.factory import create_effect

# Pan effect example
pan_right = create_effect(
    "pan_right",
    zoom_factor=1.2
)
image_ref = AssetReference.from_asset(image)\
    .with_effects([pan_right])

# Zoom effect example
zoom_in = create_effect(
    "zoom_in",
    start_zoom=1.0,
    end_zoom=1.3
)
image_ref = AssetReference.from_asset(image)\
    .with_effects([zoom_in])

# Combining pan and zoom
combined_effect = [
    create_effect("pan_right", zoom_factor=1.1),
    create_effect("zoom_in", start_zoom=1.0, end_zoom=1.2)
]
image_ref = AssetReference.from_asset(image)\
    .with_effects(combined_effect)
```

## Criando Efeitos Personalizados

Você pode criar efeitos personalizados implementando o protocolo Effect:

```python
from moviepy.video.VideoClip import VideoClip

class CustomFadeEffect:
    """Custom fade effect implementation."""

    def __init__(self, fade_duration: float = 1.0):
        self.fade_duration = fade_duration

    def apply(self, clip: VideoClip) -> VideoClip:
        """Apply custom fade effect."""
        def modify_frame(t):
            # Custom frame modification logic
            frame = clip.get_frame(t)
            alpha = min(1.0, t / self.fade_duration)
            return frame * alpha

        return clip.fl(modify_frame)
```

## Combinando Efeitos

Os efeitos podem ser combinados para criar animações complexas:

```python
# Create multiple effects
pan_right = create_effect("pan_right")
zoom_in = create_effect("zoom_in")

# Apply both effects to an asset
image_ref = AssetReference.from_asset(image)\
    .with_effects([pan_right, zoom_in])
```

## Exemplos do Mundo Real

### Efeito Ken Burns
```python
# Create a subtle Ken Burns effect
ken_burns = [
    create_effect(
        "zoom_in",
        start_zoom=1.0,
        end_zoom=1.2
    ),
    create_effect("pan_right")
]

# Apply to background image
background_ref = AssetReference.from_asset(background)\
    .with_effects(ken_burns)
```

### Animação de Título
```python
# Create title entrance effect
title_effects = [
    create_effect("zoom_in", start_zoom=0.8, end_zoom=1.0),
    create_effect("pan_up")
]

# Apply to title
title_ref = AssetReference.from_asset(title)\
    .with_effects(title_effects)
```

## Melhores Práticas

1. **Temporização de Efeitos**
```python
# Consider clip duration when setting effect parameters
if clip_duration < 2:
    zoom_factor = 1.1  # Subtle for short clips
else:
    zoom_factor = 1.3  # More dramatic for longer clips
```

2. **Considerações de Desempenho**
```python
# Limit number of simultaneous effects
MAX_EFFECTS = 2

if len(effects) > MAX_EFFECTS:
    warnings.warn("Too many effects may impact performance")
```

3. **Combinações de Efeitos**
```python
# Create reusable effect combinations
def create_entrance_effects():
    return [
        create_effect("zoom_in", start_zoom=0.8),
        create_effect("pan_up")
    ]
```

## Conclusão

O Sistema de Efeitos do Mosaico fornece uma maneira poderosa de adicionar elementos dinâmicos às suas composições de vídeo. Ao entender e usar adequadamente os efeitos, você pode criar vídeos com aparência profissional e elementos visuais envolventes. Seja usando efeitos integrados ou criando personalizados, a flexibilidade do sistema permite produções de vídeo criativas e impactantes.
