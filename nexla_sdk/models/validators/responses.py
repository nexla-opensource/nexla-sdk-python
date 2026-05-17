"""Validator response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class ValidatorCredential(BaseModel):
    """Credential reference in validator response."""

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class Validator(BaseModel):
    """Validator response model."""

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: str = "validator"
    code_type: Optional[str] = None
    output_type: Optional[str] = None
    code: Optional[Any] = None
    code_config: Optional[Dict[str, Any]] = None
    code_encoding: Optional[str] = None
    code_error: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None
    repo_config: Optional[Dict[str, Any]] = None
    reusable: bool = True
    public: bool = False
    managed: bool = False
    ai_function_type: Optional[str] = None
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    access_roles: Optional[List[str]] = Field(default_factory=list)
    data_credentials: Optional[ValidatorCredential] = None
    runtime_data_credentials: Optional[ValidatorCredential] = None
    data_sets: Optional[List[int]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    referenced_resource_ids: Optional[Dict[str, List[int]]] = None
    copied_from_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
