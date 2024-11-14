# Sistema de Posicionamento

!!! note "Pré-requisitos"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)

## Visão Geral

O Sistema de Posicionamento no Mosaico fornece uma maneira flexível de posicionar elementos visuais (como imagens e texto) em sua composição de vídeo. Ele oferece três estratégias distintas de posicionamento, cada uma adequada para diferentes casos de uso.

## Tipos de Posicionamento

### Posicionamento Absoluto (Baseado em Pixels)
Posicionamento preciso usando coordenadas exatas em pixels a partir do canto superior esquerdo do quadro.

```python
from mosaico.positioning import AbsolutePosition

class AbsolutePosition:
    type: Literal["absolute"] = "absolute"
    x: NonNegativeInt = 0          # Pixels from left
    y: NonNegativeInt = 0          # Pixels from top
```

Exemplo de Uso:
```python
# Position an element 100 pixels from left, 50 from top
logo_position = AbsolutePosition(x=100, y=50)
```

### Posicionamento Relativo (Baseado em Porcentagem)
Posiciona elementos usando porcentagens das dimensões do quadro.

```python
from mosaico.positioning import RelativePosition

class RelativePosition:
    type: Literal["relative"] = "relative"
    x: NonNegativeFloat = 0.5      # 0.0 to 1.0 (left to right)
    y: NonNegativeFloat = 0.5      # 0.0 to 1.0 (top to bottom)
```

Exemplo de Uso:
```python
# Center an element (50% from left and top)
centered_position = RelativePosition(x=0.5, y=0.5)

# Position at bottom-right corner
corner_position = RelativePosition(x=1.0, y=1.0)
```

Casos de Uso:

- Layouts responsivos
- Posicionamento independente de resolução
- Composições dinâmicas
- Designs adaptáveis

### Posicionamento por Região (Regiões Nomeadas)
Posiciona elementos usando regiões predefinidas do quadro.

```python
from mosaico.positioning import RegionPosition

class RegionPosition:
    type: Literal["region"] = "region"
    x: Literal["left", "center", "right"] = "center"
    y: Literal["top", "center", "bottom"] = "center"
```

Exemplo de Uso:
```python
# Position in bottom-center (typical for subtitles)
subtitle_position = RegionPosition(x="center", y="bottom")

# Position in top-right corner
title_position = RegionPosition(x="right", y="top")
```

Casos de Uso:

- Legendas
- Lower thirds
- Elementos padrão de vídeo
- Posicionamento rápido

## Conversão de Posição

O Mosaico fornece utilitários para converter entre tipos de posição:

```python
from mosaico.positioning.utils import convert_position_to_absolute

# Convert any position type to absolute coordinates
absolute_pos = convert_position_to_absolute(
    position=RegionPosition(x="center", y="bottom"),
    frame_size=(1920, 1080)
)
```

## Exemplos Práticos

### Posicionamento de Logo
```python
# Create an image asset with absolute positioning
logo = create_asset(
    "image",
    path="logo.png",
    params=ImageAssetParams(
        position=AbsolutePosition(x=50, y=30)
    )
)
```

### Título Centralizado
```python
# Create a centered text title
title = create_asset(
    "text",
    data="Welcome",
    params=TextAssetParams(
        position=RelativePosition(x=0.5, y=0.5),
        align="center"
    )
)
```

### Legendas
```python
# Create subtitles in standard position
subtitle = create_asset(
    "subtitle",
    data="Hello world",
    params=TextAssetParams(
        position=RegionPosition(x="center", y="bottom")
    )
)
```

## Validação de Posição e Auxiliares

### Verificação de Tipo
```python
from mosaico.positioning.utils import (
    is_absolute_position,
    is_relative_position,
    is_region_position
)

# Check position types
if is_region_position(position):
    # Handle region position
    pass
elif is_relative_position(position):
    # Handle relative position
    pass
elif is_absolute_position(position):
    # Handle absolute position
    pass
```

### Criação de Posição por Região
```python
# Create from string shorthand
position = RegionPosition.from_string("bottom")  # center-bottom
position = RegionPosition.from_string("right")   # right-center
```

## Melhores Práticas

1. **Escolhendo o Tipo de Posição Correto**
    - Use Absoluto para requisitos de precisão em pixels
    - Use Relativo para layouts independentes de resolução
    - Use Região para elementos padrão de vídeo

2. **Considerações sobre Resolução**
    ```python
    # Bad: Hard-coded absolute positions
    position = AbsolutePosition(x=1920, y=1080)

    # Good: Relative positioning for flexibility
    position = RelativePosition(x=1.0, y=1.0)
    ```

3. **Layouts Manuteníveis**
    ```python
    # Create reusable positions
    LOWER_THIRD_POSITION = RegionPosition(x="left", y="bottom")
    WATERMARK_POSITION = AbsolutePosition(x=50, y=50)
    ```

4. **Posicionamento Dinâmico**
    ```python
    # Adjust position based on content
    def get_title_position(title_length: int) -> Position:
        if title_length > 50:
            return RegionPosition(x="center", y="top")
        return RelativePosition(x=0.5, y=0.3)
    ```

## Conclusão

Entender e usar efetivamente o sistema de posicionamento é crucial para criar composições de vídeo com aparência profissional. A flexibilidade de ter três estratégias de posicionamento permite que você lide com qualquer requisito de layout enquanto mantém um código limpo e manutenível.
