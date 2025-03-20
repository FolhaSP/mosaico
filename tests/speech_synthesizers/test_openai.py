import pytest
from pydantic import ValidationError

from mosaico.speech_synthesizers.openai import OpenAISpeechSynthesizer


def test_pass_instructions_raises_on_non_4o_model() -> None:
    with pytest.raises(
        ValidationError, match="`instructions` cannot be set when model is not from the GPT-4o family or higher."
    ):
        _ = OpenAISpeechSynthesizer(api_key="test", model="tts-1", instructions="Test")


def test_pass_instructions_as_synthesize_kwargs_raises_on_non_4o_model() -> None:
    synthesizer = OpenAISpeechSynthesizer(api_key="test", model="tts-1")

    with pytest.raises(
        ValueError, match="`instructions` cannot be set when model is not from the GPT-4o family or higher."
    ):
        synthesizer.synthesize(["Test"], instructions="Test")
