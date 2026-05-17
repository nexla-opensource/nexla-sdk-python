"""Flow trigger request models."""

from typing import Optional

from nexla_sdk.models.base import BaseModel


class FlowTriggerCreate(BaseModel):
    """Request model for creating a flow trigger.

    Flow triggers define when one flow should trigger based on events
    from another flow. The triggering and triggered resources must be
    specified, along with the event types.

    Event Types:
        - DATA_SINK_WRITE_DONE: Triggered when a data sink finishes writing
        - DATA_SOURCE_READ_START: Triggered when a data source starts reading
        - DATA_SOURCE_READ_DONE: Triggered when a data source finishes reading
    """

    # Event types
    triggering_event_type: str  # Required
    triggered_event_type: str  # Required

    # Triggering resource (one of these sets required)
    triggering_flow_node_id: Optional[int] = None
    triggering_resource_id: Optional[int] = None
    triggering_resource_type: Optional[str] = None  # data_source, data_sink
    data_sink_id: Optional[int] = None  # Shorthand for triggering data sink

    # Triggered resource (one of these sets required)
    triggered_origin_node_id: Optional[int] = None
    triggered_resource_id: Optional[int] = None
    triggered_resource_type: Optional[str] = None  # data_source, data_sink
    data_source_id: Optional[int] = None  # Shorthand for triggered data source

    # Optional owner/org
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
