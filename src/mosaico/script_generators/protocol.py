from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from mosaico.media import Media
from mosaico.script_generators.script import ShootingScript


@runtime_checkable
class ScriptGenerator(Protocol):
    """
    A protocol for generating a shooting script from a list of media files.

    This protocol defines the interface for generating a shooting script for a project from a list of media objects.
    The `generate` method should be implemented by concrete classes and should fullfill the contract of this protocol
    by returning a shooting script containing the shots generated from the media files.

    Concrete implementations of the `ScriptGenerator` protocol can be used by the `VideoProjectBuilder` class to
    automatically generate a shooting script for a project, avoiding the need of a manually defined timeline.

    !!! note
        This is a runtime checkable protocol, which means ``isinstance()`` and
        ``issubclass()`` checks can be performed against it.

    __Example__:

    ```python
    class MyScriptGenerator:
        def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
            # Implement script generation logic here
            ...

    generator: ScriptGenerator = MyScriptGenerator()
    script = generator.generate(my_media_files)
    ```
    """

    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """
        Generate a shooting script from a list of media files.

        :param media: The list of media objects.
        :param kwargs: Additional context for the script generation.
        :return: The shooting script generated from the media files.
        """
        ...
