# Nexla SDK Test Structure

This document outlines the comprehensive testing strategy for the Nexla SDK, covering all resource types and testing methodologies.

## Test Organization

The tests are organized into several categories:

```
tests/
├── unit/              # Unit tests with mocked dependencies
├── integration/       # Integration tests with real API
├── property/          # Property-based tests using hypothesis
├── models/            # Model validation tests
├── performance/       # Performance and load tests
└── utils/            # Test utilities and helpers
```

## Testing Strategies

### 1. Unit Tests (`unit/`)
- Mock all HTTP calls
- Test individual methods in isolation
- Verify correct request formation
- Test error handling
- Fast and deterministic

### 2. Integration Tests (`integration/`)
- Use real API credentials
- Test full request/response cycle
- Test actual API behavior
- Require valid credentials
- Slower but realistic

### 3. Property-Based Tests (`property/`)
- Use Hypothesis library for automated testing
- Generate random valid inputs
- Test edge cases automatically
- Verify properties that should always hold
- Great for finding unexpected bugs

## Current Test Coverage

### ✅ Completed Resources

#### Flows
- **Unit Tests**: `tests/unit/test_flows.py` (13 tests)
  - Complete CRUD operations (list, get, create, activate, pause, delete)
  - Flow-specific operations (get_by_resource)
  - Error handling and validation
  - Mock response verification
  
- **Integration Tests**: `tests/integration/test_flows.py` (7 tests)
  - Real API interaction tests
  - CRUD with cleanup
  - Pagination and filtering
  - Error scenarios
  
- **Property Tests**: `tests/property/test_flows.py` (8 tests)
  - Automated edge case discovery
  - Stateful testing with state machines
  - Input validation and serialization

#### Lookups (Data Maps)
- **Unit Tests**: `tests/unit/test_lookups.py` (15 tests)
  - Complete CRUD operations (list, get, create, update, delete)
  - Entry management (upsert, get, delete entries)
  - Single and multiple key operations
  - Error handling and validation
  - Mock response verification
  
- **Integration Tests**: `tests/integration/test_lookups.py` (8 tests)
  - Real API interaction tests
  - CRUD with cleanup
  - Entry operations testing
  - Pagination and filtering
  - Error scenarios
  
- **Property Tests**: `tests/property/test_lookups.py` (7 tests)
  - Automated serialization testing
  - Response parsing validation
  - Edge case name testing
  - Data defaults serialization

### 🚧 In Progress

### 📋 Pending Resources
- **Destinations**: Data destination management
- **Credentials**: Authentication credential management
- **Nexsets**: Dataset management
- **Sources**: Data source management  
- **Users**: User account management
- **Organizations**: Organization management
- **Teams**: Team management
- **Projects**: Project management
- **Notifications**: Notification management
- **Metrics**: Performance metrics

## Test Utilities

### Mock Infrastructure (`tests/utils/`)

#### MockDataFactory (`mock_builders.py`)
- Creates realistic mock data for all resources
- Supports nested relationships (owner, organization, etc.)
- Configurable via overrides
- Consistent data generation

#### MockResponseBuilder (`mock_builders.py`)
- Static methods for building mock API responses
- Supports all HTTP response patterns
- Proper error response simulation

#### NexlaAssertions (`assertions.py`)
- Custom assertion methods for each resource type
- Validates nested object structures
- Clear error messages for test failures

#### Test Fixtures (`fixtures.py`)
- `create_test_client()`: Creates properly mocked NexlaClient
- `get_test_credentials()`: Loads real API credentials for integration tests
- `create_mock_response()`: Builds mock HTTP responses

### Test Configuration

#### pyproject.toml (`[tool.pytest.ini_options]`, `[tool.coverage.*]`)
- Test markers: unit, integration, property, performance, slow
- Coverage configuration; CI enforces an 85% minimum with `--cov-fail-under=85`
- Test discovery patterns
- Hypothesis settings

#### conftest.py
- Automatic test marking
- Shared fixtures
- Test environment setup

## Running Tests

### All Tests
```bash
python -m pytest
```

### By Category
```bash
# Unit tests only
python -m pytest -m unit

# Integration tests (requires credentials)
python -m pytest -m integration

# Property-based tests
python -m pytest -m property
```

### By Resource
```bash
# All flows tests
python -m pytest tests/unit/test_flows.py tests/integration/test_flows.py tests/property/test_flows.py

# All lookups tests
python -m pytest tests/unit/test_lookups.py tests/integration/test_lookups.py tests/property/test_lookups.py
```

### With Coverage
```bash
python -m pytest --cov=nexla_sdk --cov-report=html
```

### Performance Mode
```bash
# Fast testing with fewer examples
python -m pytest -x --hypothesis-profile=ci

# Thorough testing
python -m pytest --hypothesis-profile=dev
```

## Best Practices

### Unit Tests
1. Mock all external dependencies
2. Test one function/method per test
3. Use descriptive test names
4. Verify both successful and error cases
5. Check request formation and response parsing

### Integration Tests
1. Always clean up created resources
2. Use unique names to avoid conflicts
3. Handle rate limiting gracefully
4. Test real error scenarios
5. Skip tests when credentials unavailable

### Property Tests
1. Define clear strategies for data generation
2. Use assume() for input constraints
3. Suppress health checks when appropriate
4. Keep examples count reasonable for CI
5. Test invariants that should always hold

### Mock Data
1. Use realistic but predictable data
2. Support all required fields
3. Allow customization via overrides
4. Maintain consistency across related objects
5. Generate valid enum values

## Test Environment Setup

### Environment Variables
```bash
# For integration tests (optional)
export NEXLA_TEST_SERVICE_KEY="your-service-key"
export NEXLA_TEST_ACCESS_TOKEN="your-access-token"  
export NEXLA_TEST_API_URL="https://your-nexla-instance.com/nexla-api"

# For test configuration
export PYTEST_CURRENT_TEST="true"
```

### Dependencies
All test dependencies are defined in `requirements.txt`:
- pytest: Core testing framework
- pytest-mock: Mocking utilities
- pytest-cov: Coverage reporting
- pytest-xdist: Parallel test execution
- hypothesis: Property-based testing
- faker: Realistic fake data generation
- responses: HTTP request mocking
- freezegun: Time mocking

## Debugging Tests

### Common Issues
1. **Mock not called**: Check if the mock is properly set up before the function call
2. **Wrong URL**: Verify the API URL construction in assertions
3. **Validation errors**: Check if mock data matches the expected model schema
4. **Hypothesis failures**: Add health check suppressions or improve strategies

### Debug Techniques
```bash
# Run with verbose output
python -m pytest -v -s

# Run single test with debugging
python -m pytest tests/unit/test_flows.py::TestFlowsUnit::test_list_flows -v -s

# See full traceback
python -m pytest --tb=long

# Drop into debugger on failure
python -m pytest --pdb
```

This testing framework provides comprehensive coverage of the Nexla SDK with multiple testing strategies to ensure reliability, correctness, and robustness across all supported operations. 