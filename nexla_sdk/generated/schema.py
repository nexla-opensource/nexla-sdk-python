"""Schema typing helpers for generated operation-level access."""

from typing import Any, Dict, List, TypedDict, Union

JSONPrimitive = Union[str, int, float, bool, None]
JSONValue = Union[JSONPrimitive, Dict[str, "JSONValue"], List["JSONValue"]]
JSONObject = Dict[str, JSONValue]


class RawRequest(TypedDict, total=False):
    path_params: Dict[str, Any]
    query: Dict[str, Any]
    body: JSONObject
    headers: Dict[str, str]


class RawResponse(TypedDict, total=False):
    status: str
    message: str
    data: Any
    errors: List[str]
    metadata: Dict[str, Any]
