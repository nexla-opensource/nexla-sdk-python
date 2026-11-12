from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.models.async_tasks.requests import AsyncTaskCreate
from nexla_sdk.models.async_tasks.responses import AsyncTask, DownloadLink
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class AsyncTasksResource(BaseResource[AsyncTask]):
    """Resource for managing asynchronous tasks."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/async_tasks"
        self._model_class = AsyncTask

    def list(self, **params: Any) -> List[AsyncTask]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        """List asynchronous tasks."""
        response = self._make_request("GET", self._path, params=params)
        return cast(List[AsyncTask], self._parse_response(response))

    def create(self, payload: Union[AsyncTaskCreate, Dict[str, Any]]) -> AsyncTask:
        """Create/start an asynchronous task."""
        serialized = self._serialize_data(payload)
        response = self._make_request("POST", self._path, json=serialized)
        return cast(AsyncTask, self._parse_response(response))

    def list_of_type(self, task_type: str, **params: Any) -> List[AsyncTask]:
        path = f"{self._path}/of_type/{task_type}"
        response = self._make_request("GET", path, params=params)
        return cast(List[AsyncTask], self._parse_response(response))

    def list_by_status(self, status: str) -> List[AsyncTask]:
        path = f"{self._path}/by_status/{status}"
        response = self._make_request("GET", path)
        return cast(List[AsyncTask], self._parse_response(response))

    def types(self) -> List[str]:
        path = f"{self._path}/types"
        return cast(List[str], self._make_request("GET", path))

    def explain_arguments(self, task_type: str) -> Dict[str, Any]:
        path = f"{self._path}/explain_arguments/{task_type}"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def get(self, task_id: int) -> AsyncTask:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        path = f"{self._path}/{task_id}"
        response = self._make_request("GET", path)
        return cast(AsyncTask, self._parse_response(response))

    def delete(self, task_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{task_id}"
        return cast(Dict[str, Any], self._make_request("DELETE", path))

    def rerun(self, task_id: int) -> AsyncTask:
        path = f"{self._path}/{task_id}/rerun"
        response = self._make_request("POST", path)
        return cast(AsyncTask, self._parse_response(response))

    def result(self, task_id: int) -> Optional[Dict[str, Any]]:
        path = f"{self._path}/{task_id}/result"
        return cast(Optional[Dict[str, Any]], self._make_request("GET", path))

    def download_link(self, task_id: int) -> Union[str, DownloadLink]:
        path = f"{self._path}/{task_id}/download_link"
        response = self._make_request("GET", path)
        # Some servers may return a plain URL string; others an object
        if isinstance(response, str):
            return response
        if isinstance(response, dict) and "url" in response:
            return DownloadLink.model_validate(response)
        return cast(Union[str, DownloadLink], response)

    def acknowledge(self, task_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{task_id}/acknowledge"
        return cast(Dict[str, Any], self._make_request("POST", path))
