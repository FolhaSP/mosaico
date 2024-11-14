from __future__ import annotations

from mosaico.speech_synthesizers.elevenlabs import ElevenLabsSpeechSynthesizer
from mosaico.speech_synthesizers.openai import OpenAISpeechSynthesizer
from mosaico.speech_synthesizers.protocol import SpeechSynthesizer


__all__ = [
    "SpeechSynthesizer",
    "OpenAISpeechSynthesizer",
    "ElevenLabsSpeechSynthesizer",
]
