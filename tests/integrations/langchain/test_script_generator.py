from collections.abc import Sequence
from typing import Any

import pytest
from langchain_core.runnables import RunnableLambda

from mosaico.integrations.langchain.script_generator import (
    LangChainScriptGenerator,
    convert_script_generator_to_runnable,
)
from mosaico.media import Media
from mosaico.script_generators.protocol import ScriptGenerator
from mosaico.script_generators.script import ShootingScript, Shot


@pytest.fixture
def sample_media():
    return [Media.from_data("Test video content", metadata={"description": "A test video", "credit": "Test Author"})]


@pytest.fixture
def sample_script():
    return ShootingScript(
        title="Test Script",
        description="A test script",
        shots=[
            Shot(
                number=1,
                description="Test shot",
                start_time=0.0,
                end_time=5.0,
                subtitle="Test subtitle",
                media_references=[0],
            )
        ],
    )


@pytest.fixture
def mock_runnable(sample_script):
    def process_media(inputs: dict) -> ShootingScript:
        # Verify media is present in inputs
        assert "media" in inputs
        return sample_script

    return RunnableLambda(process_media).with_types(input_type=dict, output_type=ShootingScript)


def test_langchain_script_generator_initialization(mock_runnable):
    """Test that the generator initializes correctly with valid runnable"""
    generator = LangChainScriptGenerator(mock_runnable)
    assert generator.runnable == mock_runnable


def test_langchain_script_generator_invalid_output_type():
    """Test that initialization fails with invalid output type"""
    invalid_runnable = RunnableLambda(lambda x: "invalid").with_types(
        input_type=dict,
        output_type=str,  # Invalid - should be ShootingScript
    )

    with pytest.raises(TypeError, match="Runnable must return a ShootingScript object"):
        LangChainScriptGenerator(invalid_runnable)


class MockScriptGenerator(ScriptGenerator):
    """Mock implementation of ScriptGenerator for testing"""

    def generate(self, media: Sequence[Media], **kwargs) -> ShootingScript:
        return ShootingScript(
            title="Mock Script",
            shots=[
                Shot(
                    number=1,
                    description="Mock shot",
                    start_time=0.0,
                    end_time=5.0,
                    subtitle="Test",
                    media_references=[0],
                )
            ],
        )


def test_convert_script_generator_to_runnable(sample_media):
    """Test converting a ScriptGenerator to a LangChain runnable"""
    generator = MockScriptGenerator()
    runnable = convert_script_generator_to_runnable(generator)

    assert runnable.InputType == dict[str, Any]
    assert runnable.OutputType == ShootingScript

    result = runnable.invoke({"media": sample_media})
    assert isinstance(result, ShootingScript)
    assert len(result.shots) == 1


def test_convert_script_generator_with_additional_kwargs(sample_media):
    """Test that additional kwargs are properly passed through"""

    class KwargsTestGenerator(ScriptGenerator):
        def generate(self, media: Sequence[Media], **kwargs) -> ShootingScript:
            assert "test_param" in kwargs
            assert kwargs["test_param"] == "test_value"
            return ShootingScript(title="Test")

    generator = KwargsTestGenerator()
    runnable = convert_script_generator_to_runnable(generator)

    result = runnable.invoke({"media": sample_media, "test_param": "test_value"})

    assert isinstance(result, ShootingScript)


def test_convert_script_generator_invalid_input():
    """Test that the runnable properly handles invalid input"""
    generator = MockScriptGenerator()
    runnable = convert_script_generator_to_runnable(generator)

    with pytest.raises(KeyError):
        runnable.invoke({"invalid_key": "value"})
