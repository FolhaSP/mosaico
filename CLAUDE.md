# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- **Install dependencies**: `make install` (installs all dependencies and pre-commit hooks via uv)
- **Sync dependencies**: `uv sync --frozen --all-extras`

### Code Quality
- **Lint code**: `make lint` or `uv run ruff check . --fix`
- **Format code**: `make format` or `uv run ruff format .`
- **Run all quality checks**: `make all` (lint + format + test)

### Testing
- **Run unit tests**: `make test` or `uv run pytest tests`
- **Run E2E tests**: `make e2e` or `uv run pytest e2e`
- **Run specific test**: `uv run pytest tests/path/to/test_file.py::test_function`

### Documentation
- **Build docs**: `make docs` or `uv run mkdocs build`
- **Serve docs locally**: `make docs-serve` or `uv run mkdocs serve --no-strict`

### CLI Usage
- **Run mosaico CLI**: `uv run mosaico` or `python -m mosaico`

## Architecture Overview

Mosaico is a Python video generation framework built on a composition-based architecture that treats video creation as orchestrating media assets on a timeline.

### Core Components

**Media Layer** (`media.py`): Foundational abstraction for all media content (text, images, audio, video) with support for both in-memory data and file references.

**Assets System** (`assets/`): Transforms raw media into typed, parameterized assets ready for composition:
- `AudioAsset`, `ImageAsset`, `TextAsset`, `SubtitleAsset`
- Each has associated parameter classes controlling rendering behavior
- Factory functions provide type-safe asset creation

**Clip Makers** (`clip_makers/`): Convert assets into MoviePy clips using the `ClipMaker[T]` protocol. Specialized implementations handle each asset type's conversion to video/audio clips.

**Effects System** (`effects/`): Transform clips via the `Effect[ClipType]` protocol. Built-in effects include Zoom, Pan, Fade, and CrossFade.

**Positioning** (`positioning/`): Three positioning modes:
- `AbsolutePosition`: Pixel-perfect placement
- `RelativePosition`: Percentage-based positioning  
- `RegionPosition`: Named region placement

**Video Module** (`video/`): Central orchestration via `VideoProject` which manages assets, timeline, and rendering configuration.

**Scene Management** (`scene.py`): Groups related assets with timing via `AssetReference` objects.

### Data Flow

```
Media Objects → Assets → Asset References → Scenes → Timeline → Video Project → Rendered Video
```

### Extension Points

The framework uses Python protocols for extensibility:
- `ClipMaker[T]`: Create new asset-to-clip converters
- `Effect[ClipType]`: Implement visual/audio effects
- `SpeechSynthesizer`: Text-to-speech integration (OpenAI, ElevenLabs included)
- `AudioTranscriber`: Speech-to-text functionality (AssemblyAI, OpenAI included)
- `ScriptGenerator`: AI-powered script generation from media
- `TranscriptionAligner`: Align transcriptions with original text

### AI Integrations

Built-in support for:
- **Speech Synthesis**: OpenAI TTS, ElevenLabs
- **Audio Transcription**: AssemblyAI, OpenAI Whisper
- **Script Generation**: AI-powered content creation from media collections
- **Framework Integrations**: Haystack and LangChain adapters for LLM workflows

## Key Patterns

- **Protocol-based design**: Extensible interfaces without inheritance
- **Factory pattern**: Type-safe object creation via `create_asset()`, `create_effect()`, `make_clip()`
- **Pydantic models**: Comprehensive validation and type safety
- **Storage abstraction**: fsspec for flexible storage backends
- **Timeline composition**: Assets can be individual references or grouped in scenes

## Development Notes

- Uses `uv` for dependency management and virtual environments
- Follows PEP 257 docstring conventions
- Ruff for linting and formatting with strict rules
- MyPy for type checking
- Pre-commit hooks enforce code quality
- Test coverage tracked via pytest-cov
- Documentation built with MkDocs Material

## Optional Dependencies

The framework supports optional integrations via extras:
- `assemblyai`: AssemblyAI transcription
- `elevenlabs`: ElevenLabs speech synthesis
- `openai`: OpenAI TTS and transcription
- `langchain`: LangChain framework integration
- `haystack`: Haystack AI framework integration
- `cli`: Click-based command-line interface