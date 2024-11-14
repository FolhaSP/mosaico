# Começando

__Mosaico__ é uma biblioteca Python para criar e gerenciar composições de vídeo programaticamente. Fornece uma interface de alto nível para trabalhar com assets de mídia, posicionar elementos, aplicar efeitos e gerar roteiros de vídeo, tudo construído sobre o MoviePy - uma das bibliotecas de edição de vídeo mais populares em Python.

A biblioteca foi projetada pensando em flexibilidade e extensibilidade, oferecendo abstrações limpas para:

- Gerenciamento de diferentes tipos de assets de mídia (áudio, imagens, texto, legendas)
- Controle preciso de posicionamento e layout
- Aplicação de efeitos e animação
- Geração de roteiros com IA
- Síntese de texto em fala
- Integração com frameworks populares de ML

## Recursos e Capacidades Principais

<div class="grid cards" markdown>

-   [:material-script-text: __Geração de Roteiros__](concepts/script-generators.md)

    ---

    -   Interfaces limpas para geração personalizada de roteiros
    -   Framework extensível para integração com IA
    -   Organização de cenas e tomadas
    -   Renderização de roteiro para vídeo

-   [:material-file-multiple: __Gerenciamento de Assets__](concepts/media-and-assets.md)

    ---

    -   Suporte para múltiplos tipos de mídia
    -   Manipulação flexível de parâmetros e metadados de assets
    -   Sistema de referência para rastreamento de assets em cenas

-   [:material-arrange-send-backward: __Sistema de Posicionamento__](concepts/positioning.md)

    ---

    -   Múltiplos modos de posicionamento (absoluto, relativo, baseado em regiões)
    -   Cálculos de posicionamento com consciência de quadro
    -   Opções flexíveis de alinhamento

-   [:material-movie-filter: __Motor de Efeitos__](concepts/effects.md)

    ---

    -   Efeitos incorporados de pan e zoom
    -   Sistema extensível de efeitos
    -   Configuração baseada em parâmetros
    -   Suporte à composição de efeitos

-   [:material-microphone-message: __Síntese de Fala__](concepts/speech-synthesizers.md)

    ---

    -   Integração com principais provedores de TTS
    -   Parâmetros configuráveis de voz
    -   Suporte à síntese em lote
    -   Controles de parâmetros de assets

-   [:material-puzzle: __Integrações Externas__](integrations/index.md)

    ---

    -   Integrações prontas com Haystack e LangChain
    -   Sistema extensível de adaptadores
    -   Protocolos limpos de integração
</div>
