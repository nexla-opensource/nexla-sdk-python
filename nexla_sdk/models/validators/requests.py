"""Validator request models."""

from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel


class ValidatorCreate(BaseModel):
    """Request model for creating a validator."""

    name: Optional[str] = None
    description: Optional[str] = None
    code_type: str  # Required: jolt_standard, jolt_custom, python, javascript, etc.
    code: Optional[Any] = None
    code_config: Optional[Dict[str, Any]] = None
    code_encoding: Optional[str] = None  # none, base64
    custom_config: Optional[Dict[str, Any]] = None
    resource_type: str = "validator"
    output_type: Optional[str] = None  # record, attribute, custom
    reusable: Optional[bool] = None
    public: Optional[bool] = None
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    data_credentials_id: Optional[int] = None
    runtime_data_credentials_id: Optional[int] = None
    tags: Optional[List[str]] = None
    repo_type: Optional[str] = None
    repo_config: Optional[Dict[str, Any]] = None
    ai_function_type: Optional[str] = None


class ValidatorUpdate(BaseModel):
    """Request model for updating a validator."""

    name: Optional[str] = None
    description: Optional[str] = None
    code_type: Optional[str] = None
    code: Optional[Any] = None
    code_config: Optional[Dict[str, Any]] = None
    code_encoding: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None
    output_type: Optional[str] = None
    reusable: Optional[bool] = None
    public: Optional[bool] = None
    data_credentials_id: Optional[int] = None
    runtime_data_credentials_id: Optional[int] = None
    tags: Optional[List[str]] = None
    repo_type: Optional[str] = None
    repo_config: Optional[Dict[str, Any]] = None


class ValidatorCopyOptions(BaseModel):
    """Options for copying a validator."""

    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    copy_access_controls: Optional[bool] = None
    reuse_data_credentials: Optional[bool] = None
