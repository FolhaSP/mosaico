from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from mosaico.media import Media
from mosaico.script_generators.protocol import ScriptGenerator
from mosaico.script_generators.script import ShootingScript


if TYPE_CHECKING:
    from langchain_core.runnables import Runnable


class LangChainScriptGenerator:
    """
    A script generator that integrates with LangChain runnables to convert media into shooting scripts.

    This class enables seamless integration with LangChain by wrapping any compatible Runnable
    to generate shooting scripts from media. The Runnable should be configured to:

    1. Accept a dictionary input with a 'media' key containing a sequence of Media objects
    2. Output a ShootingScript object

    Example usage:

    ```python
    from langchain import PromptTemplate, LLMChain
    from mosaico import Media

    # Create a LangChain runnable that processes media into scripts
    prompt = PromptTemplate(
        input_variables=["media"],
        template="Create script for: {media}"
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    # Wrap the chain in the script generator
    generator = LangChainScriptGenerator(chain)

    # Generate script from media
    media = [Media(...)]
    script = generator.generate(media)
    ```

    The LangChain integration supports:
    - Custom prompts and chains
    - Any LLM supported by LangChain
    - Additional kwargs passed through to the underlying runnable
    - Input/output type validation
    - Async execution via LangChain's runtime

    The runnable should handle media parsing, prompt construction, and script formatting
    internally to produce a valid ShootingScript object.

    See LangChain documentation for details on creating compatible runnables:
    https://python.langchain.com/docs/modules/chains/
    """

    __slots__ = ("runnable",)

    def __init__(self, runnable: "Runnable[dict[str, Any], ShootingScript]") -> None:
        """
        Initialize with a LangChain runnable that converts media to a shooting script.

        :param runnable: A LangChain runnable that takes a dict with 'media' key
            and returns a ShootingScript
        :raises TypeError: If runnable's input/output types don't match requirements
        """
        # Validate output type at runtime
        if not runnable.OutputType == ShootingScript:
            raise TypeError("Runnable must return a ShootingScript object")

        self.runnable = runnable

    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """
        Generate a shooting script using the LangChain runnable.

        :param media: Sequence of media objects to generate script from
        :param kwargs: Additional arguments passed to the runnable
        :return: Generated shooting script
        """
        return self.runnable.invoke({"media": media}, **kwargs)


def convert_script_generator_to_runnable(generator: ScriptGenerator) -> "Runnable[dict[str, Any], ShootingScript]":
    """
    Convert a script generator to a LangChain runnable that generates shooting scripts.

    This function wraps a script generator to create a LangChain runnable that
    converts media into shooting scripts. The resulting runnable can be used
    with LangChain to process media and generate scripts.

    :param generator: A script generator that converts media to a shooting script
    :return: A LangChain runnable that processes media into a shooting script
    """
    try:
        from langchain_core.runnables import RunnableLambda
    except ImportError:
        raise ImportError("LangChain is required to convert script generators to runnables")

    def _generate_script(input_: dict[str, Any]) -> ShootingScript:
        return generator.generate(input_["media"], **{k: v for k, v in input_.items() if k != "media"})

    return RunnableLambda(_generate_script).with_types(input_type=dict[str, Any], output_type=ShootingScript)
