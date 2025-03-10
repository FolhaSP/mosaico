import json
import os
from pathlib import Path

import pytest

from mosaico.media import Media
from mosaico.project import Project
from mosaico.rendering.engines.moviepy.engine import MoviepyRenderingEngine
from mosaico.script_generators.news import NewsVideoScriptGenerator


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="Export OPENAI_API_KEY to run this test.")
def test_news_script_generation(samples_dir: Path, tmp_path: Path) -> None:
    """
    Test the script generation for a news video project.
    """
    news_articles_dir = samples_dir / "news_articles"
    context = (news_articles_dir / "articles.txt").read_text()
    raw_media = json.loads((news_articles_dir / "related_media.json").read_text())
    media = [Media.model_validate(m) for m in raw_media]

    script_generator = NewsVideoScriptGenerator(
        context=context,
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
        num_paragraphs=5,
        language="pt",
    )

    project = Project.from_script_generator(script_generator, media=media).with_fps(10)

    assert len(project.timeline.tracks) == 5

    # Assert that effects are being suggested by AI and at least one of them is
    # a movement-related event, such as "pan_left" or "zoom_out".
    # for event in project.timeline:
    #     for ref in event.asset_references:
    #         if ref.asset_type == "image":
    #             assert any(fx.type.startswith(("pan_", "zoom_")) for fx in ref.effects)
    #             assert not any(fx.type.startswith(("fade_", "crossfade_")) for fx in ref.effects)
    output_file = tmp_path / "news.mp4"
    engine = MoviepyRenderingEngine()
    engine.render_project(project, output_file)
    # render_video(project, output_file)
