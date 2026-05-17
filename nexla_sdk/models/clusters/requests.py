"""Cluster request models."""

from typing import List, Optional

from nexla_sdk.models.base import BaseModel


class ClusterEndpointItem(BaseModel):
    """Endpoint configuration for cluster create/update."""

    service: str
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    context: Optional[str] = None
    header_host: Optional[str] = None


class ClusterCreate(BaseModel):
    """Request model for creating a cluster."""

    org_id: int
    name: str
    region: str  # Required
    description: Optional[str] = None
    provider: Optional[str] = None  # aws, gcp, azure, private
    is_default: Optional[bool] = None
    is_private: Optional[bool] = None
    endpoints: Optional[List[ClusterEndpointItem]] = None


class ClusterUpdate(BaseModel):
    """Request model for updating a cluster."""

    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    is_default: Optional[bool] = None
    is_private: Optional[bool] = None
    endpoints: Optional[List[ClusterEndpointItem]] = None


class ClusterEndpointCreate(BaseModel):
    """Request model for creating a cluster endpoint."""

    cluster_id: int
    service: str
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    context: Optional[str] = None
    header_host: Optional[str] = None


class ClusterEndpointUpdate(BaseModel):
    """Request model for updating a cluster endpoint."""

    service: Optional[str] = None
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    context: Optional[str] = None
    header_host: Optional[str] = None
