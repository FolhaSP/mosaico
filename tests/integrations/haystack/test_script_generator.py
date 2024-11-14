from unittest.mock import Mock

import pytest

from mosaico.integrations.haystack.script_generator import HaystackScriptGenerator
from mosaico.media import Media
from mosaico.script_generators.script import ShootingScript


@pytest.fixture
def mock_pipeline():
    return Mock()


@pytest.fixture
def script_generator(mock_pipeline):
    return HaystackScriptGenerator(
        pipeline=mock_pipeline, input_component="test_component", media_input_key="media", script_output_key="script"
    )


def test_init():
    """Test initialization with custom parameters"""
    pipeline = Mock()
    generator = HaystackScriptGenerator(
        pipeline=pipeline,
        input_component="custom_component",
        media_input_key="custom_media",
        script_output_key="custom_script",
    )

    assert generator.pipeline == pipeline
    assert generator.input_component == "custom_component"
    assert generator.media_input_key == "custom_media"
    assert generator.script_output_key == "custom_script"


def test_generate_success(script_generator, mock_pipeline):
    """Test successful script generation"""
    # Setup test data
    media = [Media.from_data("test")]
    expected_script = ShootingScript(title="Test Script")

    # Configure mock pipeline
    mock_pipeline.run.return_value = {"component1": {"script": expected_script}}

    # Execute and verify
    result = script_generator.generate(media)

    assert result == expected_script
    mock_pipeline.run.assert_called_once_with({"test_component": {"media": [media[0]]}})


def test_generate_with_dict_output(script_generator, mock_pipeline):
    """Test script generation when pipeline returns a dict instead of ShootingScript"""
    media = [Media.from_data("test")]
    script_dict = {"title": "Test Script", "shots": []}

    mock_pipeline.run.return_value = {"component1": {"script": script_dict}}

    result = script_generator.generate(media)

    assert isinstance(result, ShootingScript)
    assert result.title == "Test Script"
    assert result.shots == []


def test_generate_with_kwargs(script_generator, mock_pipeline):
    """Test script generation with additional kwargs"""
    media = [Media.from_data("test")]
    expected_script = ShootingScript(title="Test Script")

    mock_pipeline.run.return_value = {"component1": {"script": expected_script}}

    _ = script_generator.generate(media, extra_param="value")

    mock_pipeline.run.assert_called_once_with({"test_component": {"media": [media[0]], "extra_param": "value"}})


def test_generate_pipeline_error(script_generator, mock_pipeline):
    """Test error handling when pipeline execution fails"""
    media = [Media.from_data("test")]
    mock_pipeline.run.side_effect = ValueError("Pipeline error")

    with pytest.raises(RuntimeError, match="Haystack pipeline execution failed: Pipeline error"):
        script_generator.generate(media)


def test_generate_invalid_output_type(script_generator, mock_pipeline):
    """Test error handling when pipeline returns invalid output type"""
    media = [Media.from_data("test")]
    mock_pipeline.run.return_value = {"component1": {"script": "invalid_type"}}

    with pytest.raises(ValueError, match="Pipeline output for key 'script' is not a ShootingScript"):
        script_generator.generate(media)


def test_generate_missing_output_key(script_generator, mock_pipeline):
    """Test error handling when pipeline output is missing the script key"""
    media = [Media.from_data("test")]
    mock_pipeline.run.return_value = {"component1": {"wrong_key": None}}

    with pytest.raises(ValueError, match="Pipeline output did not contain expected key 'script'"):
        script_generator.generate(media)
