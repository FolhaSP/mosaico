import pytest

from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.transcription_aligners.sequence_matcher import SequenceMatcherTranscriptionAligner


@pytest.fixture
def aligner():
    return SequenceMatcherTranscriptionAligner()


def test_identical_transcription(aligner):
    # Test when transcription and original text are identical
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
    ]
    transcription = Transcription(words=words)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    assert result.words[1].start_time == 0.5
    assert result.words[1].end_time == 1.0


def test_word_replacement(aligner):
    # Test when words need to be replaced
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="werd", start_time=0.5, end_time=1.0),  # Misspelled
    ]
    transcription = Transcription(words=words)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"  # Corrected
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    assert result.words[1].start_time == 0.5
    assert result.words[1].end_time == 1.0


def test_word_deletion(aligner):
    # Test when words need to be deleted
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="beautiful", start_time=0.5, end_time=1.0),  # Extra word
        TranscriptionWord(text="world", start_time=1.0, end_time=1.5),
    ]
    transcription = Transcription(words=words)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    assert result.words[1].start_time == 1.0
    assert result.words[1].end_time == 1.5


def test_word_insertion_middle(aligner):
    # Test inserting words in the middle
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="world", start_time=1.0, end_time=1.5),
    ]
    transcription = Transcription(words=words)
    original_text = "hello beautiful world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 3
    assert result.words[0].text == "hello"
    assert result.words[1].text == "beautiful"
    assert result.words[2].text == "world"
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    # Verify the inserted word has timestamps between the surrounding words
    assert result.words[1].start_time >= 0.5
    assert result.words[1].end_time <= 1.0


def test_word_insertion_beginning(aligner):
    # Test inserting words at the beginning
    words = [TranscriptionWord(text="world", start_time=1.0, end_time=1.5)]
    transcription = Transcription(words=words)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    assert result.words[1].start_time == 1.0
    assert result.words[1].end_time == 1.5
    # The new word should have timestamps before the existing word
    assert result.words[0].end_time <= 1.0


def test_word_insertion_end(aligner):
    # Test inserting words at the end
    words = [TranscriptionWord(text="hello", start_time=0.0, end_time=0.5)]
    transcription = Transcription(words=words)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    # The new word should have timestamps after the existing word
    assert result.words[1].start_time >= 0.5


def test_empty_transcription(aligner):
    # Test with empty transcription but non-empty original text
    transcription = Transcription(words=[])
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    # Check that default timing is assigned
    assert result.words[0].start_time < result.words[1].start_time


def test_multiple_word_replacement(aligner):
    # Test replacing multiple words with different number of words
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="big", start_time=0.5, end_time=1.0),
        TranscriptionWord(text="world", start_time=1.0, end_time=1.5),
    ]
    transcription = Transcription(words=words)
    original_text = "hello beautiful amazing world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 4
    assert result.words[0].text == "hello"
    assert result.words[1].text == "beautiful"
    assert result.words[2].text == "amazing"
    assert result.words[3].text == "world"
    # Check timing distribution
    assert result.words[1].start_time >= 0.5
    assert result.words[2].end_time <= 1.0


def test_complex_scenario(aligner):
    # Test a more complex scenario with insertions, deletions, and replacements
    words = [
        TranscriptionWord(text="hallo", start_time=0.0, end_time=0.5),  # misspelled
        TranscriptionWord(text="beautiful", start_time=0.5, end_time=1.0),  # will be kept
        TranscriptionWord(text="whirled", start_time=1.0, end_time=1.5),  # misspelled
        TranscriptionWord(text="extra", start_time=1.5, end_time=2.0),  # will be deleted
    ]
    transcription = Transcription(words=words)
    original_text = "hello beautiful amazing world today"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 5
    assert result.words[0].text == "hello"  # replaced
    assert result.words[1].text == "beautiful"  # kept
    assert result.words[2].text == "amazing"  # inserted
    assert result.words[3].text == "world"  # replaced
    assert result.words[4].text == "today"  # inserted

    # Verify timing is reasonable
    assert 0.0 <= result.words[0].start_time < result.words[0].end_time
    assert result.words[0].end_time <= result.words[1].start_time
    assert result.words[1].end_time <= result.words[3].start_time


def test_from_srt_with_alignment(aligner):
    """Test alignment when loading from an SRT file"""
    srt_content = """1
00:00:00,000 --> 00:00:00,500
hallo

2
00:00:00,500 --> 00:00:01,000
whirled"""

    transcription = Transcription.from_srt(srt_content)
    original_text = "hello world"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 2
    assert result.words[0].text == "hello"
    assert result.words[1].text == "world"
    assert result.words[0].start_time == 0.0
    assert result.words[0].end_time == 0.5
    assert result.words[1].start_time == 0.5
    assert result.words[1].end_time == 1.0


def test_srt_with_punctuation(aligner):
    """Test alignment with punctuation in SRT"""
    srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello, world! How are
you today?"""

    transcription = Transcription.from_srt(srt_content)
    original_text = "Hello world How are you today"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 6
    assert result.words[0].text == "Hello"
    assert result.words[1].text == "world"
    assert result.words[5].text == "today"


def test_empty_original_text(aligner):
    """Test with an empty original text"""
    words = [
        TranscriptionWord(text="hello", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
    ]
    transcription = Transcription(words=words)
    original_text = ""

    result = aligner.align(transcription, original_text)

    # All words should be deleted, resulting in an empty transcription
    assert len(result.words) == 0


def test_long_complex_srt(aligner):
    """Test with a longer, more complex SRT file"""
    srt_content = """1
00:00:00,000 --> 00:00:02,000
artificial intelligence has evolved

2
00:00:02,000 --> 00:00:04,000
rapidly in the lost decades

3
00:00:04,000 --> 00:00:07,000
enabling machines to perform tax that
were once thought impossible

4
00:00:07,000 --> 00:00:10,000
from natural language processing to computer vision
and beyond
"""

    transcription = Transcription.from_srt(srt_content)
    original_text = (
        "artificial intelligence has evolved rapidly in the last decades enabling machines "
        "to perform tasks that were once thought impossible from natural language processing "
        "to computer vision and beyond"
    )

    result = aligner.align(transcription, original_text)

    assert "last" in [word.text for word in result.words]  # "lost" corrected to "last"
    assert "tasks" in [word.text for word in result.words]  # "tax" corrected to "tasks"

    # Verify the timeline is consistent
    for i in range(len(result.words) - 1):
        assert result.words[i].end_time <= result.words[i + 1].start_time


def test_word_segmentation_multiple_replace(aligner):
    """Test handling cases where one word becomes multiple words or vice versa"""
    words = [
        TranscriptionWord(text="cannot", start_time=0.0, end_time=0.5),
        TranscriptionWord(text="goto", start_time=0.5, end_time=1.0),
        TranscriptionWord(text="thestore", start_time=1.0, end_time=1.5),
    ]
    transcription = Transcription(words=words)
    original_text = "can not go to the store"

    result = aligner.align(transcription, original_text)

    assert len(result.words) == 6
    assert result.words[0].text == "can"
    assert result.words[1].text == "not"
    assert result.words[2].text == "go"
    assert result.words[3].text == "to"
    assert result.words[4].text == "the"
    assert result.words[5].text == "store"

    # Check timing distribution
    assert result.words[0].start_time < result.words[1].start_time
    assert result.words[1].end_time <= result.words[2].start_time
