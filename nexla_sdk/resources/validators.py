"""Resource for managing validators (data validation rules)."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.validators.requests import (
    ValidatorCopyOptions,
    ValidatorCreate,
    ValidatorUpdate,
)
from nexla_sdk.models.validators.responses import Validator
from nexla_sdk.resources.base_resource import BaseResource


class ValidatorsResource(BaseResource):
    """Resource for managing validators (data validation rules).

    Validators are code containers used to validate data within flows.
    They support various code types including Python, JavaScript, and Jolt.

    Examples:
        # List validators
        validators = client.validators.list()

        # Get a specific validator
        validator = client.validators.get(123)

        # Create a Python validator
        validator = client.validators.create(ValidatorCreate(
            name="My Validator",
            code_type="python",
            code="def validate(record): return record['value'] > 0"
        ))

        # List public validators
        public_validators = client.validators.list_public()
    """

    def __init__(self, client):
        """Initialize the validators resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/validators"
        self._model_class = Validator

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        access_role: Optional[str] = None,
        expand: bool = False,
        **kwargs,
    ) -> List[Validator]:
        """List validators with optional filters.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            access_role: Filter by access role (owner, collaborator, operator, admin)
            expand: Include full details for each validator
            **kwargs: Additional query parameters

        Returns:
            List of validators
        """
        if expand:
            kwargs["expand"] = 1
        return super().list(
            page=page, per_page=per_page, access_role=access_role, **kwargs
        )

    def list_public(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Validator]:
        """List publicly available validators.

        Args:
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of public validators
        """
        path = f"{self._path}/public"
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def get(self, validator_id: int, expand: bool = False) -> Validator:
        """Get validator by ID.

        Args:
            validator_id: Validator ID
            expand: Include expanded references

        Returns:
            Validator instance
        """
        return super().get(validator_id, expand=expand)

    def create(self, data: Union[ValidatorCreate, Dict[str, Any]]) -> Validator:
        """Create a new validator.

        Args:
            data: Validator creation data

        Returns:
            Created validator
        """
        return super().create(data)

    def update(
        self, validator_id: int, data: Union[ValidatorUpdate, Dict[str, Any]]
    ) -> Validator:
        """Update a validator.

        Args:
            validator_id: Validator ID
            data: Updated validator data

        Returns:
            Updated validator
        """
        return super().update(validator_id, data)

    def delete(self, validator_id: int) -> Dict[str, Any]:
        """Delete a validator.

        Args:
            validator_id: Validator ID

        Returns:
            Response with status
        """
        return super().delete(validator_id)

    def copy(
        self,
        validator_id: int,
        options: Optional[Union[ValidatorCopyOptions, Dict[str, Any]]] = None,
    ) -> Validator:
        """Copy a validator.

        Args:
            validator_id: Validator ID to copy
            options: Copy options (owner_id, org_id, etc.)

        Returns:
            Copied validator
        """
        return super().copy(validator_id, options)

    def search_tags(self, tags: List[str]) -> List[Validator]:
        """Search validators by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of validators matching the tags
        """
        path = f"{self._path}/search_tags"
        response = self._make_request("POST", path, json=tags)
        return self._parse_response(response)

    def search(self, filters: Dict[str, Any]) -> List[Validator]:
        """Search validators (alias to search_tags endpoint)."""
        path = f"{self._path}/search"
        response = self._make_request("POST", path, json=filters)
        return self._parse_response(response)
