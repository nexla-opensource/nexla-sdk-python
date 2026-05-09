from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class DocContainer(BaseModel):
    """Documentation container attached to a Nexla resource (e.g. a nexset)."""

    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    name: Optional[str] = None
    description: Optional[str] = None
    doc_type: Optional[str] = None
    public: Optional[bool] = None
    repo_type: Optional[str] = None
    repo_config: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    access_roles: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    copied_from_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
