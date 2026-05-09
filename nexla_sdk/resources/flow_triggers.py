"""Resource for managing flow triggers."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.flow_triggers.requests import FlowTriggerCreate
from nexla_sdk.models.flow_triggers.responses import FlowTrigger
from nexla_sdk.resources.base_resource import BaseResource


class FlowTriggersResource(BaseResource):
    """Resource for managing flow triggers (orchestration events).

    Flow triggers define when one flow should trigger based on events
    from another flow. They are immutable once created - to change a
    trigger, delete and recreate it.

    Examples:
        # List flow triggers
        triggers = client.flow_triggers.list()

        # List all triggers (super user only)
        all_triggers = client.flow_triggers.list_all()

        # Create a trigger: start data source when sink completes
        trigger = client.flow_triggers.create(FlowTriggerCreate(
            triggering_event_type="DATA_SINK_WRITE_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            data_sink_id=123,  # Triggering sink
            data_source_id=456  # Triggered source
        ))

        # Pause a trigger
        client.flow_triggers.pause(trigger.id)

        # Activate a trigger
        client.flow_triggers.activate(trigger.id)

        # Delete a trigger
        client.flow_triggers.delete(trigger.id)
    """

    def __init__(self, client):
        """Initialize the flow triggers resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/flow_triggers"
        self._model_class = FlowTrigger

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        access_role: Optional[str] = None,
        **kwargs,
    ) -> List[FlowTrigger]:
        """List flow triggers accessible by current user.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            access_role: Filter by access role (owner, collaborator, operator, admin)

        Returns:
            List of flow triggers
        """
        return super().list(
            page=page, per_page=per_page, access_role=access_role, **kwargs
        )

    def list_all(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[FlowTrigger]:
        """List all flow triggers (super user only).

        Args:
            page: Page number (1-based)
            per_page: Items per page (max: 100)

        Returns:
            List of all flow triggers

        Raises:
            AuthorizationError: If user is not a super user
        """
        path = f"{self._path}/all"
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def get(self, trigger_id: int, expand: bool = False) -> FlowTrigger:
        """Get flow trigger by ID.

        Args:
            trigger_id: Flow trigger ID
            expand: Include expanded references (where supported)

        Returns:
            FlowTrigger instance
        """
        return super().get(trigger_id, expand=expand)

    def create(self, data: Union[FlowTriggerCreate, Dict[str, Any]]) -> FlowTrigger:
        """Create a new flow trigger.

        Note: Flow triggers are immutable - update is not supported.
        To change a trigger, delete and recreate it.

        Args:
            data: Flow trigger creation data

        Returns:
            Created flow trigger

        Raises:
            ValidationError: If trigger would create a cycle or duplicate
        """
        return super().create(data)

    def delete(self, trigger_id: int) -> Dict[str, Any]:
        """Delete a flow trigger.

        Args:
            trigger_id: Flow trigger ID

        Returns:
            Response with status
        """
        return super().delete(trigger_id)

    def activate(self, trigger_id: int) -> FlowTrigger:
        """Activate a flow trigger.

        Args:
            trigger_id: Flow trigger ID

        Returns:
            Activated flow trigger
        """
        return super().activate(trigger_id)

    def pause(self, trigger_id: int) -> FlowTrigger:
        """Pause a flow trigger.

        Args:
            trigger_id: Flow trigger ID

        Returns:
            Paused flow trigger
        """
        return super().pause(trigger_id)

    def update(self, resource_id=None, data=None):
        """Flow triggers are immutable. To change a trigger, delete and recreate it."""
        raise NotImplementedError(
            "Flow triggers are immutable once created. "
            "To change a trigger, delete it and create a new one."
        )
