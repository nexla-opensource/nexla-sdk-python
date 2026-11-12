"""Test configuration and fixtures."""

import logging
import os

import pytest
from dotenv import load_dotenv

from nexla_sdk import NexlaClient
from nexla_sdk.exceptions import AuthenticationError
from tests.utils import MockDataFactory, MockHTTPClient, MockResponseBuilder
from tests.utils.assertions import NexlaAssertions

# Load environment variables from .env file in the tests directory
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)

# Test environment variables
NEXLA_TEST_API_URL = os.getenv("NEXLA_TEST_API_URL")
NEXLA_TEST_SERVICE_KEY = os.getenv("NEXLA_TEST_SERVICE_KEY")
NEXLA_TEST_ACCESS_TOKEN = os.getenv("NEXLA_TEST_ACCESS_TOKEN")
NEXLA_TEST_API_VERSION = os.getenv("NEXLA_TEST_API_VERSION", "v1")
NEXLA_TEST_LOG_LEVEL = os.getenv("NEXLA_TEST_LOG_LEVEL", "INFO")

# Configure logging level based on environment variable
log_level = getattr(logging, NEXLA_TEST_LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


# Pytest markers for skipping tests
skip_if_no_integration_creds = pytest.mark.skipif(
    not (NEXLA_TEST_API_URL and (NEXLA_TEST_SERVICE_KEY or NEXLA_TEST_ACCESS_TOKEN)),
    reason="Nexla integration test credentials not set (NEXLA_TEST_API_URL and NEXLA_TEST_SERVICE_KEY/NEXLA_TEST_ACCESS_TOKEN)",
)


@pytest.fixture(scope="session")
def api_url() -> str:
    """Get the API URL for integration tests."""
    if not NEXLA_TEST_API_URL:
        pytest.skip("NEXLA_TEST_API_URL not set for integration tests")
    return NEXLA_TEST_API_URL


@pytest.fixture(scope="session")
def service_key() -> str:
    """Get the service key for integration tests."""
    if not NEXLA_TEST_SERVICE_KEY:
        pytest.skip("NEXLA_TEST_SERVICE_KEY not set for integration tests")
    return NEXLA_TEST_SERVICE_KEY


@pytest.fixture(scope="session")
def access_token() -> str:
    """Get the access token for integration tests."""
    if not NEXLA_TEST_ACCESS_TOKEN:
        pytest.skip("NEXLA_TEST_ACCESS_TOKEN not set for integration tests")
    return NEXLA_TEST_ACCESS_TOKEN


@pytest.fixture(scope="session")
def api_version() -> str:
    """Get the API version for tests."""
    return NEXLA_TEST_API_VERSION


# Unit Test Fixtures (with mocks)
@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for unit tests."""
    return MockHTTPClient()


@pytest.fixture
def mock_client(mock_http_client):
    """Create a Nexla client with mock HTTP client for unit tests."""
    # First, add the authentication token response for the initial token request
    mock_http_client.add_response(
        "/token",
        {
            "access_token": "mock-token-12345",
            "expires_in": 86400,
            "token_type": "Bearer",
        },
    )

    # Create client with service key authentication
    client = NexlaClient(
        service_key="test-service-key",
        base_url="https://api.test.nexla.io/nexla-api",
        http_client=mock_http_client,
    )

    # Clear any previous requests from initialization
    mock_http_client.clear_requests()

    return client


@pytest.fixture
def mock_response_builder():
    """Get the mock response builder."""
    return MockResponseBuilder


@pytest.fixture
def mock_data_factory():
    """Get the mock data factory."""
    return MockDataFactory


@pytest.fixture
def assertions() -> NexlaAssertions:
    """Get the assertions helper class."""
    return NexlaAssertions()


# Integration Test Fixtures (with real API)
@pytest.fixture(scope="session")
def integration_client(api_url: str, api_version: str) -> NexlaClient:
    """
    Provides a NexlaClient instance configured for integration tests.
    Tries to make a simple call to verify authentication.
    """
    logger.info(
        f"Initializing Nexla client with URL: {api_url}, API version: {api_version}"
    )

    # Try service key first, then access token
    if NEXLA_TEST_SERVICE_KEY:
        client = NexlaClient(
            service_key=NEXLA_TEST_SERVICE_KEY,
            base_url=api_url,
            api_version=api_version,
        )
    elif NEXLA_TEST_ACCESS_TOKEN:
        client = NexlaClient(
            access_token=NEXLA_TEST_ACCESS_TOKEN,
            base_url=api_url,
            api_version=api_version,
        )
    else:
        pytest.skip("No authentication credentials available for integration tests")

    # Perform a lightweight check to ensure the client is functional
    try:
        logger.info("Testing client authentication")
        # Try to get credentials list as a lightweight auth check
        credentials = client.credentials.list()
        logger.info(f"Authentication successful, found {len(credentials)} credentials")

    except AuthenticationError as e:
        logger.error(f"Authentication failed for integration tests: {e}")
        pytest.skip(f"Authentication failed for integration tests: {e}")

    except Exception as e:
        # Catch other potential issues like network errors during setup
        logger.error(f"Could not connect to Nexla API or other setup error: {e}")
        pytest.skip(f"Could not connect to Nexla API or other setup error: {e}")

    return client


# Test data fixtures
@pytest.fixture
def sample_credential_data():
    """Sample credential data for testing."""
    return {
        "name": "Test S3 Credential",
        "credentials_type": "s3",
        "properties": {
            "access_key_id": "test-access-key",
            "secret_access_key": "test-secret-key",
            "region": "us-east-1",
        },
    }


@pytest.fixture
def sample_credential_response():
    """Sample credential response for testing."""
    return MockResponseBuilder.credential()


@pytest.fixture
def sample_credentials_list():
    """Sample list of credentials for testing."""
    from tests.utils.mock_builders import credential_list

    return credential_list(count=3)


@pytest.fixture
def sample_probe_tree_request():
    """Sample probe tree request for testing."""
    return {"depth": 3, "path": "/"}


@pytest.fixture
def sample_probe_sample_request():
    """Sample probe sample request for testing."""
    return {"connection_type": "s3", "path": "/data/sample.csv", "max_rows": 100}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Mark unmarked tests under tests/unit/ as unit tests.

    Runs at collection time, so `pytest -m unit` selects these tests. A marker
    added inside a fixture runs too late for -m selection. Property tests keep
    their own category (run with `--property`).
    """
    category_markers = ("integration", "performance", "contract")
    for item in items:
        if not item.nodeid.startswith("tests/unit/"):
            continue
        if not any(item.get_closest_marker(name) for name in category_markers):
            item.add_marker(pytest.mark.unit)


# Test environment fixtures
@pytest.fixture
def temp_env_vars():
    """Temporarily set environment variables for testing."""
    original_env = {}

    def set_env(**kwargs):
        for key, value in kwargs.items():
            original_env[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)

    yield set_env

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


# Cleanup fixtures for integration tests
@pytest.fixture
def cleanup_credentials():
    """Track created credentials for cleanup in integration tests."""
    created_credentials = []

    def track_credential(credential):
        created_credentials.append(credential)
        return credential

    yield track_credential

    # Cleanup (this will run after the test)
    # Note: This would need access to the client, so in practice
    # you'd pass the client to this fixture or use a different approach
