import json
import os
from pathlib import Path

import pytest

from mosaico.media import Media
from mosaico.script_generators.news import NewsVideoScriptGenerator
from mosaico.video.project import VideoProject


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="Export OPENAI_API_KEY to run this test.")
def test_news_script_generation(samples_dir: Path) -> None:
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

    project = VideoProject.from_script_generator(script_generator, media=media)

    assert len(project.timeline) == 5
