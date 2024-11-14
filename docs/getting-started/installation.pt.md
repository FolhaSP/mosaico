# Instalação

## Requisitos

Antes de instalar o framework __Mosaico__, você precisa garantir que tem os seguintes pré-requisitos:

1. **Python 3.10 ou superior**

    O Mosaico requer Python 3.10 ou superior. Você pode verificar sua versão do Python executando:

    ```bash
    python --version
    ```

    Se você precisar atualizar ou instalar o Python, visite [python.org](https://www.python.org/downloads/) para obter a versão mais recente.

2. **FFmpeg**

    O __Mosaico__ depende do FFmpeg para processamento de vídeo. Você deve ter o FFmpeg instalado e disponível no PATH do seu sistema.

    Para verificar se o FFmpeg está instalado, execute:

    ```bash
    ffmpeg -version
    ```

    Se não estiver instalado, você pode obtê-lo em [ffmpeg.org](https://ffmpeg.org/download.html) ou usar o gerenciador de pacotes do seu sistema operacional.

    === "Ubuntu/Debian"

        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```

    === "macOS (com Homebrew)"

        ```bash
        brew install ffmpeg
        ```

    === "Windows (com Chocolatey)"

        ```bash
        choco install ffmpeg
        ```

Depois de garantir que esses pré-requisitos estejam satisfeitos, você pode prosseguir com a instalação do __Mosaico__.

## Instalação

Para instalar o __Mosaico__, execute o seguinte comando de acordo com seu gerenciador de pacotes preferido:

=== "pip"

    ```bash
    pip install mosaico
    ```

=== "pipx"

    ```bash
    pipx install mosaico
    ```

=== "uv"

    ```bash
    uv add mosaico
    ```

=== "poetry"

    ```bash
    poetry add mosaico
    ```

=== "pdm"

    ```bash
    pdm add mosaico
    ```

Também é possível instalar o __Mosaico__ a partir do código fonte clonando o repositório e executando o seguinte comando:

```bash
git clone https://github.com/folhalab/mosaico.git
cd mosaico
pip install -e .
```
