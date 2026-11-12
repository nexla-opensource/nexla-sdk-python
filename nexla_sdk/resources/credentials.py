"""Credentials resource implementation."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from nexla_sdk.models.credentials.requests import (
    CredentialCreate,
    CredentialUpdate,
    ProbeSampleRequest,
    ProbeTreeRequest,
)
from nexla_sdk.models.credentials.responses import (
    Credential,
    ProbeSampleResponse,
    ProbeTreeResponse,
)
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class CredentialsResource(BaseResource):
    """Resource for managing data credentials."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/data_credentials"
        self._model_class = Credential

    def list(
        self, credentials_type: Optional[str] = None, **kwargs
    ) -> List[Credential]:
        """
        List credentials with optional filters.

        Args:
            credentials_type: Filter by credential type (e.g., 's3', 'gcs')
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of credentials

        Examples:
            # All credentials
            client.credentials.list()

            # Filter by type
            client.credentials.list(credentials_type="s3")

            # With pagination and role
            client.credentials.list(page=1, per_page=20, access_role="owner")
        """
        params = kwargs.copy()
        if credentials_type:
            params["credentials_type"] = credentials_type

        return super().list(**params)

    def list_all(self, **params) -> List[Credential]:
        """List all credentials (admin only)."""
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def list_public(self, **params) -> List[Credential]:
        response = self._make_request("GET", f"{self._path}/public", params=params)
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[Credential]:
        return super().list_accessible(**params)

    def credentials_schema(self, source_type: Optional[str] = None) -> Dict[str, Any]:
        path = f"{self._path}/format"
        if source_type:
            path = f"{path}/{source_type}"
        return self._make_request("GET", path)

    def db_data_types(self, source_type: str) -> Dict[str, Any]:
        path = f"{self._path}/db_data_types/{source_type}"
        return self._make_request("GET", path)

    def search(self, filters: Dict[str, Any], **params) -> List[Credential]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Credential]:
        return super().search_tags(tags, **params)

    def get(self, credential_id: int, expand: bool = False) -> Credential:
        """
        Get single credential by ID.

        Args:
            credential_id: Credential ID
            expand: Include expanded references

        Returns:
            Credential instance

        Examples:
            client.credentials.get(123)
        """
        return super().get(credential_id, expand)

    def create(self, data: CredentialCreate) -> Credential:
        """
        Create new credential.

        Args:
            data: Credential creation data

        Returns:
            Created credential

        Examples:
            new_cred = client.credentials.create(
                CredentialCreate(name="my-s3", connector_type="s3", config={...})
            )
        """
        return super().create(data)

    def update(self, credential_id: int, data: CredentialUpdate) -> Credential:
        """
        Update credential.

        Args:
            credential_id: Credential ID
            data: Updated credential data

        Returns:
            Updated credential
        """
        return super().update(credential_id, data)

    def delete(self, credential_id: int) -> Dict[str, Any]:
        """
        Delete credential.

        Args:
            credential_id: Credential ID

        Returns:
            Response with status
        """
        return super().delete(credential_id)

    def probe(
        self,
        credential_id: int,
        async_mode: bool = False,
        request_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Test credential validity.

        Args:
            credential_id: Credential ID

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe"
        params = {}
        if async_mode:
            params["async"] = True
        if request_id is not None:
            params["request_id"] = request_id
        response = self._make_request("GET", path, params=params)

        # Handle cases where the response might be None or contain raw text
        if response is None:
            return {
                "status": "success",
                "message": "Credential probe completed successfully",
            }
        elif isinstance(response, dict) and "raw_text" in response:
            return {
                "status": "success",
                "message": response["raw_text"],
                "status_code": response.get("status_code"),
            }
        else:
            return response

    def probe_list_buckets(self, credential_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/list"
        return self._make_request("GET", path)

    def probe_summary(self, credential_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/summary"
        return self._make_request("GET", path)

    def probe_list_files(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/buckets"
        return self._make_request("POST", path, json=payload)

    def probe_tree_request(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/tree"
        return self._make_request("POST", path, json=payload)

    def probe_read_file(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/files"
        return self._make_request("POST", path, json=payload)

    def probe_detect_schemas(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/schemas"
        return self._make_request("POST", path, json=payload)

    def probe_read_sample(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/sample"
        return self._make_request("POST", path, json=payload)

    def probe_file_download(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/file/download"
        return self._make_request("POST", path, json=payload)

    def probe_search_path(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/probe/search_path"
        return self._make_request("POST", path, json=payload)

    def probe_tree(
        self,
        credential_id: int,
        request: ProbeTreeRequest,
        async_mode: bool = False,
        request_id: Optional[int] = None,
    ) -> ProbeTreeResponse:
        """
        Preview storage structure accessible by credential.

        Args:
            credential_id: Credential ID
            request: Probe tree request

        Returns:
            Storage structure response
        """
        path = f"{self._path}/{credential_id}/probe/tree"
        params = {}
        if async_mode:
            params["async"] = True
        if request_id is not None:
            params["request_id"] = request_id
        response = self._make_request(
            "POST", path, json=request.to_dict(), params=params
        )
        return ProbeTreeResponse(**response)

    def probe_sample(
        self,
        credential_id: int,
        request: ProbeSampleRequest,
        async_mode: bool = False,
        request_id: Optional[int] = None,
    ) -> ProbeSampleResponse:
        """
        Preview data content accessible by credential.

        Args:
            credential_id: Credential ID
            request: Probe sample request

        Returns:
            Sample data response
        """
        path = f"{self._path}/{credential_id}/probe/sample"
        params = {}
        if async_mode:
            params["async"] = True
        if request_id is not None:
            params["request_id"] = request_id
        response = self._make_request(
            "POST", path, json=request.to_dict(), params=params
        )
        return ProbeSampleResponse(**response)

    def refresh(self, credential_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/refresh"
        return self._make_request("PUT", path)

    def usage(self, credential_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/usage"
        return self._make_request("GET", path)

    def intent(
        self, credential_id: int, payload: Dict[str, Any], method: str = "PUT"
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/intent"
        return self._make_request(method.upper(), path, json=payload)

    def migrate_iceberg(
        self, credential_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{credential_id}/migrate/iceberg"
        return self._make_request("POST", path, json=payload)

    def data_credentials_update_credentials(
        self, credentials_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Partially update credentials (PATCH).

        Args:
            credentials_id: Credential ID
            data: Fields to update

        Returns:
            Updated credential as a dict
        """
        path = f"{self._path}/{credentials_id}"
        return self._make_request("PATCH", path, json=data)

    def iceberg_migration_status(
        self, credential_id: int, run_id: str
    ) -> Dict[str, Any]:
        """
        Get the status of an Iceberg migration run.

        Args:
            credential_id: Credential ID
            run_id: Migration run ID

        Returns:
            Migration status
        """
        path = f"{self._path}/{credential_id}/migrate/iceberg/{run_id}/status"
        return self._make_request("GET", path)

    def data_credentials_probe_credentials_get(
        self, credential_id: int, async_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Test credential validity through the probe/authenticate route.

        Args:
            credential_id: Credential ID
            async_mode: Sent as the async query parameter

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/authenticate"
        params = {}
        if async_mode is not None:
            params["async"] = async_mode
        return self._make_request("GET", path, params=params)

    def data_credentials_probe_list_files_in_bucket_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List files in a bucket (PUT probe/buckets).

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/buckets"
        return self._make_request("PUT", path, json=data)

    def probe_database_metadata_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read database metadata through the credential.

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/database/metadata"
        return self._make_request("POST", path, json=data)

    def probe_database_query_usage_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read database query usage through the credential.

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/database/query-usage"
        return self._make_request("POST", path, json=data)

    def data_credentials_probe_file_download_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Download a file through the credential (PUT probe/file/download).

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/file/download"
        return self._make_request("PUT", path, json=data)

    def data_credentials_probe_read_file_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read a file through the credential (PUT probe/files).

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/files"
        return self._make_request("PUT", path, json=data)

    def data_credentials_probe_detect_schemas_credentials(
        self, credential_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect schemas through the credential (PUT probe/schemas).

        Args:
            credential_id: Credential ID
            data: Optional probe body

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/schemas"
        return self._make_request("PUT", path, json=data)

    def data_credentials_probe_search_path_credentials(
        self,
        credential_id: int,
        data: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
        keep_path: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Search a path through the credential (PUT probe/search_path).

        Args:
            credential_id: Credential ID
            data: Optional probe body
            query: Sent as the query query parameter
            keep_path: Sent as the keep_path query parameter

        Returns:
            Probe response
        """
        path = f"{self._path}/{credential_id}/probe/search_path"
        params = {}
        if query is not None:
            params["query"] = query
        if keep_path is not None:
            params["keep_path"] = keep_path
        return self._make_request("PUT", path, json=data, params=params)
