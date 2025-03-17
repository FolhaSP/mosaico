from unittest.mock import patch

import pytest

from mosaico.media import Media
from mosaico.script_generators.news.generator import NewsVideoScriptGenerator, ParagraphMediaSuggestion, ShootingScript
from mosaico.script_generators.script import Shot, ShotMediaReference


@pytest.fixture
def mock_media():
    """Create a list of mock media objects."""
    media1 = Media.from_data(data="test data 1", mime_type="image/jpeg", metadata={"description": "Test image 1"})
    media1.id = "media1"

    media2 = Media.from_data(data="test data 2", mime_type="image/png", metadata={"description": "Test image 2"})
    media2.id = "media2"

    media3 = Media.from_data(data="test data 3", mime_type="video/mp4", metadata={"description": "Test video"})
    media3.id = "media3"

    return [media1, media2, media3]


@pytest.fixture
def mock_paragraphs():
    """Mock paragraphs returned from _summarize_context."""
    return [
        "First paragraph about news topic.",
        "Second paragraph with more details.",
        "Third paragraph with conclusion.",
    ]


@pytest.fixture
def mock_suggestions():
    """Mock suggestions returned from _suggest_paragraph_media."""
    return [
        ParagraphMediaSuggestion(
            paragraph="First paragraph about news topic.", media_ids=["media1"], relevance="High relevance to the topic"
        ),
        ParagraphMediaSuggestion(
            paragraph="Second paragraph with more details.",
            media_ids=["media2", "media3"],
            relevance="Medium relevance to the topic",
        ),
    ]


@pytest.fixture
def mock_shooting_script():
    """Mock shooting script returned from _generate_shooting_script."""
    return ShootingScript(
        title="Test News Video",
        description="A test news video",
        shots=[
            Shot(
                number=1,
                description="Opening shot",
                subtitle="Introduction to the topic",
                media_references=[
                    ShotMediaReference(media_id="media1", type="image", start_time=0.0, end_time=3.0, effects=[])
                ],
            ),
            Shot(
                number=2,
                description="Second shot",
                subtitle="More details",
                media_references=[
                    ShotMediaReference(media_id="media2", type="image", start_time=3.0, end_time=6.0, effects=[]),
                    ShotMediaReference(
                        media_id="media3", type="video", start_time=6.0, end_time=10.0, effects=["fade_in"]
                    ),
                ],
            ),
        ],
    )


@patch.object(NewsVideoScriptGenerator, "_summarize_context")
@patch.object(NewsVideoScriptGenerator, "_suggest_paragraph_media")
@patch.object(NewsVideoScriptGenerator, "_generate_shooting_script")
def test_generate_adds_effects_to_images(
    mock_generate_shooting_script,
    mock_suggest_paragraph_media,
    mock_summarize_context,
    mock_media,
    mock_paragraphs,
    mock_suggestions,
    mock_shooting_script,
):
    """Test that the generate method adds effects to images without existing effects."""
    # Arrange
    mock_summarize_context.return_value = mock_paragraphs
    mock_suggest_paragraph_media.return_value = mock_suggestions
    mock_generate_shooting_script.return_value = mock_shooting_script

    generator = NewsVideoScriptGenerator(context="Test context")

    # Act
    result = generator.generate(mock_media)

    # Assert
    # Check that all image media references have effects
    for shot in result.shots:
        for media_ref in shot.media_references:
            if media_ref.type == "image":
                assert media_ref.effects, f"Media reference {media_ref.media_id} should have effects"
                assert (
                    len(media_ref.effects) > 0
                ), f"Media reference {media_ref.media_id} should have at least one effect"
                assert isinstance(media_ref.effects[0], str), "Effect should be a string"
                # Check that the effect is one of the valid VideoEffectType values
                assert any(
                    media_ref.effects[0].startswith(prefix) for prefix in ["zoom_", "pan_"]
                ), f"Effect {media_ref.effects[0]} should start with 'zoom_' or 'pan_'"


@patch.object(NewsVideoScriptGenerator, "_summarize_context")
@patch.object(NewsVideoScriptGenerator, "_suggest_paragraph_media")
@patch.object(NewsVideoScriptGenerator, "_generate_shooting_script")
@patch("mosaico.script_generators.news.generator._random_effect")
def test_generate_uses_random_effect(
    mock_random_effect,
    mock_generate_shooting_script,
    mock_suggest_paragraph_media,
    mock_summarize_context,
    mock_media,
    mock_paragraphs,
    mock_suggestions,
    mock_shooting_script,
):
    """Test that the generate method uses _random_effect to add effects."""
    # Arrange
    mock_summarize_context.return_value = mock_paragraphs
    mock_suggest_paragraph_media.return_value = mock_suggestions
    mock_generate_shooting_script.return_value = mock_shooting_script
    mock_random_effect.return_value = "zoom_in"  # Mock the random effect

    generator = NewsVideoScriptGenerator(context="Test context")

    # Act
    result = generator.generate(mock_media)

    # Assert
    # Check that the random effect was used
    assert result.shots[0].media_references[0].effects == ["zoom_in"]
    # Check that _random_effect was called the correct number of times
    # We expect it to be called once for each image media reference without effects
    assert mock_random_effect.call_count == 2
