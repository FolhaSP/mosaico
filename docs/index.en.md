# Getting Started

__Mosaico__ is a Python library for programmatically creating and managing video compositions. It provides a high-level interface for working with media assets, positioning elements, applying effects, and generating video scripts, all built on top of MoviePy - one of the most popular video editing libraries in Python.

The library is designed with flexibility and extensibility in mind, offering clean abstractions for:

- Managing different types of media assets (audio, images, text, subtitles)
- Precise positioning and layout control
- Effect application and animation
- AI-powered script generation
- Text-to-speech synthesis
- Integration with popular ML frameworks

## Key Features and Capabilities

<div class="grid cards" markdown>

-   [:material-script-text: __Script Generation__](concepts/script-generators.md)

    ---

    -   Clean interfaces for custom script generation
    -   Extensible framework for AI integration
    -   Shot and scene organization
    -   Script-to-video rendering

-   [:material-file-multiple: __Asset Management__](concepts/media-and-assets.md)

    ---

    -   Support for multiple media types
    -   Flexible asset parameters and metadata handling
    -   Reference system for tracking assets in scenes

-   [:material-arrange-send-backward: __Positioning System__](concepts/positioning.md)

    ---

    -   Multiple positioning modes (absolute, relative, region-based)
    -   Frame-aware positioning calculations
    -   Flexible alignment options

-   [:material-movie-filter: __Effects Engine__](concepts/effects.md)

    ---

    -   Built-in pan and zoom effects
    -   Extensible effect system
    -   Parameter-based effect configuration
    -   Effect composition support

-   [:material-microphone-message: __Speech Synthesis__](concepts/speech-synthesizers.md)

    ---

    -   Integration with major TTS providers
    -   Configurable voice parameters
    -   Batch synthesis support
    -   Asset parameter controls

-   [:material-puzzle: __External Integrations__](integrations/index.md)

    ---

    -   Haystack and LangChain integrations out of the box
    -   Extensible adapter system
    -   Clean integration protocols
</div>
