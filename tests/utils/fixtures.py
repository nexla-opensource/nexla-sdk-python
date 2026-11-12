"""Test fixtures and mock HTTP client."""

from typing import Any, Callable, Dict, List, Optional, Union

from nexla_sdk.http_client import HttpClientError, HttpClientInterface


class MockHTTPClient(HttpClientInterface):
    """Mock HTTP client for testing that records requests and returns configured responses."""

    def __init__(self):
        self.requests = []  # Track all requests made
        self.responses = {}  # Map of URL patterns to responses
        self.response_queue = []  # Queue of responses to return in order
        self.default_response = {"status": "ok"}
        self.header_map = {}  # URL pattern -> response headers
        self.paged_responses = {}  # URL pattern -> [(body, headers), ...] in order
        self._last_headers = {}

    def request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs
    ) -> Dict[str, Any]:
        """Record request and return mock response."""
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": kwargs.get("params", {}),
            "data": kwargs.get("data", {}),
            "json": kwargs.get("json", {}),
        }
        self.requests.append(request_data)

        self._last_headers = self._headers_for(url)

        # Paged responses carry their own headers, in order
        for pattern, pages in self.paged_responses.items():
            if pattern in url and pages:
                body, self._last_headers = pages.pop(0)
                return body

        # Look for configured response
        for pattern, response in self.responses.items():
            if pattern in url:
                # If response is a callable, call it with request data
                if callable(response):
                    return response(request_data)
                elif isinstance(response, HttpClientError):
                    raise response
                else:
                    return response

        # Return from queue if available
        if self.response_queue:
            response = self.response_queue.pop(0)
            if isinstance(response, HttpClientError):
                raise response
            return response

        # Return default response
        return self.default_response

    def request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs
    ):
        """Return (body, response headers). Headers come from add_headers or add_paged_response."""
        body = self.request(method, url, headers, **kwargs)
        return body, dict(self._last_headers)

    def _headers_for(self, url: str) -> Dict[str, str]:
        for pattern, hdrs in self.header_map.items():
            if pattern in url:
                return dict(hdrs)
        return {}

    def add_headers(self, url_pattern: str, headers: Dict[str, str]):
        """Attach response headers to every response whose URL contains the pattern."""
        self.header_map[url_pattern] = headers

    def add_paged_response(self, url_pattern: str, pages: List[tuple]):
        """Serve (body, headers) pairs in order for URLs containing the pattern."""
        self.paged_responses[url_pattern] = list(pages)

    def add_response(
        self,
        url_pattern: str,
        response: Union[Dict[str, Any], HttpClientError, Callable],
    ):
        """Add a response for a specific URL pattern."""
        self.responses[url_pattern] = response

    def add_error(self, url_pattern: str, error: HttpClientError):
        """Add an error response for a specific URL pattern."""
        self.responses[url_pattern] = error

    def queue_response(self, response: Union[Dict[str, Any], HttpClientError]):
        """Queue a response to be returned in order."""
        self.response_queue.append(response)

    def clear_responses(self):
        """Clear all configured responses."""
        self.responses.clear()
        self.response_queue.clear()

    def clear_requests(self):
        """Clear the recorded requests."""
        self.requests.clear()

    def get_last_request(self) -> Optional[Dict[str, Any]]:
        """Get the last request made."""
        return self.requests[-1] if self.requests else None

    def get_request(self) -> Optional[Dict[str, Any]]:
        """Get the last request made (alias for get_last_request)."""
        return self.get_last_request()

    def get_requests_by_method(self, method: str) -> List[Dict[str, Any]]:
        """Get all requests made with a specific method."""
        return [req for req in self.requests if req["method"] == method]

    def get_requests_by_url_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Get all requests made to URLs containing the pattern."""
        return [req for req in self.requests if pattern in req["url"]]

    def assert_request_made(self, method: str, url_pattern: str, **kwargs):
        """Assert that a specific request was made."""
        matching_requests = [
            req
            for req in self.requests
            if req["method"] == method and url_pattern in req["url"]
        ]

        if not matching_requests:
            raise AssertionError(
                f"No {method} request to '{url_pattern}' found. "
                f"Requests made: {[req['method'] + ' ' + req['url'] for req in self.requests]}"
            )

        # Check additional parameters if provided
        if kwargs:
            for key, expected_value in kwargs.items():
                if key == "json" and "json" in matching_requests[-1]:
                    actual_value = matching_requests[-1]["json"]
                    if actual_value != expected_value:
                        raise AssertionError(
                            f"Expected JSON {expected_value}, got {actual_value}"
                        )
                elif key == "params" and "params" in matching_requests[-1]:
                    actual_value = matching_requests[-1]["params"]
                    if actual_value != expected_value:
                        raise AssertionError(
                            f"Expected params {expected_value}, got {actual_value}"
                        )

    def assert_no_unexpected_requests(
        self, expected_patterns: Optional[List[str]] = None
    ):
        """Assert that all recorded requests match expected URL patterns.

        Args:
            expected_patterns: List of URL patterns that are expected.
                             If None, uses the keys from the responses dictionary.

        Raises:
            AssertionError: If any requests don't match the expected patterns.
        """
        # Use response keys as default expected patterns if none provided
        if expected_patterns is None:
            expected_patterns = list(self.responses.keys())

        # If no expected patterns and no responses configured, all requests are unexpected
        if not expected_patterns:
            if self.requests:
                unexpected_requests = [
                    f"{req['method']} {req['url']}" for req in self.requests
                ]
                raise AssertionError(
                    f"Unexpected requests found (no expected patterns configured): {unexpected_requests}"
                )
            return

        # Check each request against expected patterns
        unexpected_requests = []
        for request in self.requests:
            url = request["url"]
            method = request["method"]

            # Check if this request matches any expected pattern
            matches_pattern = False
            for pattern in expected_patterns:
                if pattern in url:
                    matches_pattern = True
                    break

            if not matches_pattern:
                unexpected_requests.append(f"{method} {url}")

        # Raise error if any unexpected requests found
        if unexpected_requests:
            raise AssertionError(
                f"Unexpected requests found: {unexpected_requests}. "
                f"Expected patterns: {expected_patterns}"
            )


def create_mock_response(
    data: Dict[str, Any], status_code: int = 200
) -> Dict[str, Any]:
    """Create a mock response with the given data."""
    response = {"status_code": status_code, "data": data}
    response.update(data)
    return response


def create_http_error(
    status_code: int, message: str, details: Optional[Dict[str, Any]] = None
) -> HttpClientError:
    """Create an HTTP error for testing."""
    error_data = {"error": message, "status_code": status_code, "message": message}
    if details:
        error_data.update(details)

    return HttpClientError(
        message=message,
        status_code=status_code,
        response=error_data,  # Fixed: was 'response_data', should be 'response'
    )


def create_paginated_response(
    items: List[Dict[str, Any]],
    page: int = 1,
    per_page: int = 20,
    total: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a paginated response with the given items."""
    if total is None:
        total = len(items)

    total_pages = (total + per_page - 1) // per_page

    # Calculate the items for this page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    page_items = items[start_index:end_index]

    return {
        "data": page_items,
        "meta": {
            "currentPage": page,
            "totalCount": total,
            "pageCount": total_pages,
            "perPage": per_page,
        },
    }


