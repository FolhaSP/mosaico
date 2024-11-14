from collections.abc import Sequence
from typing import Any, ClassVar, Protocol, runtime_checkable

from mosaico.assets.audio import AudioAsset, AudioAssetParams


@runtime_checkable
class SpeechSynthesizer(Protocol):
    """
    Protocol defining the interface for text-to-speech synthesis services.

    The SpeechSynthesizer protocol standardizes how text is converted to speech across
    different TTS providers (e.g., Google Cloud TTS, Azure Speech). Implementations
    of this protocol handle the specifics of communicating with TTS services and managing
    the generated audio assets.

    Implementations should handle:

    * Authentication with the TTS service
    * Rate limiting and quotas
    * Error handling and retries
    * Audio format conversion if necessary
    * Temporary file management
    * Resource cleanup

    Example:

    ```python
    class MySpeechSynthesizer(SpeechSynthesizer):
        provider = "my-provider"

        def synthesize(self, texts, audio_params=None):
            # Implementation details
            pass

    synthesizer = MySpeechSynthesizer()
    audio_assets = synthesizer.synthesize(
        texts=["Hello world", "Welcome to the demo"],
        audio_params=AudioAssetParams(volume=0.8)
    )
    ```

    :cvar provider: Identifier for the TTS service provider (e.g., "openai", "assemblyai", "azure").
        This should be a unique string that identifies the implementation.
    """

    provider: ClassVar[str]
    """The provider of the speech synthesizer."""

    def synthesize(
        self, texts: Sequence[str], *, audio_params: AudioAssetParams | None = None, **kwargs: Any
    ) -> list[AudioAsset]:
        """
        Convert a list of texts into synthesized speech audio assets.

        This method handles the conversion of text to speech, managing both the synthesis
        process and the creation of audio assets for use in video projects.


        !!! note
            * The method should handle cleanup of any temporary files
            * Audio assets should be properly configured with metadata
            * Implementation should handle text normalization if needed
            * Large texts may need to be chunked according to service limits
            * Audio format should match project requirements

        :param texts: List of text strings to be converted to speech. Each string should
            be properly formatted text ready for synthesis.
        :param audio_params: Optional parameters for configuring the output audio assets.
            If None, default parameters will be used. These parameters affect properties
            like sample rate, channels, etc.
        :param kwargs: Additional provider-specific parameters.
        :return: List of audio assets containing the synthesized speech. The returned list
            will have the same length as the input texts list, with corresponding indices.

        """
        ...
