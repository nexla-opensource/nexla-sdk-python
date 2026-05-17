"""Cluster response models."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization


class ClusterEndpointRef(BaseModel):
    """Cluster endpoint reference for cluster response."""

    id: int
    service: Optional[str] = None
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    context: Optional[str] = None
    header_host: Optional[str] = None


class Cluster(BaseModel):
    """Cluster response model.

    Clusters define infrastructure endpoints for processing data flows.
    They contain multiple endpoints for different services.
    """

    id: int
    org_id: Optional[int] = None
    uid: Optional[str] = None
    is_default: Optional[bool] = None
    is_private: Optional[bool] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # INIT, ACTIVE, PAUSED
    region: Optional[str] = None
    provider: Optional[str] = None  # aws, gcp, azure, private
    org: Optional[Organization] = None
    endpoints: Optional[List[ClusterEndpointRef]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ClusterEndpoint(BaseModel):
    """Cluster endpoint response model.

    Endpoints define individual service connections within a cluster.
    """

    id: int
    cluster_id: Optional[int] = None
    org_id: Optional[int] = None
    service: Optional[str] = None
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    context: Optional[str] = None
    header_host: Optional[str] = None
    org: Optional[Organization] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