def create_auth_token_response(
    access_token: str = "mock-token-12345", expires_in: int = 86400
) -> Dict[str, Any]:
    """Create a mock authentication token response."""
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "scope": "read write",
    }


def create_webhook_response(
    webhook_id: Optional[int] = None, **overrides
) -> Dict[str, Any]:
    """Create a mock webhook response."""
    from faker import Faker

    fake = Faker()

    base = {
        "id": webhook_id or fake.random_int(1, 10000),
        "url": fake.url(),
        "active": True,
        "events": ["source.created", "source.updated", "source.deleted"],
        "created_at": fake.date_time().isoformat(),
        "updated_at": fake.date_time().isoformat(),
    }
    base.update(overrides)
    return base


def create_api_key_response(
    api_key_id: Optional[int] = None, **overrides
) -> Dict[str, Any]:
    """Create a mock API key response."""
    from faker import Faker

    fake = Faker()

    base = {
        "id": api_key_id or fake.random_int(1, 10000),
        "name": f"API Key {fake.random_int(1, 100)}",
        "key": f"nexla_{fake.uuid4()}",
        "active": True,
        "permissions": ["read", "write"],
        "created_at": fake.date_time().isoformat(),
        "updated_at": fake.date_time().isoformat(),
    }
    base.update(overrides)
    return base


