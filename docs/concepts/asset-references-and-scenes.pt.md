# Referências de Assets e Cenas

!!! note "Pré-requisitos"
    - [__Assets__](media-and-assets.md#assets-production-ready-elements)

## Visão Geral

Referências de assets são um conceito central no Mosaico que permite controlar como os assets aparecem na linha do tempo do seu vídeo. Elas fornecem uma maneira de gerenciar diferentes tipos de mídia de forma eficiente, controlar como a mídia aparece no seu vídeo, manter segurança de tipos e validação, criar composições de vídeo complexas e estender funcionalidades conforme necessário. Um grupo de referências de assets pode ser combinado em uma cena para criar uma seção lógica do seu vídeo.

Em resumo, o sistema de assets no Mosaico consiste em dois componentes principais:

- **Referências de Assets**: Definem quando e como os assets aparecem na linha do tempo
- **Cenas**: Agrupam referências de assets relacionados

Estes componentes formam os blocos de construção da sua linha do tempo de vídeo e controlam a apresentação dos seus assets de mídia.

## Referências de Assets

Referências de assets são cruciais para controlar como os assets aparecem na sua linha do tempo de vídeo. Elas atuam como instruções para:

- Quando os assets aparecem e desaparecem
- Por quanto tempo ficam visíveis
- Quais efeitos são aplicados
- Quaisquer substituições de parâmetros

Pense nelas como as "direções de palco" para seus assets:

```python
from mosaico.assets.reference import AssetReference

# Control asset timing and effects
asset_ref = (
    AssetReference.from_asset(image)
    .with_start_time(0)
    .with_end_time(5)
    .with_effects([fade_in_effect])
)
```

### Estrutura

A estrutura básica de uma referência de asset consiste nos seguintes componentes:

```python
from mosaico.assets.reference import AssetReference

#Basic structure of an asset reference
reference = AssetReference(
    asset_id="background_01",           # Asset identifier
    asset_params=ImageAssetParams(...), # Optional parameter overrides
    start_time=0,                       # When asset appears
    end_time=10,                        # When asset disappears
    effects=[]                          # Optional effects
)
```

### Criando Referências de Assets

Existem duas maneiras principais de criar referências de assets:

1. **A partir de um Asset Existente**
```python
# Create reference from asset
logo_ref = AssetReference.from_asset(
    asset=logo_asset,
    start_time=0,
    end_time=30
)

# Using builder pattern
title_ref = AssetReference.from_asset(title_asset)\
    .with_start_time(5)\
    .with_end_time(10)\
    .with_params(TextAssetParams(font_size=48))\
    .with_effects([fade_in_effect])
```

2. **Construção Direta**
```python
# Manual reference creation
music_ref = AssetReference(
    asset_id="background_music",
    start_time=0,
    end_time=60,
    asset_params=AudioAssetParams(volume=0.8)
)
```

## Cenas

Cenas são uma maneira de agrupar assets na sua linha do tempo de vídeo. Elas permitem organizar seu vídeo em seções lógicas e aplicar efeitos a vários assets de uma vez. Cenas podem ser usadas para criar transições, aplicar efeitos globais ou agrupar assets relacionados:

!!! warning
    A implementação de transições e efeitos globais em Cenas ainda não é suportada no Mosaico, mas será adicionada em versões futuras.

```python
from mosaico.scenes.scene import Scene

# Create a scene with multiple assets
scene = Scene(
    asset_references=[
        AssetReference.from_asset(image1),
        AssetReference.from_asset(image2),
    ],
)
```

### Padrões Comuns

#### Fundo com Sobreposição

```python
scene = Scene(
    title="Title Scene",
    asset_references=[
        # Background layer
        AssetReference.from_asset(background)
            .with_start_time(0)
            .with_end_time(10),

        # Text overlay
        AssetReference.from_asset(title)
            .with_start_time(2)
            .with_end_time(8)
    ]
)
```

#### Sincronização Áudio-Visual

```python
narration_ref = AssetReference.from_asset(narration)
    .with_start_time(0)
    .with_end_time(narration.duration)

scene = Scene(
    asset_references=[
        # Visual content matches narration timing
        AssetReference.from_asset(visual)
            .with_start_time(narration_ref.start_time)
            .with_end_time(narration_ref.end_time),
        narration_ref
    ]
)
```

#### Conteúdo Sequencial

```python
def create_sequence_scene(assets: list[BaseAsset], duration_per_asset: float) -> Scene:
    """Create a scene with sequential assets."""
    references = []
    current_time = 0

    for asset in assets:
        references.append(
            AssetReference.from_asset(asset)
                .with_start_time(current_time)
                .with_end_time(current_time + duration_per_asset)
        )
        current_time += duration_per_asset

    return Scene(asset_references=references)
```

## Melhores Práticas

**Organização de Referências de Assets**

- Mantenha assets relacionados juntos em cenas
- Use relações de tempo significativas
- Aplique efeitos com moderação

**Estrutura de Cena**

- Agrupe conteúdo logicamente relacionado
- Mantenha hierarquias de tempo claras
- Adicione títulos e descrições descritivos

**Gerenciamento da Linha do Tempo**

- Verifique a existência de assets antes de referenciá-los
- Verifique a consistência do tempo
- Gerencie transições entre cenas

## Conclusão

Este sistema abrangente de assets permite gerenciar diferentes tipos de mídia de forma eficiente, controlar como a mídia aparece no seu vídeo, manter segurança de tipos e validação, criar composições de vídeo complexas e estender funcionalidades conforme necessário.
