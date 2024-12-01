"""Base classes and interfaces for FastMCP resources."""

import abc
from typing import Union

from pydantic import BaseModel, Field, field_validator
from pydantic.networks import _BaseUrl


class Resource(BaseModel, abc.ABC):
    """Base class for all resources."""

    uri: _BaseUrl = Field(description="URI of the resource")
    name: str = Field(description="Name of the resource", default=None)
    description: str | None = Field(
        description="Description of the resource", default=None
    )
    mime_type: str = Field(
        default="text/plain",
        description="MIME type of the resource content",
        pattern=r"^[a-zA-Z0-9]+/[a-zA-Z0-9\-+.]+$",
    )

    @field_validator("name", mode="before")
    @classmethod
    def set_default_name(cls, name: str | None, info) -> str:
        """Set default name from URI if not provided."""
        if name:
            return name
        if uri := info.data.get("uri"):
            return str(uri)
        raise ValueError("Either name or uri must be provided")

    @abc.abstractmethod
    async def read(self) -> Union[str, bytes]:
        """Read the resource content."""
        pass

    model_config = {
        "validate_default": True,
    }
