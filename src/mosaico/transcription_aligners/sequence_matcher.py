from difflib import SequenceMatcher

from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.logging import get_logger
from mosaico.transcription_aligners.protocol import TranscriptionAligner


logger = get_logger(__name__)


class SequenceMatcherTranscriptionAligner(TranscriptionAligner):
    """Aligns transcriptions based on difflib.SequenceMatcher."""

    def align(self, transcription: Transcription, original_text: str) -> Transcription:  # noqa: C901, PLR0912, PLR0915
        """
        Aligns a transcription with an original text based on similarity scores.

        :param transcription: The transcription to align.
        :param original_text: The original text to align against.
        :return: The aligned transcription.
        """
        transcripted_text = " ".join(word.text for word in transcription.words)

        if transcripted_text == original_text:
            logger.debug("Transcription matches original text. No alignment needed.")
            return transcription

        words_with_time_ranges = transcription.words
        broken_words = [word.text for word in words_with_time_ranges]

        # 2. Split original text into words
        logger.debug("Splitting original text into words.")
        original_words = original_text.split()

        # 3. Use SequenceMatcher to identify differences
        logger.debug("Using SequenceMatcher to identify differences.")
        matcher = SequenceMatcher(None, broken_words, original_words)
        opcodes = matcher.get_opcodes()
        logger.debug(f"SequenceMatcher found {len(opcodes)} differences")

        # 4. Apply corrections while preserving time ranges
        logger.debug("Applying corrections while preserving time ranges.")
        fixed_words = []

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                # No change needed, keep original words and time ranges
                logger.debug("No change needed, keeping original words and time ranges.")
                for word in words_with_time_ranges[i1:i2]:
                    fixed_words.append(word.copy())

            elif tag == "replace":
                # Replace words but adapt their time ranges
                logger.debug("Replacing words and adapting their time ranges.")
                broken_chunk = broken_words[i1:i2]
                original_chunk = original_words[j1:j2]
                time_ranges = [(word.start_time, word.end_time) for word in words_with_time_ranges[i1:i2]]

                if len(broken_chunk) == len(original_chunk):
                    # One-to-one replacement - keep original time ranges
                    for i in range(len(broken_chunk)):
                        start_time, end_time = time_ranges[i]
                        fixed_word = TranscriptionWord(text=original_chunk[i], start_time=start_time, end_time=end_time)
                        fixed_words.append(fixed_word)

                else:
                    # Different lengths - redistribute time ranges
                    chunk_start = time_ranges[0][0]  # First word's start time
                    chunk_end = time_ranges[-1][1]  # Last word's end time
                    total_duration = chunk_end - chunk_start
                    word_count = len(original_chunk)

                    # Distribute time evenly for each new word
                    if word_count > 0:
                        word_duration = total_duration / word_count
                        for i, word in enumerate(original_chunk):
                            word_start = chunk_start + (i * word_duration)
                            word_end = word_start + word_duration
                            fixed_word = TranscriptionWord(text=word, start_time=word_start, end_time=word_end)
                            fixed_words.append(fixed_word)

            elif tag == "delete":
                # Skip these words (they don't exist in original)
                logger.debug("Skipping deleted word.")
                pass

            elif tag == "insert":
                # New words - need to assign appropriate time ranges
                logger.debug("Inserting new words.")
                if i1 > 0 and i1 < len(words_with_time_ranges):
                    # Insert between existing words
                    prev_word_end = words_with_time_ranges[i1 - 1].end_time
                    next_word_start = words_with_time_ranges[i1].start_time
                    available_gap = next_word_start - prev_word_end

                    # Distribute the available gap among the new words
                    word_count = j2 - j1
                    if available_gap > 0 and word_count > 0:
                        word_duration = available_gap / word_count
                        for i in range(word_count):
                            word_start = prev_word_end + (i * word_duration)
                            word_end = word_start + word_duration
                            fixed_word = TranscriptionWord(
                                text=original_words[j1 + i], start_time=word_start, end_time=word_end
                            )
                            fixed_words.append(fixed_word)
                    else:
                        # No gap available, use prev_word_end for all inserted words
                        for i in range(j1, j2):
                            fixed_word = TranscriptionWord(
                                text=original_words[i], start_time=prev_word_end, end_time=prev_word_end
                            )
                            fixed_words.append(fixed_word)

                elif i1 == 0 and words_with_time_ranges:
                    # Insert at the beginning
                    first_word_start = words_with_time_ranges[0].start_time
                    insert_duration = min(0.5, first_word_start) if first_word_start > 0 else 0.1
                    word_count = j2 - j1

                    if word_count > 0:
                        word_duration = insert_duration / word_count
                        for i in range(word_count):
                            word_start = max(0, first_word_start - insert_duration + (i * word_duration))
                            word_end = word_start + word_duration
                            fixed_word = TranscriptionWord(
                                text=original_words[j1 + i], start_time=word_start, end_time=word_end
                            )
                            fixed_words.append(fixed_word)

                elif i1 >= len(words_with_time_ranges) and words_with_time_ranges:
                    # Insert at the end
                    last_word_end = words_with_time_ranges[-1].end_time
                    word_duration = 0.1  # Default duration for appended words
                    for i in range(j1, j2):
                        word_start = last_word_end + ((i - j1) * word_duration)
                        word_end = word_start + word_duration
                        fixed_word = TranscriptionWord(text=original_words[i], start_time=word_start, end_time=word_end)
                        fixed_words.append(fixed_word)

                else:
                    # Empty transcription case
                    word_duration = 0.5
                    for i in range(j1, j2):
                        word_start = i * word_duration
                        word_end = word_start + word_duration
                        fixed_word = TranscriptionWord(text=original_words[i], start_time=word_start, end_time=word_end)
                        fixed_words.append(fixed_word)

        return Transcription(words=fixed_words)
