from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from nexla_sdk.exceptions import NexlaError
from nexla_sdk.models.access import (
    AccessorRequestList,
    AccessorResponse,
    AccessorResponseList,
)
from nexla_sdk.utils.pagination import Paginator

T = TypeVar("T")


class BaseResource:
    """Base class for all Nexla resources."""

    def __init__(self, client):
        """
        Initialize resource.

        Args:
            client: Nexla client instance
        """
        self.client = client
        self._path = ""  # Override in subclasses
        self._model_class = None  # Override in subclasses

    def _make_request(
        self,
        method: str,
        path: str,
        resource_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Make HTTP request using client with enhanced error context."""
        try:
            return self.client.request(method, path, **kwargs)
        except NexlaError:
            # NexlaError and its subclasses should pass through unchanged
            raise
        except Exception as e:
            # Extract resource type from path
            resource_type = (
                self._path.strip("/").split("/")[-1] if self._path else "unknown"
            )

            # Build context information
            context = {
                "method": method,
                "path": path,
                "resource_path": self._path,
                "kwargs": {
                    k: v for k, v in kwargs.items() if k not in ["json", "data"]
                },  # Exclude sensitive data
            }

            if hasattr(e, "response") and e.response:
                context["api_response"] = e.response
            if hasattr(e, "status_code"):
                context["status_code"] = e.status_code

            # Re-raise with enhanced context
            raise NexlaError(
                message=str(e),
                operation=operation or f"{method.lower()}_{resource_type}",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=e,
            ) from e

    def _serialize_data(self, data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """
        Convert data to dictionary for JSON serialization.

        Args:
            data: Data to serialize (dict or Pydantic model)

        Returns:
            Dictionary representation
        """
        if data is None:
            return {}

        # Check if it's a Pydantic model (has model_dump method)
        if hasattr(data, "model_dump"):
            return data.model_dump(exclude_none=True)

        # If it's already a dict, return as-is
        if isinstance(data, dict):
            return data

        # For other types, try to convert to dict
        if hasattr(data, "__dict__"):
            return data.__dict__

        return data

    def _parse_response(
        self, response: Any, model_class: Optional[Type[T]] = None
    ) -> Any:
        """Parse response into model objects."""
        model_class = model_class or self._model_class

        if not model_class:
            return response

        if isinstance(response, list):
            return [
                model_class.model_validate(item) if isinstance(item, dict) else item
                for item in response
            ]
        elif isinstance(response, dict):
            return model_class.model_validate(response)
        return response

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        access_role: Optional[str] = None,
        **params,
    ) -> List[T]:
        """
        List resources with optional filters.

        Common filters available across most resources:
        - page: Page number (1-based)
        - per_page: Items per page
        - access_role: owner, collaborator, operator, admin

        Any resource-specific filters can be passed via keyword arguments
        (for example, `credentials_type` for credentials, `expand` for users/projects).

        Args:
            page: Page number (1-based)
            per_page: Items per page
            access_role: Filter by access role (owner, collaborator, operator, admin)
            **params: Resource-specific query parameters

        Returns:
            List of resources

        Examples:
            # Basic listing
            client.sources.list()

            # With pagination and role
            client.sources.list(page=1, per_page=20, access_role="owner")

            # With a resource-specific filter
            client.credentials.list(credentials_type="s3")
        """
        query_params = {}
        if page is not None:
            query_params["page"] = page
        if per_page is not None:
            query_params["per_page"] = per_page
        if access_role is not None:
            query_params["access_role"] = access_role
        query_params.update(params)

        response = self._make_request(
            "GET", self._path, operation="list_resources", params=query_params
        )
        return self._parse_response(response)

    def paginate(
        self, per_page: int = 20, access_role: Optional[str] = None, **params
    ) -> Paginator[T]:
        """
        Get paginator for iterating through resources.

        Args:
            per_page: Items per page
            access_role: Filter by access role
            **params: Additional query parameters

        Returns:
            Paginator instance
        """
        return Paginator(
            fetch_func=self.list, page_size=per_page, access_role=access_role, **params
        )

    def get(self, resource_id: int, expand: bool = False) -> T:
        """
        Get single resource by ID.

        Args:
            resource_id: Resource ID
            expand: Include expanded references (where supported)

        Returns:
            Resource instance

        Examples:
            # Get by ID
            client.sources.get(123)

            # Get with expanded relations (when supported by resource)
            client.projects.get(456, expand=True)
        """
        path = f"{self._path}/{resource_id}"
        params = {"expand": 1} if expand else {}

        response = self._make_request(
            "GET",
            path,
            resource_id=str(resource_id),
            operation="get_resource",
            params=params,
        )
        return self._parse_response(response)

    def create(self, data: Union[Dict[str, Any], Any]) -> T:
        """
        Create new resource.

        Args:
            data: Resource data (Pydantic model or dict)

        Returns:
            Created resource

        Examples:
            # Using a typed request model
            source = client.sources.create(SourceCreate(name="My Source", connector=...))

            # Some resources may still accept a plain dict
            client.async_tasks.create(AsyncTaskCreate(type="export", arguments={...}))
        """
        serialized_data = self._serialize_data(data)
        response = self._make_request(
            "POST", self._path, operation="create_resource", json=serialized_data
        )
        return self._parse_response(response)

    def update(self, resource_id: int, data: Union[Dict[str, Any], Any]) -> T:
        """
        Update resource.

        Args:
            resource_id: Resource ID
            data: Updated data (dict or Pydantic model)

        Returns:
            Updated resource
        """
        path = f"{self._path}/{resource_id}"
        serialized_data = self._serialize_data(data)
        response = self._make_request(
            "PUT",
            path,
            resource_id=str(resource_id),
            operation="update_resource",
            json=serialized_data,
        )
        return self._parse_response(response)

    def delete(self, resource_id: int) -> Dict[str, Any]:
        """
        Delete resource.

        Args:
            resource_id: Resource ID

        Returns:
            Response with status
        """
        path = f"{self._path}/{resource_id}"
        return self._make_request(
            "DELETE", path, resource_id=str(resource_id), operation="delete_resource"
        )

    def activate(self, resource_id: int) -> T:
        """
        Activate resource.

        Args:
            resource_id: Resource ID

        Returns:
            Activated resource
        """
        path = f"{self._path}/{resource_id}/activate"
        response = self._make_request(
            "PUT", path, resource_id=str(resource_id), operation="activate_resource"
        )
        return self._parse_response(response)

    def pause(self, resource_id: int) -> T:
        """
        Pause resource.

        Args:
            resource_id: Resource ID

        Returns:
            Paused resource
        """
        path = f"{self._path}/{resource_id}/pause"
        response = self._make_request(
            "PUT", path, resource_id=str(resource_id), operation="pause_resource"
        )
        return self._parse_response(response)

    def copy(
        self, resource_id: int, options: Optional[Union[Dict[str, Any], Any]] = None
    ) -> T:
        """
        Copy resource.

        Args:
            resource_id: Resource ID
            options: Copy options (dict or Pydantic model)

        Returns:
            Copied resource
        """
        path = f"{self._path}/{resource_id}/copy"
        serialized_options = self._serialize_data(options) if options else {}
        response = self._make_request("POST", path, json=serialized_options)
        return self._parse_response(response)

    def list_public(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **params,
    ) -> List[T]:
        """
        List publicly available resources for this type.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            **params: Additional query parameters

        Returns:
            List of public resources
        """
        path = f"{self._path}/public"
        query_params: Dict[str, Any] = {}
        if page is not None:
            query_params["page"] = page
        if per_page is not None:
            query_params["per_page"] = per_page
        query_params.update(params)
        response = self._make_request("GET", path, params=query_params)
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[T]:
        """
        List resources accessible to the current user (access_insights).

        Args:
            **params: Optional query parameters

        Returns:
            List of accessible resources
        """
        path = f"{self._path}/accessible"
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def get_access_insights(self, resource_id: int, **params) -> Dict[str, Any]:
        """
        Explain why the current user can access a resource.

        Args:
            resource_id: Resource ID
            **params: Optional query parameters

        Returns:
            Access insights payload
        """
        path = f"{self._path}/{resource_id}/access"
        return self._make_request("GET", path, params=params)

    def get_users_access_insights(self, resource_id: int, **params) -> Dict[str, Any]:
        """
        Get access insights for all users with access to a resource.

        Args:
            resource_id: Resource ID
            **params: Optional query parameters

        Returns:
            Users access insights payload
        """
        path = f"{self._path}/{resource_id}/users_access_insights"
        return self._make_request("GET", path, params=params)

    def search(self, filters: Dict[str, Any], **params) -> List[T]:
        """
        Search resources using filter criteria.

        Args:
            filters: Search filters payload
            **params: Optional query parameters

        Returns:
            List of matching resources
        """
        path = f"{self._path}/search"
        response = self._make_request("POST", path, json=filters, params=params)
        return self._parse_response(response)

    def search_tags(self, tags: List[str], **params) -> List[T]:
        """
        Search resources by tags.

        Args:
            tags: List of tags to search for
            **params: Optional query parameters

        Returns:
            List of matching resources
        """
        path = f"{self._path}/search_tags"
        response = self._make_request("POST", path, json=tags, params=params)
        return self._parse_response(response)

    def get_docs(self, resource_id: int) -> Dict[str, Any]:
        """
        Get documentation entries for a resource.

        Args:
            resource_id: Resource ID

        Returns:
            Docs payload
        """
        path = f"{self._path}/{resource_id}/docs"
        return self._make_request("GET", path)

    def set_docs(self, resource_id: int, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Replace documentation entries for a resource.

        Args:
            resource_id: Resource ID
            docs: Docs payload

        Returns:
            Updated docs payload
        """
        path = f"{self._path}/{resource_id}/docs"
        return self._make_request("POST", path, json=docs)

    def add_docs(self, resource_id: int, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add documentation entries for a resource.

        Args:
            resource_id: Resource ID
            docs: Docs payload to add

        Returns:
            Updated docs payload
        """
        path = f"{self._path}/{resource_id}/docs"
        return self._make_request("PUT", path, json=docs)

    def remove_docs(
        self, resource_id: int, docs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Remove documentation entries for a resource.

        Args:
            resource_id: Resource ID
            docs: Docs payload to remove (optional)

        Returns:
            Updated docs payload
        """
        path = f"{self._path}/{resource_id}/docs"
        return self._make_request("DELETE", path, json=docs or [])

    def get_referenced_by(self, resource_id: int) -> Dict[str, Any]:
        """
        Get resources that reference this resource.

        Args:
            resource_id: Resource ID

        Returns:
            Referenced-by payload
        """
        path = f"{self._path}/{resource_id}/referenced_by"
        return self._make_request("GET", path)

    def get_control_event(self, resource_id: int, event: str) -> Dict[str, Any]:
        """
        Get control event info for a resource.

        Args:
            resource_id: Resource ID
            event: Control event name

        Returns:
            Control event payload
        """
        path = f"{self._path}/{resource_id}/control/{event}"
        return self._make_request("GET", path)

    def get_tags(self, resource_id: int) -> List[str]:
        """
        Get tags for a resource.

        Args:
            resource_id: Resource ID

        Returns:
            List of tags
        """
        path = f"{self._path}/{resource_id}/tags"
        return self._make_request("GET", path)

    def set_tags(self, resource_id: int, tags: List[str]) -> List[str]:
        """
        Replace all tags for a resource.

        Args:
            resource_id: Resource ID
            tags: Tags to set

        Returns:
            Updated list of tags
        """
        path = f"{self._path}/{resource_id}/tags"
        return self._make_request("POST", path, json=tags)

    def add_tags(self, resource_id: int, tags: List[str]) -> List[str]:
        """
        Add tags to a resource.

        Args:
            resource_id: Resource ID
            tags: Tags to add

        Returns:
            Updated list of tags
        """
        path = f"{self._path}/{resource_id}/tags"
        return self._make_request("PUT", path, json=tags)

    def remove_tags(self, resource_id: int, tags: List[str]) -> List[str]:
        """
        Remove tags from a resource.

        Args:
            resource_id: Resource ID
            tags: Tags to remove

        Returns:
            Updated list of tags
        """
        path = f"{self._path}/{resource_id}/tags"
        return self._make_request("DELETE", path, json=tags)

    def get_audit_log(
        self,
        resource_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        event_filter: Optional[str] = None,
        change_filter: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get audit log for resource.

        Args:
            resource_id: Resource ID
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            event_filter: Filter by event type
            change_filter: Filter by change type
            page: Page number for pagination
            per_page: Items per page

        Returns:
            List of audit log entries
        """
        path = f"{self._path}/{resource_id}/audit_log"
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if event_filter is not None:
            params["event_filter"] = event_filter
        if change_filter is not None:
            params["change_filter"] = change_filter
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)

    def get_accessors(self, resource_id: int) -> AccessorResponseList:
        """
        Get access control rules for resource.

        Args:
            resource_id: Resource ID

        Returns:
            List of access control rules
        """
        path = f"{self._path}/{resource_id}/accessors"
        response = self._make_request("GET", path)

        # Parse response into AccessorResponse objects
        if isinstance(response, list):
            return [AccessorResponse.model_validate(item) for item in response]
        return []

    def add_accessors(
        self, resource_id: int, accessors: AccessorRequestList
    ) -> AccessorResponseList:
        """
        Add access control rules.

        Args:
            resource_id: Resource ID
            accessors: List of accessor rules

        Returns:
            Updated accessor list
        """
        path = f"{self._path}/{resource_id}/accessors"
        serialized_accessors = [
            self._serialize_data(accessor) for accessor in accessors
        ]
        response = self._make_request(
            "PUT", path, json={"accessors": serialized_accessors}
        )

        # Parse response into AccessorResponse objects
        if isinstance(response, list):
            return [AccessorResponse.model_validate(item) for item in response]
        return []

    def replace_accessors(
        self, resource_id: int, accessors: AccessorRequestList
    ) -> AccessorResponseList:
        """
        Replace all access control rules.

        Args:
            resource_id: Resource ID
            accessors: List of accessor rules

        Returns:
            New accessor list
        """
        path = f"{self._path}/{resource_id}/accessors"
        serialized_accessors = [
            self._serialize_data(accessor) for accessor in accessors
        ]
        response = self._make_request(
            "POST", path, json={"accessors": serialized_accessors}
        )

        # Parse response into AccessorResponse objects
        if isinstance(response, list):
            return [AccessorResponse.model_validate(item) for item in response]
        return []

    def delete_accessors(
        self, resource_id: int, accessors: Optional[AccessorRequestList] = None
    ) -> AccessorResponseList:
        """
        Delete access control rules.

        Args:
            resource_id: Resource ID
            accessors: Specific accessors to delete (None = delete all)

        Returns:
            Remaining accessor list
        """
        path = f"{self._path}/{resource_id}/accessors"
        data = None
        if accessors:
            serialized_accessors = [
                self._serialize_data(accessor) for accessor in accessors
            ]
            data = {"accessors": serialized_accessors}
        response = self._make_request("DELETE", path, json=data)

        # Parse response into AccessorResponse objects
        if isinstance(response, list):
            return [AccessorResponse.model_validate(item) for item in response]
        return []
