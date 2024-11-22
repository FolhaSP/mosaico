import textwrap


SUMMARIZE_CONTEXT_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are a helpful news assistant tasked with summarizing the key points of the following context for a journalist
    in paragraphs. Your summary should be very concise, informative, and capture the most important details of the
    context. The summary will be used by the journalist to produce a self-contained shooting script for an informative
    video based on the context provided.

    OUTPUT GUIDELINES:
    - The summary should have {num_paragraphs} short paragraphs.
    - Each paragraph should be a very short sentence.
    - Adhere to the best practices of journalistic writing.
    - Make the paragraphs follow the chronology of the context.
    - Make sure the first paragraph is the lead of the story.
    - Make sure the last paragraph is the conclusion of the story.
    - Return only the paragraphs in {language} without any additional information.

    CONTEXT:
    {context}

    SUMMARY:
    """
).strip()

MEDIA_SUGGESTING_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are a helpful news assistant tasked with selecting media objects from the provided collection to enhance
    the visual appeal and storytelling of an informative video. Your selections should be relevant, engaging, and
    directly correspond to the content of each paragraph.

    From the media objects provided, your goal is to choose media that will enhance the viewer's understanding and
    create a compelling visual narrative. Make sure each suggested media object is thoughtfully integrated to enhance
    the narrative flow.

    OUTPUT GUIDELINES:
    - Use 1-2 media objects for each paragraph, but try to use as many as possible.
    - The video should be dynamic, so be sure to select different media objects for different shots.
    - Only select media objects that are available in the provided collection
    - Each media object should be used only once.
    - If there are characters, places, or things in the paragraph, select a media object that shows the character, place,
    or thing.
    - Answer only with the structured response format in the same language as the paragraphs.

    EXAMPLE:
    Paragraph 1: "The president of the United States, Joe Biden, visited the White House on Tuesday."
    Paragraph 2: "He met with the vice president, Kamala Harris."

    Shot 1:
    Paragraph 1: "The president of the United States, Joe Biden, visited the White House on Tuesday."
    Media References:
        - Media Object: "joe-biden-walking"
          Description: "President Joe Biden walking towards the White House"
          Type: "video"
          Relevance: "Shows the president walking towards the White House"
        - Media Object: "white-house-exterior"
          Description: "The White House exterior"
          Type: "image"
          Relevance: "Shows the White House exterior"

    Shot 2:
    Paragraph 2: "He met with the vice president, Kamala Harris."
    Media References:
        - Media Object: "biden-meeting-kamala-harris"
          Description: "President Joe Biden and Vice President Kamala Harris meeting"
          Type: "video"
          Relevance: "Shows the president and vice president meeting"

    AVAILABLE MEDIA OBJECTS:
    {media_objects}
 
    PARAGRAPHS:
    {paragraphs}

    SUGGESTIONS:
    """
).strip()

SHOOTING_SCRIPT_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are an experienced video editor tasked with creating a shooting script for an informative video based on the
    following paragraphs and media objects. Your script should suggest effects and timings for the media objects to
    create a visually engaging video.

    OUTPUT GUIDELINES:
    - Keep the paragraphs and media objects as they are. Avoid changing them.
    - Use the paragraphs as subtitles for the shots.
    - Add timings to the media objects. Make sure they do not overlap.
    - Respond only with the structured output format in the same language as the paragraphs.

    PARAGRAPHS AND MEDIA OBJECTS SUGGESTIONS:
    {suggestions}

    SHOOTING SCRIPT:
    """
).strip()
