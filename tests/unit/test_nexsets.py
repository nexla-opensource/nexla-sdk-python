"""Unit tests for nexsets resource."""

import pytest
from pydantic import ValidationError

from nexla_sdk.exceptions import NotFoundError, ServerError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.doc_containers import DocContainer, DocContainerInput
from nexla_sdk.models.nexsets.requests import (
    NexsetCopyOptions,
    NexsetCreate,
    NexsetUpdate,
)
from nexla_sdk.models.nexsets.responses import Nexset
from tests.utils.mock_builders import MockDataFactory


@pytest.mark.unit
class TestNexsetsResource:
    """Test nexsets resource methods."""

    def test_list_nexsets(self, mock_client):
        """Test listing nexsets."""
        # Arrange
        mock_factory = MockDataFactory()
        mock_nexset1 = mock_factory.create_mock_nexset(id=1001, name="Dataset 1")
        mock_nexset2 = mock_factory.create_mock_nexset(id=1002, name="Dataset 2")
        mock_response = [mock_nexset1, mock_nexset2]
        mock_client.http_client.add_response("/data_sets", mock_response)

        # Act
        nexsets = mock_client.nexsets.list()

        # Assert
        assert len(nexsets) == 2
        assert all(isinstance(nexset, Nexset) for nexset in nexsets)
        mock_client.http_client.assert_request_made("GET", "/data_sets")

    def test_list_nexsets_with_parameters(self, mock_client):
        """Test listing nexsets with query parameters."""
        # Arrange
        mock_factory = MockDataFactory()
        mock_response = [mock_factory.create_mock_nexset()]
        mock_client.http_client.add_response("/data_sets", mock_response)

        # Act
        mock_client.nexsets.list(page=2, per_page=50, access_role="collaborator")

        # Assert
        mock_client.http_client.assert_request_made("GET", "/data_sets")
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("page") == 2
        assert request["params"].get("per_page") == 50
        assert request["params"].get("access_role") == "collaborator"

    def test_get_nexset(self, mock_client):
        """Test getting single nexset."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(
            id=nexset_id, name="Test Dataset"
        )
        mock_client.http_client.add_response(f"/data_sets/{nexset_id}", mock_response)

        # Act
        nexset = mock_client.nexsets.get(nexset_id)

        # Assert
        assert isinstance(nexset, Nexset)
        assert nexset.id == nexset_id
        assert nexset.name == "Test Dataset"
        mock_client.http_client.assert_request_made("GET", f"/data_sets/{nexset_id}")

    def test_get_nexset_with_expand(self, mock_client):
        """Test getting nexset with expand parameter."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(id=nexset_id)
        mock_client.http_client.add_response(f"/data_sets/{nexset_id}", mock_response)

        # Act
        mock_client.nexsets.get(nexset_id, expand=True)

        # Assert
        mock_client.http_client.assert_request_made("GET", f"/data_sets/{nexset_id}")
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("expand") == 1

    def test_create_nexset(self, mock_client):
        """Test creating nexset."""
        # Arrange
        create_data = NexsetCreate(
            name="New Dataset",
            parent_data_set_id=2001,
            has_custom_transform=True,
            description="Test dataset creation",
        )
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(id=1001, name="New Dataset")
        mock_client.http_client.add_response("/data_sets", mock_response)

        # Act
        nexset = mock_client.nexsets.create(create_data)

        # Assert
        assert isinstance(nexset, Nexset)
        assert nexset.id == 1001
        assert nexset.name == "New Dataset"
        mock_client.http_client.assert_request_made("POST", "/data_sets")

        # Verify request body
        request = mock_client.http_client.get_last_request()
        assert request["json"]["name"] == "New Dataset"

    def test_update_nexset(self, mock_client):
        """Test updating nexset."""
        # Arrange
        nexset_id = 1001
        update_data = NexsetUpdate(
            name="Updated Dataset", description="Updated description"
        )
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(
            id=nexset_id, name="Updated Dataset"
        )
        mock_client.http_client.add_response(f"/data_sets/{nexset_id}", mock_response)

        # Act
        nexset = mock_client.nexsets.update(nexset_id, update_data)

        # Assert
        assert isinstance(nexset, Nexset)
        assert nexset.name == "Updated Dataset"
        mock_client.http_client.assert_request_made("PUT", f"/data_sets/{nexset_id}")

    def test_delete_nexset(self, mock_client):
        """Test deleting nexset."""
        # Arrange
        nexset_id = 1001
        mock_response = {"message": "Dataset deleted successfully"}
        mock_client.http_client.add_response(f"/data_sets/{nexset_id}", mock_response)

        # Act
        result = mock_client.nexsets.delete(nexset_id)

        # Assert
        assert result["message"] == "Dataset deleted successfully"
        mock_client.http_client.assert_request_made("DELETE", f"/data_sets/{nexset_id}")

    def test_activate_nexset(self, mock_client):
        """Test activating nexset."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(id=nexset_id, status="ACTIVE")
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/activate", mock_response
        )

        # Act
        nexset = mock_client.nexsets.activate(nexset_id)

        # Assert
        assert isinstance(nexset, Nexset)
        assert nexset.status == "ACTIVE"
        mock_client.http_client.assert_request_made(
            "PUT", f"/data_sets/{nexset_id}/activate"
        )

    def test_pause_nexset(self, mock_client):
        """Test pausing nexset."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(id=nexset_id, status="PAUSED")
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/pause", mock_response
        )

        # Act
        nexset = mock_client.nexsets.pause(nexset_id)

        # Assert
        assert isinstance(nexset, Nexset)
        assert nexset.status == "PAUSED"
        mock_client.http_client.assert_request_made(
            "PUT", f"/data_sets/{nexset_id}/pause"
        )

    def test_get_samples(self, mock_client):
        """Test getting nexset samples."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_sample1 = mock_factory.create_mock_nexset_sample()
        mock_sample2 = mock_factory.create_mock_nexset_sample()
        mock_response = [mock_sample1, mock_sample2]
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/samples", mock_response
        )

        # Act
        samples = mock_client.nexsets.get_samples(
            nexset_id, count=5, include_metadata=True
        )

        # Assert
        assert len(samples) == 2
        mock_client.http_client.assert_request_made(
            "GET", f"/data_sets/{nexset_id}/samples"
        )

        # Verify parameters
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("count") == 5
        assert request["params"].get("include_metadata") == True

    def test_get_samples_with_live_option(self, mock_client):
        """Test getting live samples."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = [mock_factory.create_mock_nexset_sample()]
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/samples", mock_response
        )

        # Act
        mock_client.nexsets.get_samples(nexset_id, live=True)

        # Assert
        mock_client.http_client.assert_request_made(
            "GET", f"/data_sets/{nexset_id}/samples"
        )
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("live") == True

    def test_copy_nexset(self, mock_client):
        """Test copying nexset."""
        # Arrange
        nexset_id = 1001
        copy_options = NexsetCopyOptions(copy_access_controls=True, owner_id=123)
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(
            id=1002, copied_from_id=nexset_id
        )
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/copy", mock_response
        )

        # Act
        copied_nexset = mock_client.nexsets.copy(nexset_id, copy_options)

        # Assert
        assert isinstance(copied_nexset, Nexset)
        assert copied_nexset.id == 1002
        mock_client.http_client.assert_request_made(
            "POST", f"/data_sets/{nexset_id}/copy"
        )

    def test_copy_nexset_without_options(self, mock_client):
        """Test copying nexset without options."""
        # Arrange
        nexset_id = 1001
        mock_factory = MockDataFactory()
        mock_response = mock_factory.create_mock_nexset(id=1002)
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/copy", mock_response
        )

        # Act
        mock_client.nexsets.copy(nexset_id)

        # Assert
        mock_client.http_client.assert_request_made(
            "POST", f"/data_sets/{nexset_id}/copy"
        )

    def test_http_error_handling(self, mock_client):
        """Test HTTP error handling."""
        # Arrange
        mock_client.http_client.add_error(
            "/data_sets",
            HttpClientError(
                "Server Error",
                status_code=500,
                response={"message": "Internal server error"},
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.nexsets.list()

        assert exc_info.value.status_code == 500

    def test_not_found_error(self, mock_client):
        """Test not found error handling."""
        # Arrange
        nexset_id = 99999
        mock_client.http_client.add_error(
            f"/data_sets/{nexset_id}",
            HttpClientError(
                "Not found", status_code=404, response={"message": "Nexset not found"}
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.nexsets.get(nexset_id)

    def test_validation_error_handling(self, mock_client):
        """Test validation error handling."""
        # Arrange
        invalid_response = {
            # Missing required 'id' field
            "name": "Invalid Dataset"
        }
        mock_client.http_client.add_response("/data_sets/1001", invalid_response)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.nexsets.get(1001)

        # Check that the error mentions the missing fields
        error_str = str(exc_info.value)
        assert "id" in error_str

    def test_empty_list_response(self, mock_client):
        """Test handling empty list response."""
        # Arrange
        mock_client.http_client.add_response("/data_sets", [])

        # Act
        nexsets = mock_client.nexsets.list()

        # Assert
        assert nexsets == []
        assert len(nexsets) == 0

    def test_list_docs(self, mock_client):
        """Test listing docs for a nexset."""
        # Arrange
        nexset_id = 419706
        mock_factory = MockDataFactory()
        mock_response = [
            mock_factory.create_mock_doc_container(
                id=25122, name="Doc 1", text="# Heading\n\nbody"
            )
        ]
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/docs", mock_response
        )

        # Act
        docs = mock_client.nexsets.list_docs(nexset_id)

        # Assert
        assert len(docs) == 1
        assert isinstance(docs[0], DocContainer)
        assert docs[0].id == 25122
        assert docs[0].text == "# Heading\n\nbody"
        mock_client.http_client.assert_request_made(
            "GET", f"/data_sets/{nexset_id}/docs"
        )
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("expand") == 1

    def test_list_docs_no_expand(self, mock_client):
        """Test listing docs without the expand flag."""
        # Arrange
        nexset_id = 419706
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/docs", []
        )

        # Act
        docs = mock_client.nexsets.list_docs(nexset_id, expand=False)

        # Assert
        assert docs == []
        request = mock_client.http_client.get_last_request()
        assert "expand" not in request["params"]

    def test_update_docs(self, mock_client):
        """Test replacing docs on a nexset using DocContainerInput."""
        # Arrange
        nexset_id = 419706
        mock_factory = MockDataFactory()
        mock_response = [
            mock_factory.create_mock_doc_container(
                id=25124, name="Doc 1", text="# Heading\n\nbody"
            )
        ]
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/docs", mock_response
        )

        new_doc = DocContainerInput(
            name="Doc 1",
            description="d",
            text="# Heading\n\nbody",
        )

        # Act
        result = mock_client.nexsets.update_docs(nexset_id, [new_doc])

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], DocContainer)
        assert result[0].id == 25124
        mock_client.http_client.assert_request_made(
            "POST", f"/data_sets/{nexset_id}/docs"
        )
        request = mock_client.http_client.get_last_request()
        assert "docs" in request["json"]
        assert len(request["json"]["docs"]) == 1
        sent = request["json"]["docs"][0]
        assert sent["name"] == "Doc 1"
        assert sent["text"] == "# Heading\n\nbody"
        assert sent["doc_type"] == "md"

    def test_update_docs_accepts_dicts(self, mock_client):
        """Test update_docs accepts plain dicts (e.g. from MCP layer)."""
        # Arrange
        nexset_id = 419706
        mock_client.http_client.add_response(
            f"/data_sets/{nexset_id}/docs", []
        )

        # Act — pass a plain dict, not a DocContainerInput
        mock_client.nexsets.update_docs(
            nexset_id,
            [{"name": "Raw", "doc_type": "md", "text": "# x"}],
        )

        # Assert
        request = mock_client.http_client.get_last_request()
        assert request["json"] == {
            "docs": [{"name": "Raw", "doc_type": "md", "text": "# x"}]
        }

    def test_copy_docs(self, mock_client):
        """Test copy_docs reads source, strips server fields, writes dest."""
        # Arrange
        src_id = 419706
        dst_id = 419800
        mock_factory = MockDataFactory()

        # Source docs include all server-owned fields that must be stripped
        source_docs = [
            mock_factory.create_mock_doc_container(
                id=25122,
                name="Doc 1",
                description="desc 1",
                doc_type="md",
                text="# body 1",
                public=False,
                tags=["a"],
                copied_from_id=None,
            )
        ]
        # Destination response after the POST
        dest_docs = [
            mock_factory.create_mock_doc_container(
                id=99999, name="Doc 1", text="# body 1", copied_from_id=25122
            )
        ]

        mock_client.http_client.add_response(
            f"/data_sets/{src_id}/docs", source_docs
        )
        mock_client.http_client.add_response(
            f"/data_sets/{dst_id}/docs", dest_docs
        )

        # Act
        result = mock_client.nexsets.copy_docs(src_id, dst_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == 99999
        assert result[0].copied_from_id == 25122

        # Verify GET to source
        get_requests = mock_client.http_client.get_requests_by_url_pattern(
            f"/data_sets/{src_id}/docs"
        )
        assert any(r["method"] == "GET" for r in get_requests)

        # Verify POST to destination with stripped body
        dest_requests = mock_client.http_client.get_requests_by_url_pattern(
            f"/data_sets/{dst_id}/docs"
        )
        post_requests = [r for r in dest_requests if r["method"] == "POST"]
        assert len(post_requests) == 1
        sent_docs = post_requests[0]["json"]["docs"]
        assert len(sent_docs) == 1
        sent = sent_docs[0]

        # Writable fields are carried over
        assert sent["name"] == "Doc 1"
        assert sent["description"] == "desc 1"
        assert sent["doc_type"] == "md"
        assert sent["text"] == "# body 1"

        # Server-owned and read-only fields are stripped
        for stripped in (
            "id",
            "owner",
            "org",
            "access_roles",
            "copied_from_id",
            "created_at",
            "updated_at",
            "repo_type",
            "repo_config",
            "public",
            "tags",
        ):
            assert stripped not in sent, f"{stripped!r} should be stripped"

    def test_copy_docs_empty_source(self, mock_client):
        """Test copy_docs no-ops when source has no docs."""
        # Arrange
        src_id = 419706
        dst_id = 419800
        mock_client.http_client.add_response(
            f"/data_sets/{src_id}/docs", []
        )

        # Act
        result = mock_client.nexsets.copy_docs(src_id, dst_id)

        # Assert
        assert result == []
        # No POST should have been made to the destination
        dest_requests = mock_client.http_client.get_requests_by_url_pattern(
            f"/data_sets/{dst_id}/docs"
        )
        assert all(r["method"] != "POST" for r in dest_requests)
