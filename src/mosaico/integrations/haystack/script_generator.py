from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from mosaico.media import Media
from mosaico.script_generators.script import ShootingScript


if TYPE_CHECKING:
    from haystack.core.pipeline import Pipeline


class HaystackScriptGenerator:
    """
    A script generator that integrates with Haystack pipelines to convert media into shooting scripts.

    to generate shooting scripts from media. The Pipeline should be configured to:

    1. Accept media input through a specified component and input key
    2. Output a ShootingScript object through a specified output key

    Example usage:

    ```python
    from haystack import Pipeline
    from haystack.nodes import PromptNode
    from mosaico import Media

    # Create a Haystack pipeline that processes media into scripts
    prompt_node = PromptNode(
        model_name="gpt-4",
        default_prompt_template="Create script for: {media}"
    )
    pipeline = Pipeline()
    pipeline.add_node(component=prompt_node, name="prompt", inputs=["Query"])

    # Wrap the pipeline in the script generator
    generator = HaystackScriptGenerator(
        pipeline=pipeline,
        input_component="prompt",
        media_input_key="media",
        script_output_key="script"
    )

    # Generate script from media
    media = [Media(...)]
    script = generator.generate(media)
    ```

    The Haystack integration supports:
    - Custom pipelines and components
    - Any LLM supported by Haystack
    - Additional kwargs passed through to the pipeline
    - Input/output key configuration
    - Error handling and validation

    The pipeline should handle media parsing, prompt construction, and script formatting
    internally to produce a valid ShootingScript object.

    See Haystack documentation for details on creating compatible pipelines:
    https://docs.haystack.deepset.ai/docs/pipelines
    """

    def __init__(
        self,
        pipeline: "Pipeline",
        input_component: str,
        *,
        media_input_key: str = "media",
        script_output_key: str = "script",
    ) -> None:
        """
        Initialize the adapter.

        :param pipeline: The Haystack Pipeline to wrap
        :param input_component: Name of the component that receives the media input
        :param media_input_key: The input key where media should be passed
        :param script_output_key: The output key where the script is expected
        """
        self.pipeline = pipeline
        self.input_component = input_component
        self.media_input_key = media_input_key
        self.script_output_key = script_output_key

    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        """
        Generate a shooting script using the wrapped Haystack pipeline.

        :param media: The media to generate a script for
        :param kwargs: Additional arguments to pass to the pipeline
        :return: The generated shooting script
        """
        # Prepare inputs for the pipeline
        inputs = {self.input_component: {self.media_input_key: list(media), **kwargs}}

        # Run the pipeline
        try:
            results = self.pipeline.run(inputs)
        except Exception as e:
            raise RuntimeError(f"Haystack pipeline execution failed: {str(e)}") from e

        # Extract script from results
        for component_results in results.values():
            if self.script_output_key in component_results:
                script = component_results[self.script_output_key]
                if isinstance(script, ShootingScript):
                    return script
                elif isinstance(script, dict):
                    return ShootingScript(**script)
                else:
                    raise ValueError(
                        f"Pipeline output for key '{self.script_output_key}' "
                        f"is not a ShootingScript or compatible dict: {type(script)}"
                    )

        raise ValueError(f"Pipeline output did not contain expected key '{self.script_output_key}'")
