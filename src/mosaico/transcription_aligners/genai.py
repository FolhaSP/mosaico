from typing import Any

import instructor
import litellm

from mosaico.audio_transcribers.transcription import Transcription
from mosaico.logging import get_logger
from mosaico.transcription_aligners.protocol import TranscriptionAligner


logger = get_logger(__name__)

SYSTEM_PROMPT = """
# SRT Transcription Correction

## CRITICAL RULES
1. **KEEP EXACT NUMBER OF SEGMENTS** - Must have exactly same number of segments as original SRT
2. **KEEP EXACT TIMECODES** - Use timecodes only from original SRT
3. **USE ORIGINAL TEXT ONLY** - Replace all words with original document text

## Step-by-Step Process
1. Count the number of segments in original SRT (N) - output must have EXACTLY N segments
2. Copy all timecodes exactly as they appear in the SRT
3. Replace each segment's text with words from the original document in order
4. Do NOT add ANY extra segments or extend timecodes

## Word Distribution Rules
- Distribute original text across existing segments only
- If original text has different word count:
  - May need to put multiple words in some segments
  - May need to combine/split words to fit segment count
  - NEVER exceed the original number of segments
  - NEVER extend the end timecode

## Example

**Original Text:**
"Weather forecast for today: Sunny with a high of 75 degrees. Expect clear skies throughout the afternoon."

**Original SRT (8 segments):**
```
1
00:00:01,500 --> 00:00:02,300
Weather

2
00:00:02,300 --> 00:00:02,800
forecast

3
00:00:02,800 --> 00:00:03,200
for

4
00:00:03,200 --> 00:00:03,600
tue

5
00:00:03,600 --> 00:00:04,200
sunny

6
00:00:04,200 --> 00:00:05,100
hi of 72

7
00:00:05,100 --> 00:00:06,300
expect partly cloudy

8
00:00:06,300 --> 00:00:07,500
in afternoon
```

**CORRECT OUTPUT (8 segments):**
```
1
00:00:01,500 --> 00:00:02,300
Weather

2
00:00:02,300 --> 00:00:02,800
forecast

3
00:00:02,800 --> 00:00:03,200
for

4
00:00:03,200 --> 00:00:03,600
today:

5
00:00:03,600 --> 00:00:04,200
Sunny

6
00:00:04,200 --> 00:00:05,100
with a high of 75 degrees.

7
00:00:05,100 --> 00:00:06,300
Expect clear skies

8
00:00:06,300 --> 00:00:07,500
throughout the afternoon.
```

Note: Exact same number of segments (8), exact same timecodes, but text is corrected using only the original document content.
"""

USER_PROMPT = """
I need to correct an SRT subtitle file using the original text as the source of truth.

## Original Document Text
```
{original_text}
```

## Current SRT File
```
{transcription_srt}
```

Please correct the SRT file by:
1. Keeping all timecodes exactly as they appear in my SRT file
2. Replacing all text with the correct words from my original document
3. Maintaining the same number of segments as the original SRT
4. Not adding any new segments or extending the end time
5. Combining or splitting words as needed to fit the segment count exactly as in the original document

Return the corrected SRT file with the exact same number of segments and timecodes but with the text replaced using only the original document content.
""".strip()


class GenAITranscriptionAligner(TranscriptionAligner):
    """Aligns transcription with original text using generative AI."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        model_params: dict[str, Any] | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 120,
    ) -> None:
        self.model = model
        self.model_params = model_params
        self.client = instructor.from_litellm(litellm.completion, api_key=api_key, base_url=base_url, timeout=timeout)
        logger.debug(f"Initialized GenAI transcription aligner with model '{model}'.")

    def align(self, transcription: Transcription, original_text: str) -> Transcription:
        """
        Aligns a transcription using generative AI based on an original text.

        :param transcription: Transcription with timing information.
        :param original_text: Original script text.
        :return: A new transcription with aligned text and timing.
        """
        model_params = self.model_params or {"temperature": 0}
        logger.debug(f"Aligning transcription with GenAI model '{self.model}', parameters: {model_params}")
        fixed_transcription = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT.format(
                        transcription_srt=transcription.to_srt(), original_text=original_text
                    ),
                },
            ],
            response_model=str,
            **model_params,
        )

        return Transcription.from_srt(fixed_transcription)
