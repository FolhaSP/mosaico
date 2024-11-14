from __future__ import annotations

from typing import Protocol, runtime_checkable

from mosaico.assets.audio import AudioAsset
from mosaico.audio_transcribers.transcription import Transcription


@runtime_checkable
class AudioTranscriber(Protocol):
    """
    A protocol defining the interface for audio transcription services.

    This protocol specifies the contract that all audio transcribers in the Mosaico
    project should adhere to. It defines a single method, :meth:`transcribe`, which
    takes an audio asset and returns a transcription.

    Implementations of this protocol can use various transcription technologies,
    such as speech-to-text APIs, local models, or custom algorithms. The protocol
    ensures a consistent interface regardless of the underlying implementation.

    !!! note
        This is a runtime checkable protocol, which means ``isinstance()`` and
        ``issubclass()`` checks can be performed against it.

    __Example__:

    ```python
        class MyTranscriber:
            def transcribe(self, audio_asset: AudioAsset) -> Transcription:
                # Implement transcription logic here
                ...

        transcriber: AudioTranscriber = MyTranscriber()
        transcription = transcriber.transcribe(my_audio_asset)
    ```
    """

    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        """
        Transcribe speech from an audio asset to text.

        This method should implement the core logic for converting speech in the
        provided audio asset into text. The specific implementation can vary
        based on the transcription technology being used.

        :param audio_asset: The audio asset containing the speech to be transcribed.
        :return: A Transcription object containing the text transcription of the speech.

        .. note::
           The implementation should handle various audio formats and durations
           as defined by the :class:`AudioAsset` class. It should also be able to handle
           potential errors gracefully.
        """
        ...
