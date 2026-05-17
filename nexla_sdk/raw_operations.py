"""Typed operation-level access for the full OpenAPI surface."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

from nexla_sdk.exceptions import ValidationError
from nexla_sdk.generated.operation_map import OPERATION_MAP, OperationId

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


_PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")


@dataclass(frozen=True)
class OperationDefinition:
    """Normalized operation metadata."""

    operation_id: str
    method: str
    path: str
    tags: List[str]
    summary: str
    path_params: List[str]


class RawOperationsClient:
    """Low-level typed access to any OpenAPI operation."""

    def __init__(self, client: "NexlaClient"):
        self._client = client

    def list_operations(self) -> List[str]:
        """Return sorted operation ids available in this SDK build."""
        return sorted(OPERATION_MAP.keys())

    def get_operation(
        self, operation_id: Union[OperationId, str]
    ) -> OperationDefinition:
        """Get metadata for a specific operation id."""
        spec = OPERATION_MAP.get(str(operation_id))
        if spec is None:
            raise ValidationError(
                f"Unknown operation_id: {operation_id}",
                operation="raw_get_operation",
                resource_type="operation",
                resource_id=str(operation_id),
            )

        return OperationDefinition(
            operation_id=str(operation_id),
            method=spec["method"],
            path=spec["path"],
            tags=list(spec["tags"]),
            summary=spec["summary"],
            path_params=list(spec["path_params"]),
        )

    def call(
        self,
        operation_id: Union[OperationId, str],
        *,
        path_params: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Call an operation by operation id."""
        operation = self.get_operation(operation_id)
        path = self._render_path(
            operation.path, operation.path_params, path_params or {}
        )

        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)

        return self._client.request(operation.method, path, **kwargs)

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send an arbitrary request to support non-spec or backend-only endpoints."""
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request(method.upper(), path, **kwargs)

    def get(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("GET", path, **kwargs)

    def post(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("POST", path, **kwargs)

    def put(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("PUT", path, **kwargs)

    def delete(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("DELETE", path, **kwargs)

    def patch(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if body is not None:
            kwargs["json"] = body
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("PATCH", path, **kwargs)

    def head(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("HEAD", path, **kwargs)

    def options(
        self,
        path: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if query is not None:
            kwargs["params"] = dict(query)
        if headers is not None:
            kwargs["headers"] = dict(headers)
        return self._client.request("OPTIONS", path, **kwargs)

    def _render_path(
        self,
        path_template: str,
        required_params: List[str],
        provided_params: Mapping[str, Any],
    ) -> str:
        missing = [param for param in required_params if param not in provided_params]
        if missing:
            missing_str = ", ".join(missing)
            raise ValidationError(
                f"Missing required path params: {missing_str}",
                operation="raw_call",
                resource_type="operation_path_params",
                context={"path": path_template, "required": required_params},
            )

        def _replace(match: re.Match[str]) -> str:
            key = match.group(1)
            value = provided_params.get(key)
            if value is None:
                raise ValidationError(
                    f"Path param '{key}' cannot be None",
                    operation="raw_call",
                    resource_type="operation_path_params",
                    context={"path": path_template, "param": key},
                )
            return str(value)

        rendered = _PATH_PARAM_RE.sub(_replace, path_template)
        if not rendered.startswith("/"):
            rendered = f"/{rendered}"
        return rendered