def create_rate_limit_response(
    rate_limit_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a mock rate limit response."""
    default_info = {
        "limit": 1000,
        "remaining": 999,
        "reset": 1640995200,  # Unix timestamp
        "window": 3600,  # 1 hour in seconds
    }

    if rate_limit_info:
        default_info.update(rate_limit_info)

    return {"rate_limit": default_info, "message": "Rate limit information"}


def create_health_check_response(
    status: str = "healthy", **overrides
) -> Dict[str, Any]:
    """Create a mock health check response."""
    from faker import Faker

    fake = Faker()

    base = {
        "status": status,
        "timestamp": fake.date_time().isoformat(),
        "version": "1.0.0",
        "uptime": fake.random_int(1, 1000000),
        "services": {"database": "healthy", "cache": "healthy", "storage": "healthy"},
    }
    base.update(overrides)
    return base


def create_validation_error_response(
    field_errors: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Create a mock validation error response."""
    default_errors = {
        "name": ["This field is required"],
        "email": ["Invalid email format"],
    }

    errors = field_errors or default_errors

    return {
        "error": "Validation failed",
        "status_code": 400,
        "field_errors": errors,
        "message": "The request data is invalid",
    }


def create_batch_response(
    items: List[Dict[str, Any]], batch_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a mock batch operation response."""
    from faker import Faker

    fake = Faker()

    return {
        "batch_id": batch_id or fake.uuid4(),
        "status": "completed",
        "total_items": len(items),
        "processed_items": len(items),
        "failed_items": 0,
        "results": items,
        "created_at": fake.date_time().isoformat(),
        "completed_at": fake.date_time().isoformat(),
    }


def create_test_client(service_key: str = "test-service-key", access_token: str = None):
    """Create a test NexlaClient instance with mocked HTTP client."""
    from unittest.mock import patch

    from nexla_sdk import NexlaClient

    # Create a mock HTTP client
    mock_http_client = MockHTTPClient()

    # Mock the auth token response
    mock_http_client.add_response(
        "/token",
        {"access_token": "test-token", "token_type": "Bearer", "expires_in": 86400},
    )

    # Patch the HTTP client during client creation
    with patch("nexla_sdk.client.RequestsHttpClient", return_value=mock_http_client):
        with patch("nexla_sdk.auth.RequestsHttpClient", return_value=mock_http_client):
            # Create client with either service key or access token
            if access_token:
                client = NexlaClient(access_token=access_token)
            else:
                client = NexlaClient(service_key=service_key)

    # Replace the HTTP client to ensure it's the mock one
    client.http_client = mock_http_client
    client.auth_handler.http_client = mock_http_client

    return client


def get_test_credentials() -> Optional[Dict[str, Any]]:
    """Get test credentials from environment variables."""
    import os

    service_key = os.getenv("NEXLA_SERVICE_KEY")
    access_token = os.getenv("NEXLA_ACCESS_TOKEN")
    api_url = os.getenv("NEXLA_API_URL", "https://api.nexla.io")

    if service_key:
        return {"service_key": service_key, "base_url": api_url}
    elif access_token:
        return {"access_token": access_token, "base_url": api_url}

    return None
