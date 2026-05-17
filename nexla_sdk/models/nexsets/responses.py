from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, model_validator

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner
from nexla_sdk.models.flexible_enums import FlexibleDestinationType
from nexla_sdk.models.sources.responses import DataSetBrief, Source


class DataSinkSimplified(BaseModel):
    """Simplified data sink information."""

    id: int
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    name: str
    status: Optional[str] = None
    sink_type: Optional[FlexibleDestinationType] = Field(default=None, alias="sinkType")


class Nexset(BaseModel):
    """Nexset (data set) response model."""

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    access_roles: Optional[List[str]] = None
    flow_type: Optional[str] = Field(default=None, alias="flowType")

    data_source_id: Optional[int] = None
    data_source: Optional[Source] = None
    parent_data_sets: List[DataSetBrief] = Field(default_factory=list)
    data_sinks: List[DataSinkSimplified] = Field(default_factory=list)
    transform_id: Optional[int] = None
    output_schema: Optional[Dict[str, Any]] = None
    copied_from_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NexsetSample(BaseModel):
    """Nexset sample record."""

    raw_message: Dict[str, Any] = Field(alias="rawMessage")
    nexla_metadata: Optional[Dict[str, Any]] = Field(
        default=None, alias="nexlaMetaData"
    )

    @model_validator(mode="before")
    @classmethod
    def handle_formats(cls, data):
        """Handle both formats - with and without metadata."""
        if isinstance(data, dict):
            # If rawMessage exists, use it; otherwise treat whole dict as raw_message
            if "rawMessage" in data:
                return data
            elif "raw_message" not in data:
                # Direct record format - entire dict is the raw message
                return {"raw_message": data, "nexla_metadata": None}
        return data
