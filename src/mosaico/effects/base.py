from typing import Any

from pydantic import BaseModel


class BaseEffect(BaseModel):
    """
    Base class for effects.
    """

    def get_params(self) -> dict[str, Any]:
        """Return the parameters of the effect."""
        return self.model_dump(exclude={"type"})
