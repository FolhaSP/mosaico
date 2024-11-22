import textwrap


SUMMARIZE_CONTEXT_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are a helpful news assistant tasked with summarizing the key points of the following context for a journalist
    in paragraphs. Your summary should be concise, informative, and capture the most important details of the context.
    The summary will be used by the journalist to produce a self-contained shooting script for an informative video
    based on the context provided.

    OUTPUT GUIDELINES:
    - The summary should have {num_paragraphs} short paragraphs.
    - Each paragraph should be 1-2 sentences long.
    - Adhere to the best practices of journalistic writing.
    - Return only the paragraphs in {language} without any additional information.

    CONTEXT:
    {context}

    SUMMARY:
    """
).strip()

MEDIA_SUGGESTING_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are a helpful news assistant tasked with selecting media objects that best represent each paragraph's content.
    Your goal is to suggest relevant media that can be combined to create a rich, layered visual narrative for each
    paragraph.

    OUTPUT GUIDELINES:
    For each paragraph, provide:
    - The complete paragraph text
    - A list of 2-3 relevant media IDs from the available collection
    - The type of each media (image, video, or audio)
    - A clear explanation of how each media relates to the paragraph content

    Format each suggestion as:
    {{
        "paragraph": "<full paragraph text>",
        "media_ids": ["id1", "id2", "id3"],
        "type": "image|video|audio",
        "relevance": "Explanation of how this media relates to the paragraph"
    }}

    EXAMPLE:
    {{
        "paragraph": "The president addressed the nation from the White House.",
        "media_ids": ["president-podium", "white-house-exterior"],
        "type": "image",
        "relevance": "Shows the president at the podium with the White House as context"
    }}

    REQUIREMENTS:
    - Only use media IDs that exist in the provided collection
    - Select media that can be layered effectively (e.g., background + foreground)
    - Consider visual compatibility between selected media
    - Ensure each media selection directly supports the paragraph's narrative

    PARAGRAPHS:
    {paragraphs}

    AVAILABLE MEDIA OBJECTS:
    {media_objects}

    SUGGESTIONS:
    """
).strip()

SHOOTING_SCRIPT_PROMPT = textwrap.dedent(
    """
    INSTRUCTIONS:
    You are an experienced video editor creating a shooting script that combines multiple media elements
    per shot to create visually rich compositions. Each paragraph should become one cohesive shot that
    layers multiple media elements.

    OUTPUT GUIDELINES:
    Create a ShootingScript with the following structure:
    - title: String describing the overall story
    - description: Brief overview of the video content
    - shots: List of Shot objects, where each Shot contains:
        * number: Sequential shot number
        * description: Description of the visual composition
        * subtitle: The paragraph text as narration
        * media_references: List of ShotMediaReference objects containing:
            - media_id: ID of the media to use
            - type: "image" or "video"
            - start_time: When this media should appear (in seconds)
            - end_time: When this media should end (in seconds)
            - effects: List of effects to apply (especially for images)

    TIMING GUIDELINES:
    - Each shot should be 3-5 seconds total
    - Media references within a shot can overlap
    - Stagger media start/end times for dynamic transitions
    - Use effects to add movement to static images

    EXAMPLE STRUCTURE:
    {{
        "title": "Story Title",
        "description": "Video overview",
        "shots": [
            {{
                "number": 1,
                "description": "Layered shot showing president at podium with White House background",
                "subtitle": "The president addressed the nation from the White House",
                "media_references": [
                    {{
                        "media_id": "white-house-exterior",
                        "type": "image",
                        "start_time": 0.0,
                        "end_time": 5.0,
                        "effects": ["ken_burns_zoom_in"]
                    }},
                    {{
                        "media_id": "president-podium",
                        "type": "video",
                        "start_time": 1.0,
                        "end_time": 4.0,
                        "effects": []
                    }}
                ]
            }}
        ]
    }}

    PARAGRAPHS AND MEDIA SUGGESTIONS:
    {suggestions}

    SHOOTING SCRIPT:
    """
).strip()
