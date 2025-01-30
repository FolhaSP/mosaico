from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pydantic_extra_types.language_code import LanguageAlpha2

from mosaico.media import Media
from mosaico.script_generators.news.prompts import (
    MEDIA_SUGGESTING_PROMPT,
    SHOOTING_SCRIPT_PROMPT,
    SUMMARIZE_CONTEXT_PROMPT,
)
from mosaico.script_generators.script import ShootingScript


if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


class ParagraphMediaSuggestion(BaseModel):
    """A media suggestion for a paragraph."""

    paragraph: str
    """The paragraph content to which the media object corresponds."""

    media_ids: list[str]
    """The media IDs for the shot."""

    relevance: str
    """How it relates to the specific paragraph."""


class ParagraphMediaSuggestions(BaseModel):
    """A list of media suggestions for paragraphs."""

    suggestions: list[ParagraphMediaSuggestion]
    """The list of paragraph media suggestions."""


class NewsVideoScriptGenerator:
    def __init__(
        self,
        context: str,
        model: str = "claude-3-5-sonnet-20241022",
        model_params: dict[str, Any] | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        num_paragraphs: int = 5,
        language: str | LanguageAlpha2 | None = None,
        timeout: float = 120,
    ) -> None:
        try:
            import instructor
            import litellm
        except ImportError:
            raise ImportError(
                "The 'instructor' and 'litellm' packages are required for using the NewsVideoScriptGenerator."
            )
        self.context = context
        self.model = model
        self.model_params = model_params or {"temperature": 0}
        self.num_paragraphs = num_paragraphs
        self.language = LanguageAlpha2(language) if language is not None else LanguageAlpha2("en")
        self.client = instructor.from_litellm(litellm.completion, api_key=api_key, base_url=base_url, timeout=timeout)

    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """
        Generate scenes for a project with AI.

        :param media: The list of media objects.
        :param kwargs: Additional context for the scene generation.
        :return: A tuple containing the scenes and assets generated from the media files.
        """
        paragraphs = self._summarize_context(self.context, self.num_paragraphs, self.language)
        suggestions = self._suggest_paragraph_media(paragraphs, media)
        shooting_script = self._generate_shooting_script(suggestions)
        return shooting_script

    def _summarize_context(self, context: str, num_paragraphs: int, language: LanguageAlpha2) -> list[str]:
        """
        Summarize the context to provide a brief overview of the article.
        """
        paragraphs_prompt = SUMMARIZE_CONTEXT_PROMPT.format(
            context=context, num_paragraphs=num_paragraphs, language=language.name
        )
        paragraphs = self._fetch_completion(paragraphs_prompt, response_type=str)
        return paragraphs

    def _suggest_paragraph_media(self, paragraphs: list[str], media: Sequence[Media]) -> list[ParagraphMediaSuggestion]:
        """
        Suggest media usage based on the media objects.
        """
        formatted_media = _build_media_string(media)
        prompt = MEDIA_SUGGESTING_PROMPT.format(paragraphs=paragraphs, media_objects=formatted_media)
        suggestions = self._fetch_completion(prompt, response_type=ParagraphMediaSuggestions)
        return suggestions.suggestions

    def _generate_shooting_script(self, suggestions: list[ParagraphMediaSuggestion]) -> ShootingScript:
        """
        Generate the shooting script.
        """
        prompt = SHOOTING_SCRIPT_PROMPT.format(suggestions=suggestions)
        shooting_script = self._fetch_completion(prompt, response_type=ShootingScript)
        return shooting_script

    def _fetch_completion(
        self,
        user_message: str,
        system_message: str = "You are a helpful assistant.",
        *,
        response_type: type[Any],
        **kwargs: Any,
    ) -> Any:
        """
        Fetch a completion from the AI model.
        """
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
        model_params = self.model_params | kwargs
        return self.client.chat.completions.create(
            model=self.model, messages=messages, response_model=response_type, **model_params
        )


def _format_media(media: Media, index: int) -> str:
    """
    Format a media object as a string for display.
    """
    description = media.description
    mime_type = media.mime_type or "text/plain"
    return f"Media ID: {media.id}\nMIME type: {mime_type}\nDescription: {description}\n\n"


def _build_media_string(medias: Sequence[Media]) -> str:
    """
    Build context and media strings for generating a script.
    """
    media_str = ""
    for index, media in enumerate(medias):
        fmt_media = _format_media(media, index)
        media_str += fmt_media
    return media_str
