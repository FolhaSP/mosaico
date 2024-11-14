# Installation

## Requirements

Before installing the __Mosaico__ framework, you need to make sure you have the following prerequisites:

1. **Python 3.10 or superior**

    Mosaico requires Python 3.10 or superior. You can check your Python version by running:

    ```bash
    python --version
    ```

    If you need to update or install Python, visit [python.org](https://www.python.org/downloads/) to get the latest version.

2. **FFmpeg**

    __Mosaico__ depends on FFmpeg for video processing. You must have FFmpeg installed and available in your system PATH.

    To check if FFmpeg is installed, run:

    ```bash
    ffmpeg -version
    ```

    If it's not installed, you can get it from [ffmpeg.org](https://ffmpeg.org/download.html) or use your operating system's package manager.

    === "Ubuntu/Debian"

        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```

    === "macOS (with Homebrew)"

        ```bash
        brew install ffmpeg
        ```

    === "Windows (with Chocolatey)"

        ```bash
        choco install ffmpeg
        ```

After ensuring these prerequisites are satisfied, you can proceed with the __Mosaico__ installation.

## Installation

To install __Mosaico__, run the following command according to your preferred package manager:

=== "pip"

    ``` bash
    pip install mosaico
    ```

=== "pipx"

    ``` bash
    pipx install mosaico
    ```

=== "uv"

    ``` bash
    uv add mosaico
    ```

=== "poetry"

    ``` bash
    poetry add mosaico
    ```

=== "pdm"

    ``` bash
    pdm add mosaico
    ```

It is also possible to install __Mosaico__ from source by cloning the repository and running the following command:

```bash
git clone https://github.com/folhalab/mosaico.git
cd mosaico
pip install -e .
```
