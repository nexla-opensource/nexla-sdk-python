"""Request models for doc containers."""

from typing import Optional

from pydantic import ConfigDict

from nexla_sdk.models.base import BaseModel


class DocContainerInput(BaseModel):
    """Writable fields for creating or replacing a documentation entry.

    Server-owned and read-only fields (``id``, ``owner``, ``org``,
    ``public``, ``tags``, ``created_at`` etc.) are silently ignored on
    construction so a full ``DocContainer`` response can be round-tripped
    through this model to drop fields the API does not accept on input.
    """

    model_config = ConfigDict(extra="ignore")

    name: str
    description: Optional[str] = None
    doc_type: str = "md"
    text: str
