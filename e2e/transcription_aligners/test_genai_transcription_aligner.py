import os

import pytest

from mosaico.audio_transcribers.transcription import Transcription
from mosaico.transcription_aligners.genai import GenAITranscriptionAligner


ORIGINAL_TEXT = """
Hi my name is Ali Ah. I'm going to tell you about artificial intelligence.
AI is transforming the way we live and work.
Many companies are investing in AI technologies.
They're finding ways to automate many tasks.
But there are some concerns about jobs and privacy.
We need to ensure that AI is developed responsibly.
The future of AI depends on making ethical choices today.
""".strip()

SRT_FILE = """
1
00:00:00,000 --> 00:00:01,500
Hi my name is Aliah

2
00:00:01,500 --> 00:00:03,500
Im gonna tell you about artficial intelegence

3
00:00:03,500 --> 00:00:06,000
AI is transforming the way we live an work

4
00:00:06,000 --> 00:00:09,000
Many companys are investin in AI technologies

5
00:00:09,000 --> 00:00:12,000
Theyre finding ways to automate meny tasks

6
00:00:12,000 --> 00:00:15,500
But there are sum concerms about jobs an privacy

7
00:00:15,500 --> 00:00:19,000
We need to ensure tht AI is developed respnsibly

8
00:00:19,000 --> 00:00:23,000
The futur of AI depends on making ethical choices today
""".strip()


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="Export OPENAI_API_KEY to run this test.")
def test_genai_transcription_aligner():
    original_transcription = Transcription.from_srt(SRT_FILE)
    aligner = GenAITranscriptionAligner(
        api_key=os.environ.get("OPENAI_API_KEY"), base_url=os.environ.get("OPENAI_BASE_URL")
    )
    aligned_transcription = aligner.align(original_transcription, ORIGINAL_TEXT)

    assert (
        " ".join(word.text for word in aligned_transcription.words).strip() == ORIGINAL_TEXT.replace("\n", " ").strip()
    )
    assert aligned_transcription.words[0].start_time == original_transcription.words[0].start_time
    assert aligned_transcription.words[-1].end_time == original_transcription.words[-1].end_time
