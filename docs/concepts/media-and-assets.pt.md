# Mídia e Assets

## Visão Geral

No Mosaico, mídia e assets são os elementos fundamentais da produção de vídeo. Eles representam os materiais brutos e elementos prontos para produção que compõem uma composição de vídeo. Este guia explica a diferença entre mídia e assets, como são utilizados na produção de vídeo e o sistema de tipos de assets no Mosaico.

## Entendendo o Pipeline de Produção

Na produção de vídeo com o Mosaico, existem duas etapas distintas de manipulação de conteúdo:

1. **Estágio de Mídia**: Coleta de Conteúdo Bruto
2. **Estágio de Assets**: Elementos Prontos para Produção

Esta abordagem em duas etapas reflete os fluxos de trabalho profissionais de produção de vídeo, onde materiais brutos são preparados e transformados em elementos prontos para produção. A conexão entre essas etapas são os geradores de script, que serão abordados em uma seção posterior.

### Objetos de Mídia: Materiais Brutos

Objetos de mídia representam o estágio de "materiais brutos" do seu conteúdo:

- Clipes de vídeo brutos
- Arquivos de áudio não processados
- Imagens originais
- Conteúdo de texto simples

```python
from mosaico.media import Media

# Collecting raw materials
background = Media.from_path("media/background.png")
voice_over = Media.from_path("media/narration.wav")
graphics = Media.from_path("media/graphics.png")
script = Media.from_path("media/script.txt")
```

Pense nos objetos Media como itens em sua "biblioteca de mídia" antes de serem preparados para produção.

### Assets: Elementos Prontos para Produção

Assets são os blocos fundamentais de qualquer composição de vídeo no Mosaico e representam o estágio "pronto para produção" de uma mídia. Eles representam diferentes tipos de elementos de mídia que podem ser combinados para criar um vídeo, como imagens, clipes de áudio, sobreposições de texto e legendas. Pense em assets como os materiais prontos necessários para construir seu vídeo.

Cada asset no Mosaico tem essencialmente a mesma estrutura de um objeto de mídia, mas com propriedades e capacidades adicionais, como parâmetros específicos de tipo e metadados. Assets são projetados para estarem prontos para produção e podem ser usados diretamente em composições de vídeo:

- Um identificador único
- Conteúdo principal (os dados reais da mídia)
- Parâmetros específicos do tipo
- Metadados para informações adicionais
- Capacidades de validação e processamento integradas

```python
from mosaico.assets import ImageAsset, AudioAsset

# Instantiating assets
background = ImageAsset.from_path("assets/background.png")
voice_over = AudioAsset.from_path("assets/narration.wav")
graphics = ImageAsset.from_path("assets/graphics.png")
subtitles = [SubtitleAsset.from_data(data) for data in subtitle_data]
```

### Diferenças Principais

Aqui está um resumo das principais diferenças entre Mídia e Assets:

| Aspecto | Objetos de Mídia | Assets |
|--------|--------------|---------|
| Propósito | Armazenamento e manipulação básica de conteúdo bruto | Manipulação de elementos de produção de vídeo |
| Estado | Forma original, não processada | Processado, pronto para produção |
| Propriedades | Metadados básicos e acesso ao conteúdo | Parâmetros de produção e comportamentos |
| Uso | Coleta e armazenamento de conteúdo | Timeline e composição |
| Integração | Ponte com sistemas externos | Sistema de renderização de vídeo |

## O Sistema de Tipos de Asset

O Mosaico implementa um sistema de assets flexível e com segurança de tipos usando uma classe base que outros tipos de assets estendem. Essa abordagem hierárquica garante consistência enquanto permite que cada tipo de asset tenha suas características e parâmetros específicos.

### Estrutura Base do Asset

A classe base de asset define a estrutura central para todos os tipos de assets no Mosaico. Inclui propriedades comuns como o tipo de asset e parâmetros, que são então estendidos por tipos específicos de assets.

```python
from mosaico.assets.base import BaseAsset
from pydantic import BaseModel

class BaseAsset(Media, Generic[T]):
    type: str
    params: T
```

### Tipos de Assets

Para criar uma composição de vídeo, você precisa de diferentes tipos de assets que representam vários elementos de mídia. Aqui estão alguns tipos comuns de assets no __Mosaico__:

!!! note "Assets de Vídeo"
    Embora planejados, assets de vídeo não estão atualmente implementados no Mosaico, pois sua arquitetura de integração ainda está em discussão. Eles serão adicionados em breve em versões futuras.

#### Áudio

Assets de áudio gerenciam todos os elementos sonoros em seu vídeo, incluindo narração, música, efeitos sonoros e vozes. Eles incluem propriedades básicas como duração, taxa de amostragem, canais, volume e pontos de corte. Isso ajuda você a controlar como o áudio é reproduzido em seu vídeo mantendo padrões de qualidade profissional.

Exemplo de uso:

```python
from mosaico.assets import AudioAsset, AudioAssetParams

# Create an audio asset with specific volume
audio = AudioAsset.from_path(
    "narration.mp3",
    params=AudioAssetParams(volume=0.8)
)
```

#### Imagem

