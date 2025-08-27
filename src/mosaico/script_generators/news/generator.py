import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, get_args

import instructor  # type: ignore
import litellm  # type: ignore
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic_extra_types.language_code import LanguageAlpha2

from mosaico.effects.types import VideoEffectType
from mosaico.media import Media
from mosaico.script_generators.news.prompts import (
    MEDIA_SUGGESTING_PROMPT,
    REPLACEMENT_PROMPT,
    SHOOTING_SCRIPT_PROMPT,
    SUMMARIZE_CONTEXT_PROMPT,
)
from mosaico.script_generators.script import ShootingScript, Shot, ShotMediaReference


if TYPE_CHECKING:  # pragma: no cover
    from openai.types.chat import ChatCompletionMessageParam


class ParagraphMediaSuggestion(BaseModel):
    """A media suggestion for a paragraph."""

    paragraph: str
    media_ids: list[str]
    relevance: str


class ParagraphMediaSuggestions(BaseModel):
    """A list of media suggestions for paragraphs."""

    suggestions: list[ParagraphMediaSuggestion] = Field(default_factory=list)


class ShotReplacementSuggestion(BaseModel):
    """Replacement media IDs for a specific shot."""

    shot_number: int
    media_ids: list[str]


class ShotReplacementSuggestions(BaseModel):
    """Container for shot replacement suggestions."""

    replacements: list[ShotReplacementSuggestion] = Field(default_factory=list)


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
        *,
        enforce_unique_media: bool = True,
    ) -> None:
        """
        Create the generator.

        enforce_unique_media: Ensure each media_id is used at most once in final script.
        """
        self.context = context
        self.model = model
        self.model_params = model_params or {"temperature": 0}
        self.num_paragraphs = num_paragraphs
        self.language = LanguageAlpha2(language) if language is not None else LanguageAlpha2("en")
        self.client = instructor.from_litellm(litellm.completion, api_key=api_key, base_url=base_url, timeout=timeout)
        self.enforce_unique_media = enforce_unique_media
        self.max_unsuccessful_replacement_rounds = 3

    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """Generate the shooting script with optional uniqueness enforcement."""
        paragraphs = self._summarize_context(self.context, self.num_paragraphs, self.language)
        suggestions = self._suggest_paragraph_media(paragraphs, media)
        shooting_script = self._generate_shooting_script(suggestions)

        if self.enforce_unique_media:
            shooting_script = self._ensure_unique_media_with_replacements(shooting_script, media)

        for shot in shooting_script.shots:
            for media_ref in shot.media_references:
                if media_ref.type == "image" and not media_ref.effects:
                    media_ref.effects = [_random_effect()]

        return shooting_script

    def _summarize_context(self, context: str, num_paragraphs: int, language: LanguageAlpha2) -> list[str]:
        paragraphs_prompt = SUMMARIZE_CONTEXT_PROMPT.format(
            context=context, num_paragraphs=num_paragraphs, language=language.name
        )
        return self._fetch_completion(paragraphs_prompt, response_type=list[str])

    def _suggest_paragraph_media(self, paragraphs: list[str], media: Sequence[Media]) -> list[ParagraphMediaSuggestion]:
        formatted_media = _build_media_string(media)
        formatted_paragraphs = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(paragraphs))
        prompt = MEDIA_SUGGESTING_PROMPT.format(paragraphs=formatted_paragraphs, media_objects=formatted_media)
        suggestions = self._fetch_completion(prompt, response_type=ParagraphMediaSuggestions)
        return suggestions.suggestions

    def _generate_shooting_script(self, suggestions: list[ParagraphMediaSuggestion]) -> ShootingScript:
        formatted_suggestions = "\n".join(
            f"Paragraph: {s.paragraph}\nMedia IDs: {', '.join(s.media_ids)}\nRelevance: {s.relevance}\n"
            for s in suggestions
        )
        prompt = SHOOTING_SCRIPT_PROMPT.format(suggestions=formatted_suggestions)
        return self._fetch_completion(prompt, response_type=ShootingScript)

    def _fetch_completion(
        self,
        user_message: str,
        system_message: str = "You are a helpful assistant.",
        *,
        response_type: type[Any],
        **kwargs: Any,
    ) -> Any:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
        model_params = self.model_params | kwargs
        return self.client.chat.completions.create(
            model=self.model, messages=messages, response_model=response_type, **model_params
        )

    def _ensure_unique_media_with_replacements(
        self, shooting_script: ShootingScript, media_pool: Sequence[Media]
    ) -> ShootingScript:
        """
        Enforce uniqueness.

        1. Global dedupe keeps first occurrence of each media_id.
        2. Iteratively request replacements to fill missing slots (based on original per-shot counts).
        3. Unlimited attempts while progress occurs; count only unsuccessful rounds.
        4. After self.max_unsuccessful_replacement_rounds consecutive unsuccessful rounds OR no available media, raise.
        5. Never drop shots; either all targets are filled or we error.
        """
        media_by_id = {m.id: m for m in media_pool}
        original_counts = {s.number: len(s.media_references) for s in shooting_script.shots}
        self._initial_global_dedupe(shooting_script)

        # Helper
        def total_missing() -> int:
            return sum(missing for _, missing in self._shots_needing_replacements(shooting_script, original_counts))

        unsuccessful_rounds = 0
        while True:
            _ = total_missing()
            needs = self._shots_needing_replacements(shooting_script, original_counts)
            if not needs:
                break
            available_ids = self._remaining_available_ids(shooting_script, media_pool)
            if not available_ids:
                raise RuntimeError("Error 500: Sem fotos suficientes")

            replacements = self._request_replacements(needs, available_ids, media_by_id)
            applied = False
            if replacements:
                applied = self._apply_replacements(shooting_script, replacements, original_counts, media_by_id)
            if applied:
                unsuccessful_rounds = 0
            else:
                unsuccessful_rounds += 1
                if unsuccessful_rounds >= self.max_unsuccessful_replacement_rounds:
                    raise RuntimeError("Error 500: Sem fotos suficientes")
        return shooting_script

    def _initial_global_dedupe(self, shooting_script: ShootingScript) -> None:
        seen: set[str] = set()
        for shot in shooting_script.shots:
            uniq = []
            for ref in shot.media_references:
                if ref.media_id in seen:
                    continue
                seen.add(ref.media_id)
                uniq.append(ref)
            shot.media_references = uniq

    def _remaining_available_ids(self, shooting_script: ShootingScript, media_pool: Sequence[Media]) -> list[str]:
        used = {ref.media_id for s in shooting_script.shots for ref in s.media_references}
        return [m.id for m in media_pool if m.id not in used]

    def _shots_needing_replacements(
        self, shooting_script: ShootingScript, original_counts: dict[int, int]
    ) -> list[tuple[Shot, int]]:
        needs: list[tuple[Shot, int]] = []
        for shot in shooting_script.shots:
            target = original_counts.get(shot.number, 0)
            missing = max(0, target - len(shot.media_references))
            if missing:
                needs.append((shot, missing))
        return needs

    def _request_replacements(
        self,
        needs: list[tuple[Shot, int]],
        available_ids: list[str],
        media_by_id: dict[str, Media],
    ) -> ShotReplacementSuggestions | None:
        shots_needed_str = "\n".join(
            f"Shot {shot.number} | Needed: {missing} | Subtitle: {shot.subtitle}" for shot, missing in needs
        )
        available_media_str = "\n".join(f"{mid}: {media_by_id[mid].description}" for mid in available_ids)
        prompt = REPLACEMENT_PROMPT.format(available_media=available_media_str, shots_needed=shots_needed_str)
        try:
            return self._fetch_completion(prompt, response_type=ShotReplacementSuggestions)
        except Exception:
            return None

    def _apply_replacements(
        self,
        shooting_script: ShootingScript,
        replacements: ShotReplacementSuggestions,
        original_counts: dict[int, int],
        media_by_id: dict[str, Media],
    ) -> bool:
        shot_map = {s.number: s for s in shooting_script.shots}
        used_ids = {ref.media_id for s in shooting_script.shots for ref in s.media_references}
        applied_any = False
        for rep in replacements.replacements:
            shot = shot_map.get(rep.shot_number)
            if not shot:
                continue
            missing = max(0, original_counts.get(shot.number, 0) - len(shot.media_references))
            if not missing:
                continue
            candidates: list[str] = []
            for mid in rep.media_ids:
                if len(candidates) >= missing:
                    break
                if mid in used_ids or mid not in media_by_id:
                    continue
                candidates.append(mid)
                used_ids.add(mid)
            if not candidates:
                continue
            self._append_replacement_refs(shot, candidates, media_by_id)
            applied_any = True
        return applied_any

    def _append_replacement_refs(
        self,
        shot: Shot,
        media_ids: list[str],
        media_by_id: dict[str, Media],
        default_duration: float = 3.0,
    ) -> None:
        current_end = max((ref.end_time for ref in shot.media_references), default=0.0)
        for mid in media_ids:
            media_obj = media_by_id[mid]
            start = current_end
            end = start + default_duration
            mtype = "image" if (media_obj.mime_type or "").startswith("image") else "video"
            ref = ShotMediaReference(
                media_id=mid,
                type=mtype,  # type: ignore[arg-type]
                start_time=start,
                end_time=end,
                effects=[],
            )
            shot.media_references.append(ref)
            current_end = end


def _format_media(media: Media) -> str:
    description = media.description
    mime_type = media.mime_type or "text/plain"
    return f"Media ID: {media.id}\nMIME type: {mime_type}\nDescription: {description}\n\n"


def _build_media_string(medias: Sequence[Media]) -> str:
    media_str = ""
    for media in medias:
        media_str += _format_media(media)
    return media_str


def _random_effect() -> VideoEffectType:
    return random.choice([fx for fx in get_args(VideoEffectType) if fx.startswith(("zoom_", "pan_"))])
