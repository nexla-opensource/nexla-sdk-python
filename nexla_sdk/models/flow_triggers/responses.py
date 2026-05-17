"""Flow trigger response models."""

from datetime import datetime
from typing import Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class FlowTrigger(BaseModel):
    """Flow trigger response model.

    Flow triggers define orchestration events that trigger one flow
    based on events from another flow. For example, triggering a
    data source read when a data sink write completes.
    """

    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    status: str  # ACTIVE, PAUSED
    triggering_event_type: (
        str  # DATA_SINK_WRITE_DONE, DATA_SOURCE_READ_START, DATA_SOURCE_READ_DONE
    )
    triggering_origin_node_id: Optional[int] = None
    triggering_flow_node_id: Optional[int] = None
    triggering_resource_type: Optional[str] = None  # data_source, data_sink
    triggering_resource_id: Optional[int] = None
    triggered_event_type: (
        str  # DATA_SINK_WRITE_DONE, DATA_SOURCE_READ_START, DATA_SOURCE_READ_DONE
    )
    triggered_origin_node_id: Optional[int] = None
    triggered_resource_type: Optional[str] = None  # data_source, data_sink
    triggered_resource_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