Assets de imagem lidam com visuais estáticos como fundos, sobreposições, logos e fotos em seu vídeo. Eles vêm com propriedades-chave para controlar como aparecem: tamanho (largura e altura), posição, ordem de camada (z-index), recorte e modo de fundo. Essas propriedades permitem que você controle com precisão como as imagens aparecem e trabalham juntas em seu vídeo.

Exemplo de uso:
```python
from mosaico.assets import ImageAsset, ImageAssetParams

# Create an image asset with positioning
image = ImageAsset.from_path(
    "background.jpg",
    params=ImageAssetParams(
        position=AbsolutePosition(x=100, y=100),
        as_background=True
    )
)
```

#### Texto

Assets de texto permitem que você adicione títulos, legendas e outros elementos de texto aos seus vídeos. Eles incluem opções de estilo como fontes, cores, alinhamentos e efeitos como sombras e contornos. Isso dá a você controle total sobre como o texto aparece em seu vídeo mantendo qualidade profissional.

Exemplo de uso:
```python
from mosaico.assets import TextAsset, TextAssetParams

# Create styled text
text = TextAsset.from_data(
    "Welcome to My Video",
    params=TextAssetParams(
        font_size=48,
        font_color=Color("white"),
        align="center"
    )
)
```

#### Legendas

Assets de legenda são assets de texto especializados projetados para legendagem de vídeo. Eles lidam com legendas de diálogo, closed captions, traduções e sobreposições de texto temporizado. Você pode ajustar seu posicionamento, tamanhos de fonte e cores de fundo. Eles incluem recursos para legibilidade e suporte multilíngue para criar vídeos acessíveis.

Exemplo de uso:
```python
from mosaico.assets import SubtitleAsset

# Create a subtitle with proper positioning
subtitle = SubtitleAsset.from_data(
    "This is a subtitle",
    params=TextAssetParams(
        position=RegionPosition(x="center", y="bottom"),
        font_size=36
    )
)
```

## Trabalhando com Assets

Dado que você já tem uma coleção de assets, você pode começar a trabalhar com eles para criar sua composição de vídeo.

Um pipeline comum para trabalhar com assets no Mosaico envolve carregar, gerenciar e combinar assets para criar uma sequência de vídeo. O posterior será coberto em outra seção, mas aqui está como você pode realizar operações básicas apenas com assets.

### Carregando Assets

Para o processo de composição de vídeo começar, você precisa carregar sua mídia em assets. Se você já sabe onde e como um determinado conteúdo deve ser exibido, você pode criar diretamente os assets correspondentes chamando os métodos de classe do tipo de asset ou usando o sistema de fábrica de assets.

=== "From files"

    ```python
    from mosaico.assets import ImageAsset

    image = ImageAsset.from_path("logo.png")
    ```

=== "From raw data"

    ```python
    from mosaico.assets import TextAsset

    text = TextAsset.from_data("Hello World")
    ```

=== "From factory"

    ```python
    from mosaico.assets import create_asset

    asset = create_asset("image", path="logo.png")
    ```

=== "From existing media"

    ```python
    from mosaico.assets.utils import convert_media_to_asset

    asset = convert_media_to_asset(media_object)
    ```

### Gerenciando Parâmetros de Asset

Todos os assets têm parâmetros que controlam sua aparência e comportamento. Você pode atualizar esses parâmetros para personalizar como os assets são exibidos em sua composição de vídeo.

```python
# Update text styling
text_asset = text_asset.with_params({
    "font_size": 48,
    "font_color": "#FFFFFF",
    "align": "center"
})
```

### Melhores Práticas

Ao trabalhar com assets, considere as seguintes melhores práticas para garantir que sua composição de vídeo seja bem organizada e eficiente:

1. **Organização**
    - Use IDs de asset significativos
    - Agrupe assets relacionados
    - Mantenha hierarquias claras de assets

2. **Desempenho**
    - Otimize tamanhos de imagem antes de carregar
    - Use formatos de áudio apropriados
    - Limpe assets não utilizados

3. **Manutenibilidade**
    - Documente metadados de assets
    - Use convenções de nomenclatura consistentes
    - Mantenha parâmetros de assets organizados

4. **Reusabilidade**
    - Crie templates de asset reutilizáveis
    - Compartilhe parâmetros comuns
    - Use referências de asset efetivamente

## Benefícios do Fluxo de Trabalho

Esta abordagem em duas etapas fornece várias vantagens:

1. **Separação Limpa de Responsabilidades**
    - Manipulação de mídia é separada da lógica de produção
    - Distinção clara entre conteúdo bruto e processado
    - Gerenciamento de conteúdo mais fácil

2. **Pipeline de Conteúdo Flexível**
    - Conteúdo bruto pode ser processado diferentemente para diferentes usos
    - A mesma mídia pode criar diferentes tipos de assets
    - Fácil integração com fontes de conteúdo externas

3. **Fluxo de Trabalho Profissional**
    - Espelha processos profissionais de produção de vídeo
    - Etapas claras para preparação de conteúdo
    - Gerenciamento organizado de assets

4. **Otimização de Recursos**
    - Conteúdo bruto é processado apenas quando necessário
    - Múltiplos assets podem referenciar a mesma mídia
    - Uso eficiente de recursos

## Conclusão

Entender essa distinção entre Mídia e Assets é fundamental para trabalhar efetivamente com o Mosaico, pois reflete a progressão natural do conteúdo bruto para a produção final de vídeo.
