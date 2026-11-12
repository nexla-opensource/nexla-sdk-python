"""Integration tests for nexsets resource."""

import os

import pytest

from nexla_sdk import NexlaClient, NexlaError
from nexla_sdk.exceptions import NotFoundError
from nexla_sdk.models.nexsets import NexsetCopyOptions, NexsetCreate, NexsetUpdate
from tests.utils.assertions import NexlaAssertions


@pytest.mark.integration
class TestNexsetsIntegration:
    """Integration tests for nexsets resource with real API calls."""

    @pytest.fixture(scope="class")
    def client(self):
        """Create authenticated client for integration tests."""
        service_key = os.getenv("NEXLA_SERVICE_KEY")
        access_token = os.getenv("NEXLA_ACCESS_TOKEN")

        if not service_key and not access_token:
            pytest.skip("No authentication credentials provided for integration tests")

        if service_key:
            return NexlaClient(service_key=service_key)
        else:
            return NexlaClient(access_token=access_token)

    @pytest.fixture
    def assertions(self):
        """Create assertions helper."""
        return NexlaAssertions()

    @pytest.fixture
    def test_nexset_id(self, client):
        """Provide a test nexset ID for operations."""
        # This would need to be set up with a real test environment
        # For now, we'll skip if no test nexset is available
        test_id = os.getenv("TEST_NEXSET_ID")
        if not test_id:
            pytest.skip("No test nexset ID provided")
        return int(test_id)

    def test_nexset_crud_operations(self, client, assertions):
        """Test complete CRUD lifecycle for nexsets."""
        created_nexset = None

        try:
            # Skip creation test if no parent dataset provided
            parent_id = os.getenv("TEST_PARENT_DATASET_ID")
            if not parent_id:
                pytest.skip("No test parent dataset ID provided for CRUD test")

            # Test CREATE
            create_data = NexsetCreate(
                name="Integration Test Dataset",
                description="Created during integration testing",
                parent_data_set_id=int(parent_id),
                has_custom_transform=False,
            )

            created_nexset = client.nexsets.create(create_data)
            assertions.assert_nexset_response(created_nexset)
            assert created_nexset.name == "Integration Test Dataset"

            # Test READ
            fetched_nexset = client.nexsets.get(created_nexset.id)
            assertions.assert_nexset_response(fetched_nexset)
            assert fetched_nexset.id == created_nexset.id
            assert fetched_nexset.name == created_nexset.name

            # Test UPDATE
            update_data = NexsetUpdate(
                name="Updated Integration Test Dataset",
                description="Updated during integration testing",
            )

            updated_nexset = client.nexsets.update(created_nexset.id, update_data)
            assertions.assert_nexset_response(updated_nexset)
            assert updated_nexset.name == "Updated Integration Test Dataset"
            assert updated_nexset.description == "Updated during integration testing"

        finally:
            # Test DELETE - cleanup
            if created_nexset:
                try:
                    result = client.nexsets.delete(created_nexset.id)
                    assert "message" in result or "success" in str(result).lower()
                except Exception as e:
                    print(
                        f"Warning: Failed to cleanup test nexset {created_nexset.id}: {e}"
                    )

    def test_list_nexsets(self, client, assertions):
        """Test listing nexsets."""
        # Test basic list
        nexsets = client.nexsets.list()
        assert isinstance(nexsets, list)

        for nexset in nexsets[:5]:  # Check first 5 to avoid long test times
            assertions.assert_nexset_response(nexset)

        # Test with pagination
        paginated_nexsets = client.nexsets.list(page=1, per_page=5)
        assert isinstance(paginated_nexsets, list)
        assert len(paginated_nexsets) <= 5

    def test_get_nexset_with_expand(self, client, test_nexset_id, assertions):
        """Test getting nexset with expand option."""
        nexset = client.nexsets.get(test_nexset_id, expand=True)
        assertions.assert_nexset_response(nexset)
        assert nexset.id == test_nexset_id

    def test_nexset_samples(self, client, test_nexset_id, assertions):
        """Test getting nexset samples."""
        try:
            # Test basic samples
            samples = client.nexsets.get_samples(test_nexset_id, count=3)
            assert isinstance(samples, list)

            # If samples exist, validate them
            for sample in samples:
                assertions.assert_nexset_sample(sample)

            # Test with metadata
            samples_with_metadata = client.nexsets.get_samples(
                test_nexset_id, count=2, include_metadata=True
            )
            assert isinstance(samples_with_metadata, list)

        except NexlaError as e:
            if "no samples available" in str(e).lower():
                pytest.skip("No samples available for test nexset")
            else:
                raise

    def test_nexset_lifecycle_operations(self, client, test_nexset_id, assertions):
        """Test activate and pause operations."""
        try:
            # Test activate
            activated_nexset = client.nexsets.activate(test_nexset_id)
            assertions.assert_nexset_response(activated_nexset)

            # Test pause
            paused_nexset = client.nexsets.pause(test_nexset_id)
            assertions.assert_nexset_response(paused_nexset)

        except NexlaError as e:
            if (
                "not supported" in str(e).lower()
                or "cannot be activated" in str(e).lower()
            ):
                pytest.skip("Activate/pause not supported for this nexset type")
            else:
                raise

    def test_nexset_copy(self, client, test_nexset_id, assertions):
        """Test copying a nexset."""
        copied_nexset = None

        try:
            copy_options = NexsetCopyOptions(copy_access_controls=False)

            copied_nexset = client.nexsets.copy(test_nexset_id, copy_options)
            assertions.assert_nexset_response(copied_nexset)
            assert copied_nexset.id != test_nexset_id
            assert copied_nexset.copied_from_id == test_nexset_id

        except NexlaError as e:
            if "copy not supported" in str(e).lower():
                pytest.skip("Copy operation not supported for this nexset")
            else:
                raise
        finally:
            # Cleanup copied nexset
            if copied_nexset:
                try:
                    client.nexsets.delete(copied_nexset.id)
                except Exception as e:
                    print(
                        f"Warning: Failed to cleanup copied nexset {copied_nexset.id}: {e}"
                    )

    def test_nexset_not_found_error(self, client):
        """Test error handling for non-existent nexset."""
        non_existent_id = 999999999

        with pytest.raises((NotFoundError, NexlaError)) as exc_info:
            client.nexsets.get(non_existent_id)

        # Should be a 404 error
        if hasattr(exc_info.value, "status_code"):
            assert exc_info.value.status_code == 404

    def test_nexset_validation_errors(self, client):
        """Test validation error handling."""
        try:
            # Test invalid parent dataset ID
            invalid_create_data = NexsetCreate(
                name="Invalid Test",
                parent_data_set_id=-1,  # Invalid ID
                has_custom_transform=False,
            )

            with pytest.raises(NexlaError) as exc_info:
                client.nexsets.create(invalid_create_data)

            # Should be a 400 or 422 error
            if hasattr(exc_info.value, "status_code"):
                assert exc_info.value.status_code in [400, 422]

        except Exception as e:
            # Some validation might be caught at different levels
            assert "invalid" in str(e).lower() or "error" in str(e).lower()

    def test_list_with_pagination(self, client):
        """Test pagination functionality."""
        # Get first page
        page1 = client.nexsets.list(page=1, per_page=3)
        assert isinstance(page1, list)
        assert len(page1) <= 3

        # Get second page if there are enough nexsets
        page2 = client.nexsets.list(page=2, per_page=3)
        assert isinstance(page2, list)

        # Pages should be different (if there are enough nexsets)
        if len(page1) == 3 and len(page2) > 0:
            page1_ids = {nexset.id for nexset in page1}
            page2_ids = {nexset.id for nexset in page2}
            assert page1_ids.isdisjoint(page2_ids), (
                "Pages should contain different nexsets"
            )
