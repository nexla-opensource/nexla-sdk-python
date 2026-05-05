"""Mock response builders for creating realistic test data."""

# Set a seed for deterministic test data generation
# Can be overridden by environment variable for debugging
import os
from datetime import timezone
from typing import Any, Dict, List, Optional

from faker import Faker

faker_seed = int(os.getenv("FAKER_SEED", "12345"))
fake = Faker()
Faker.seed(faker_seed)


class MockResponseBuilder:
    """Builder for creating realistic mock API responses."""

    @staticmethod
    def credential(credential_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock credential response matching the API documentation."""
        base = {
            "id": credential_id or fake.random_int(1, 10000),
            "name": f"{fake.company()} Credentials",
            "description": fake.text(max_nb_chars=100) if fake.boolean() else None,
            "credentials_type": fake.random_element(
                ["s3", "postgres", "mysql", "ftp", "gcs"]
            ),
            "credentials_version": "1",
            "verified_status": fake.random_element(
                ["VERIFIED", "UNVERIFIED", "FAILED"]
            ),
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "access_roles": ["owner"],
            "managed": fake.boolean(),
            "tags": [fake.word() for _ in range(fake.random_int(0, 3))],
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def source(
        source_id: Optional[int] = None,
        include_credentials: bool = False,
        include_datasets: bool = False,
        **overrides,
    ) -> Dict[str, Any]:
        """Build a mock source response matching the API documentation."""
        base = {
            "id": source_id or fake.random_int(1, 10000),
            "name": f"{fake.company()} Data Source",
            "description": fake.text(max_nb_chars=200) if fake.boolean() else None,
            "status": fake.random_element(
                ["ACTIVE", "PAUSED", "DRAFT", "DELETED", "ERROR", "INIT"]
            ),
            "source_type": fake.random_element(
                ["s3", "postgres", "mysql", "api_push", "ftp", "gcs", "bigquery"]
            ),
            "ingest_method": fake.random_element(["POLL", "API", "STREAMING"]),
            "source_format": fake.random_element(["JSON", "CSV", "XML", "PARQUET"]),
            "managed": fake.boolean(),
            "auto_generated": fake.boolean(),
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "access_roles": ["owner"],
            "data_sets": [],
            "data_credentials": None,
            "tags": [fake.word() for _ in range(fake.random_int(0, 3))],
            "run_ids": [],
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }

        if include_credentials:
            base["data_credentials"] = MockResponseBuilder.credential()
            base["data_credentials_id"] = base["data_credentials"]["id"]

        if include_datasets:
            base["data_sets"] = [
                MockResponseBuilder.dataset_brief()
                for _ in range(fake.random_int(1, 3))
            ]

        base.update(overrides)
        return base

    @staticmethod
    def dataset_brief(dataset_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock dataset brief response."""
        base = {
            "id": dataset_id or fake.random_int(1, 10000),
            "owner_id": fake.random_int(1, 1000),
            "org_id": fake.random_int(1, 100),
            "name": f"Dataset #{fake.random_int(1, 100)} - {fake.word()}",
            "description": f"DataSet #{fake.random_int(1, 100)} detected from {fake.company()}",
            "version": fake.random_int(1, 10),
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def destination(destination_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a destination response."""
        factory = MockDataFactory()
        base_destination = factory.create_mock_destination()
        if destination_data:
            base_destination.update(destination_data)
        return base_destination

    @staticmethod
    def data_set_info(data_set_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a data set info response."""
        factory = MockDataFactory()
        base_data_set = factory.create_mock_data_set_info()
        if data_set_data:
            base_data_set.update(data_set_data)
        return base_data_set

    @staticmethod
    def data_map_info(data_map_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a data map info response."""
        factory = MockDataFactory()
        base_data_map = factory.create_mock_data_map_info()
        if data_map_data:
            base_data_map.update(data_map_data)
        return base_data_map

    @staticmethod
    def nexset(nexset_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a nexset response."""
        factory = MockDataFactory()
        base_nexset = factory.create_mock_nexset()
        if nexset_data:
            base_nexset.update(nexset_data)
        return base_nexset

    @staticmethod
    def nexset_sample(sample_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a nexset sample response."""
        factory = MockDataFactory()
        base_sample = factory.create_mock_nexset_sample()
        if sample_data:
            base_sample.update(sample_data)
        return base_sample

    @staticmethod
    def lookup(lookup_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock lookup response."""
        base = {
            "id": lookup_id or fake.random_int(1, 10000),
            "name": f"{fake.company()} Lookup",
            "description": fake.text(max_nb_chars=200) if fake.boolean() else None,
            "map_primary_key": "key",
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {
                "id": fake.random_int(1, 100),
                "name": fake.company(),
                "email_domain": fake.domain_name(),
            },
            "access_roles": ["owner"],
            "public": fake.boolean(),
            "managed": fake.boolean(),
            "data_type": fake.random_element(["string", "integer", "number"]),
            "emit_data_default": fake.boolean(),
            "use_versioning": fake.boolean(),
            "data_format": fake.random_element([None, "json", "csv"]),
            "data_sink_id": fake.random_int(1, 1000) if fake.boolean() else None,
            "data_defaults": {"key": "default_key", "value": "default_value"},
            "data_set_id": fake.random_int(1, 1000) if fake.boolean() else None,
            "map_entry_count": fake.random_int(0, 1000),
            "map_entry_schema": {
                "type": "object",
                "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
                "$schema": "http://json-schema.org/draft-04/schema#",
                "$schema-id": fake.random_int(1000000, 9999999),
            },
            "tags": [fake.word() for _ in range(fake.random_int(0, 3))],
            "created_at": fake.past_datetime().isoformat() + "Z",
            "updated_at": fake.past_datetime().isoformat() + "Z",
        }
        return {**base, **overrides}

    @staticmethod
    def lookup_entry(**overrides) -> Dict[str, Any]:
        """Build a mock lookup entry response."""
        base = {
            "key": fake.word(),
            "value": fake.sentence(),
        }
        # Add some additional fields for complex entries
        if fake.boolean():
            base.update({"description": fake.sentence(), "category": fake.word()})
        return {**base, **overrides}

    @staticmethod
    def user(user_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock user response."""
        base = {
            "id": user_id or fake.random_int(1, 10000),
            "email": fake.email(),
            "full_name": fake.name(),
            "super_user": fake.boolean(),
            "impersonated": False,
            "default_org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "user_tier": fake.random_element(["FREE", "TRIAL", "PAID", "FREE_FOREVER"]),
            "status": fake.random_element(
                ["ACTIVE", "DEACTIVATED", "SOURCE_COUNT_CAPPED"]
            ),
            "account_locked": fake.boolean(),
            "org_memberships": [],
            "api_key": f"<API-Key-{fake.random_int(1000, 9999)}>",
            "email_verified_at": (
                fake.date_time(tzinfo=timezone.utc).isoformat()
                if fake.boolean()
                else None
            ),
            "tos_signed_at": (
                fake.date_time(tzinfo=timezone.utc).isoformat()
                if fake.boolean()
                else None
            ),
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def organization(org_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock organization response."""
        factory = MockDataFactory()
        base = factory.create_mock_organization(id=org_id)
        base.update(overrides)
        return base

    @staticmethod
    def org_member(member_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock org member response."""
        factory = MockDataFactory()
        base = factory.create_mock_org_member(id=member_id)
        base.update(overrides)
        return base

    @staticmethod
    def account_summary(org_id: int, **overrides) -> Dict[str, Any]:
        """Build a mock account summary response."""
        base = {
            "org_id": org_id,
            "data_sources": {"total": 10, "active": 8, "paused": 2},
            "data_sets": {
                "derived": {"total": 5, "active": 5},
                "detected": {"total": 5, "active": 5},
            },
            "data_sinks": {"total": 10, "active": 10},
        }
        base.update(overrides)
        return base

    @staticmethod
    def audit_log_entry(**overrides) -> Dict[str, Any]:
        """Build a mock audit log entry response."""
        factory = MockDataFactory()
        base = factory.create_mock_audit_log_entry()
        base.update(overrides)
        return base

    @staticmethod
    def team(team_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock team response."""
        base = {
            "id": team_id or fake.random_int(1, 1000),
            "name": f"{fake.word().title()} Team",
            "description": fake.text(max_nb_chars=200),
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "member": fake.boolean(),
            "members": [],
            "access_roles": ["owner"],
            "tags": [fake.word() for _ in range(fake.random_int(0, 3))],
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def team_member(user_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock team member response."""
        base = {
            "id": user_id or fake.random_int(1, 10000),
            "email": fake.email(),
            "admin": fake.boolean(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def org_membership(org_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock org membership response."""
        base = {
            "id": org_id or fake.random_int(1, 100),
            "name": fake.company(),
            "is_admin": fake.boolean(),
            "org_membership_status": fake.random_element(["ACTIVE", "DEACTIVATED"]),
            "api_key": f"<Org-API-Key-{fake.random_int(1000, 9999)}>",
        }
        base.update(overrides)
        return base

    @staticmethod
    def project(project_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock project response."""
        base = {
            "id": project_id or fake.random_int(1, 1000),
            "name": f"{fake.word().title()} Project",
            "description": fake.text(max_nb_chars=200),
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "data_flows": [],
            "flows": [],
            "access_roles": ["owner"],
            "tags": [fake.word() for _ in range(fake.random_int(0, 3))],
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def notification(
        notification_id: Optional[int] = None, **overrides
    ) -> Dict[str, Any]:
        """Build a mock notification response."""
        base = {
            "id": notification_id or fake.random_int(1, 10000),
            "owner": {
                "id": fake.random_int(1, 1000),
                "full_name": fake.name(),
                "email": fake.email(),
            },
            "org": {"id": fake.random_int(1, 100), "name": fake.company()},
            "access_roles": ["owner"],
            "level": fake.random_element(
                ["DEBUG", "INFO", "WARN", "ERROR", "RECOVERED"]
            ),
            "resource_id": fake.random_int(1, 10000),
            "resource_type": fake.random_element(["SOURCE", "SINK", "DATASET"]),
            "message_id": fake.random_int(1, 1000),
            "message": fake.text(max_nb_chars=200),
            "read_at": (
                fake.date_time(tzinfo=timezone.utc).isoformat()
                if fake.boolean()
                else None
            ),
            "created_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def flow_response(**overrides) -> Dict[str, Any]:
        """Build a mock flow response."""
        base = {
            "flows": [
                MockResponseBuilder.flow_node() for _ in range(fake.random_int(1, 3))
            ],
            "data_sources": [],
            "data_sets": [],
            "data_sinks": [],
            "data_credentials": [],
            "metrics": [],
        }
        base.update(overrides)
        return base

    @staticmethod
    def flow_node(node_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        """Build a mock flow node."""
        base = {
            "id": node_id or fake.random_int(1, 10000),
            "origin_node_id": fake.random_int(1, 10000),
            "parent_node_id": fake.random_int(1, 10000) if fake.boolean() else None,
            "data_source_id": fake.random_int(1, 10000) if fake.boolean() else None,
            "data_set_id": fake.random_int(1, 10000) if fake.boolean() else None,
            "data_sink_id": fake.random_int(1, 10000) if fake.boolean() else None,
            "status": fake.random_element(["ACTIVE", "PAUSED", "ERROR"]),
            "project_id": fake.random_int(1, 1000) if fake.boolean() else None,
            "flow_type": fake.random_element(["batch", "streaming"]),
            "name": f"{fake.word()} Flow Node" if fake.boolean() else None,
            "description": fake.text(max_nb_chars=100) if fake.boolean() else None,
            "children": [],
        }
        base.update(overrides)
        return base

    @staticmethod
    def probe_response(**overrides) -> Dict[str, Any]:
        """Build a probe response."""
        base = {
            "status": "success",
            "message": "Probe completed successfully",
            "connection_verified": True,
            "timestamp": fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base.update(overrides)
        return base

    @staticmethod
    def probe_tree_response(connection_type: str = "s3", **overrides) -> Dict[str, Any]:
        """Build a probe tree response."""
        base = {
            "status": "ok",
            "message": "Tree probe completed",
            "connection_type": connection_type,
            "object": {
                "tree": [
                    {
                        "name": "folder1",
                        "type": "folder",
                        "path": "/folder1",
                        "children": [
                            {
                                "name": "file1.csv",
                                "type": "file",
                                "path": "/folder1/file1.csv",
                                "size": 1024,
                            }
                        ],
                    }
                ]
            },
        }
        base.update(overrides)
        return base

    @staticmethod
    def probe_sample_response(
        connection_type: str = "s3", **overrides
    ) -> Dict[str, Any]:
        """Build a probe sample response."""
        base = {
            "status": "ok",
            "message": "Sample probe completed",
            "connection_type": connection_type,
            "output": {
                "sample_data": [
                    {"id": 1, "name": "Sample Row 1", "value": 100},
                    {"id": 2, "name": "Sample Row 2", "value": 200},
                ],
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "value", "type": "integer"},
                    ]
                },
            },
        }
        base.update(overrides)
        return base

    @staticmethod
    def webhook_send_response(
        dataset_id: Optional[int] = None, processed: int = 1, **overrides
    ) -> Dict[str, Any]:
        """Build a mock webhook send response."""
        base = {
            "dataset_id": dataset_id or fake.random_int(1, 10000),
            "processed": processed,
        }
        base.update(overrides)
        return base

    @staticmethod
    def flow_log_entry(**overrides) -> Dict[str, Any]:
        """Build a mock flow log entry."""
        base = {
            "log": fake.sentence(),
            "log_type": fake.random_element(["LOG", "EVENT"]),
            "severity": fake.random_element(["DEBUG", "INFO", "WARN", "ERROR"]),
            "resource_id": fake.random_int(1, 10000),
            "resource_type": fake.random_element(["SOURCE", "DATASET", "SINK"]),
            "timestamp": fake.random_int(1700000000000, 1800000000000),
        }
        base.update(overrides)
        return base

    @staticmethod
    def flow_logs_response(log_count: int = 3, **overrides) -> Dict[str, Any]:
        """Build a mock flow logs response."""
        logs = [MockResponseBuilder.flow_log_entry() for _ in range(log_count)]
        base = {
            "status": 200,
            "message": "Ok",
            "logs": {
                "data": logs,
                "meta": {
                    "org_id": fake.random_int(1, 10000),
                    "run_id": fake.random_int(1, 10000),
                    "current_page": 1,
                    "pages_count": 1,
                    "total_count": log_count,
                },
            },
        }
        base.update(overrides)
        return base

    @staticmethod
    def flow_metrics_api_response(**overrides) -> Dict[str, Any]:
        """Build a mock flow metrics API response."""
        resource_id = str(fake.random_int(1, 10000))
        base = {
            "status": 200,
            "message": "Ok",
            "metrics": {
                "data": {
                    resource_id: {
                        "records": fake.random_int(0, 10000),
                        "size": fake.random_int(0, 100000),
                        "errors": fake.random_int(0, 100),
                        "runId": fake.random_int(1, 10000),
                    }
                },
                "meta": {"currentPage": 1, "pageCount": 1, "totalCount": 1},
            },
        }
        base.update(overrides)
        return base

    @staticmethod
    def docs_recommendation_response(**overrides) -> Dict[str, Any]:
        """Build a mock docs recommendation response."""
        base = {"recommendation": fake.paragraph(), "status": "success"}
        base.update(overrides)
        return base


class MockDataFactory:
    """Factory for generating mock data for testing."""

    def __init__(self):
        self.fake = Faker()

    def create_mock_owner(self, **kwargs) -> Dict[str, Any]:
        """Create mock owner data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "full_name": kwargs.get("full_name", self.fake.name()),
            "email": kwargs.get("email", self.fake.email()),
            "email_verified_at": kwargs.get(
                "email_verified_at",
                self.fake.date_time(tzinfo=timezone.utc).isoformat(),
            ),
        }

    def create_mock_organization(self, **kwargs) -> Dict[str, Any]:
        """Create mock organization data."""
        base_data = {
            "name": self.fake.company(),
            "description": self.fake.sentence(),
            "email_domain": self.fake.domain_name(),
            "access_roles": ["owner"],
            "account_tier": self.create_mock_org_tier(),
            "created_at": self.fake.date_time(tzinfo=timezone.utc).isoformat(),
            "updated_at": self.fake.date_time(tzinfo=timezone.utc).isoformat(),
        }
        base_data.update(kwargs)
        if "id" not in base_data:
            base_data["id"] = self.fake.random_int(min=1, max=1000)
        return base_data

    def create_mock_org_tier(self, **kwargs) -> Dict[str, Any]:
        """Create mock org tier data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10)),
            "name": kwargs.get("name", "FREE"),
            "display_name": kwargs.get("display_name", "Free"),
            "record_count_limit": kwargs.get("record_count_limit", 1000000),
            "record_count_limit_time": kwargs.get("record_count_limit_time", "DAILY"),
            "data_source_count_limit": kwargs.get("data_source_count_limit", 3),
        }

    def create_mock_audit_log_entry(self, **kwargs) -> Dict[str, Any]:
        """Create a mock audit log entry."""
        return {
            "id": self.fake.random_int(min=1, max=100000),
            "item_type": self.fake.random_element(["DataSource", "DataSink", "User"]),
            "item_id": self.fake.random_int(min=1, max=10000),
            "event": self.fake.random_element(["create", "update", "delete"]),
            "org_id": self.fake.random_int(min=1, max=1000),
            "owner_id": self.fake.random_int(min=1, max=10000),
            "owner_email": self.fake.email(),
            "created_at": self.fake.date_time(tzinfo=timezone.utc).isoformat(),
            "change_summary": [],
            "object_changes": {},
            "request_ip": self.fake.ipv4(),
            "request_user_agent": self.fake.user_agent(),
            "request_url": self.fake.uri(),
            "user": {"id": self.fake.random_int(1, 10000), "email": self.fake.email()},
            **kwargs,
        }

    def create_mock_connector(self, **kwargs) -> Dict[str, Any]:
        """Create mock connector data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=1000)),
            "type": kwargs.get(
                "type", self.fake.random_element(["s3", "postgres", "snowflake"])
            ),
            "connection_type": kwargs.get("connection_type", "database"),
            "name": kwargs.get("name", self.fake.word().title() + " Connector"),
            "description": kwargs.get("description", self.fake.sentence()),
            "nexset_api_compatible": kwargs.get("nexset_api_compatible", True),
        }

    def create_mock_credential(self, **kwargs) -> Dict[str, Any]:
        """Create mock credential data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"Test Credential {self.fake.random_int(min=1, max=100)}"
            ),
            "credentials_type": kwargs.get("credentials_type", "postgres"),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "verified_status": kwargs.get("verified_status", "VERIFIED"),
            "connector": kwargs.get("connector", self.create_mock_connector()),
            "description": kwargs.get("description", self.fake.sentence()),
            "verified_at": kwargs.get(
                "verified_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "managed": kwargs.get("managed", False),
        }

    def create_mock_source(self, **kwargs) -> Dict[str, Any]:
        """Create mock source data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"Test Source {self.fake.random_int(min=1, max=100)}"
            ),
            "status": kwargs.get("status", "ACTIVE"),
            "source_type": kwargs.get("source_type", "postgres"),
            "connector_type": kwargs.get("connector_type", "postgres"),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "managed": kwargs.get("managed", False),
            "auto_generated": kwargs.get("auto_generated", False),
            "connector": kwargs.get("connector", self.create_mock_connector()),
            "description": kwargs.get("description", self.fake.sentence()),
            "ingest_method": kwargs.get("ingest_method", "BATCH"),
            "source_format": kwargs.get("source_format", "JSON"),
            "source_config": kwargs.get("source_config", {"table": "test_table"}),
            "poll_schedule": kwargs.get("poll_schedule"),
            "code_container_id": kwargs.get("code_container_id"),
            "data_credentials_id": kwargs.get(
                "data_credentials_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_credentials": kwargs.get("data_credentials"),
            "data_sets": kwargs.get("data_sets", []),
            "api_keys": kwargs.get("api_keys", []),
            "run_ids": kwargs.get("run_ids", []),
            "copied_from_id": kwargs.get("copied_from_id"),
            "flow_type": kwargs.get("flow_type", "batch"),
            "has_template": kwargs.get("has_template", False),
            "vendor_endpoint": kwargs.get("vendor_endpoint"),
            "vendor": kwargs.get("vendor"),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_destination(self, **kwargs) -> Dict[str, Any]:
        """Create mock destination data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"Test Destination {self.fake.random_int(min=1, max=100)}"
            ),
            "status": kwargs.get("status", "ACTIVE"),
            "sink_type": kwargs.get("sink_type", "postgres"),
            "connector_type": kwargs.get("connector_type", "postgres"),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "managed": kwargs.get("managed", False),
            "connector": kwargs.get("connector", self.create_mock_connector()),
            "description": kwargs.get("description", self.fake.sentence()),
            "data_set_id": kwargs.get(
                "data_set_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_map_id": kwargs.get("data_map_id"),
            "data_source_id": kwargs.get("data_source_id"),
            "sink_format": kwargs.get("sink_format", "json"),
            "sink_config": kwargs.get("sink_config", {"table": "output_table"}),
            "sink_schedule": kwargs.get("sink_schedule"),
            "in_memory": kwargs.get("in_memory", False),
            "data_set": kwargs.get("data_set"),
            "data_map": kwargs.get("data_map"),
            "data_credentials_id": kwargs.get(
                "data_credentials_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_credentials": kwargs.get("data_credentials"),
            "copied_from_id": kwargs.get("copied_from_id"),
            "flow_type": kwargs.get("flow_type", "batch"),
            "has_template": kwargs.get("has_template", False),
            "vendor_endpoint": kwargs.get("vendor_endpoint"),
            "vendor": kwargs.get("vendor"),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_data_set_info(self, **kwargs) -> Dict[str, Any]:
        """Create mock data set info data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"Test Dataset {self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "status": kwargs.get("status", "ACTIVE"),
            "output_schema": kwargs.get(
                "output_schema", {"type": "object", "properties": {}}
            ),
            "version": kwargs.get("version", 1),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_data_map_info(self, **kwargs) -> Dict[str, Any]:
        """Create mock data map info data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "owner_id": kwargs.get("owner_id", self.fake.random_int(min=1, max=1000)),
            "org_id": kwargs.get("org_id", self.fake.random_int(min=1, max=100)),
            "name": kwargs.get(
                "name", f"Test Data Map {self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "public": kwargs.get("public", False),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_nexset(self, **kwargs) -> Dict[str, Any]:
        """Create mock nexset data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"Test Nexset {self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "status": kwargs.get("status", "ACTIVE"),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "flow_type": kwargs.get("flow_type", "batch"),
            "data_source_id": kwargs.get(
                "data_source_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_source": kwargs.get("data_source"),
            "parent_data_sets": kwargs.get("parent_data_sets", []),
            "data_sinks": kwargs.get("data_sinks", []),
            "transform_id": kwargs.get("transform_id"),
            "output_schema": kwargs.get("output_schema", {"type": "object"}),
            "copied_from_id": kwargs.get("copied_from_id"),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_nexset_sample(self, **kwargs) -> Dict[str, Any]:
        """Create mock nexset sample data."""
        return {
            "raw_message": kwargs.get(
                "raw_message",
                {
                    "id": self.fake.random_int(min=1, max=1000),
                    "name": self.fake.name(),
                    "value": self.fake.random_number(digits=3),
                },
            ),
            "nexla_metadata": kwargs.get(
                "nexla_metadata",
                {
                    "timestamp": self.fake.date_time(tzinfo=timezone.utc).isoformat(),
                    "source": "test",
                },
            ),
        }

    def create_mock_lookup(self, **kwargs) -> Dict[str, Any]:
        """Create mock lookup data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "name": kwargs.get(
                "name", f"test_lookup_{self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "map_primary_key": kwargs.get("map_primary_key", "id"),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "public": kwargs.get("public", False),
            "managed": kwargs.get("managed", False),
            "data_type": kwargs.get("data_type", "lookup"),
            "emit_data_default": kwargs.get("emit_data_default", False),
            "use_versioning": kwargs.get("use_versioning", False),
            "data_format": kwargs.get("data_format", "json"),
            "data_sink_id": kwargs.get("data_sink_id"),
            "data_defaults": kwargs.get("data_defaults", {}),
            "data_set_id": kwargs.get("data_set_id"),
            "map_entry_count": kwargs.get("map_entry_count", 0),
            "map_entry_schema": kwargs.get("map_entry_schema", {"type": "object"}),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_lookup_entry(self, **kwargs) -> Dict[str, Any]:
        """Create mock lookup entry data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=1000)),
            "name": kwargs.get("name", self.fake.name()),
            "value": kwargs.get("value", self.fake.word()),
            "metadata": kwargs.get("metadata", {"source": "test"}),
        }

    def create_mock_org_member(self, **kwargs) -> Dict[str, Any]:
        """Create mock org member data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "full_name": kwargs.get("full_name", self.fake.name()),
            "email": kwargs.get("email", self.fake.email()),
            "is_admin?": kwargs.get("is_admin", self.fake.boolean()),
            "access_role": kwargs.get("access_role", ["member"]),
            "org_membership_status": kwargs.get("org_membership_status", "ACTIVE"),
            "user_status": kwargs.get("user_status", "ACTIVE"),
        }

    def create_mock_project(self, **kwargs) -> Dict[str, Any]:
        """Create mock project data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "name": kwargs.get(
                "name", f"Test Project {self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "client_identifier": kwargs.get("client_identifier"),
            "client_url": kwargs.get("client_url"),
            "flows_count": kwargs.get(
                "flows_count", self.fake.random_int(min=0, max=10)
            ),
            "data_flows": kwargs.get("data_flows", []),
            "flows": kwargs.get("flows", []),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "tags": kwargs.get("tags", []),
            "copied_from_id": kwargs.get("copied_from_id"),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_project_data_flow(self, **kwargs) -> Dict[str, Any]:
        """Create mock project data flow data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "project_id": kwargs.get(
                "project_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_source_id": kwargs.get(
                "data_source_id", self.fake.random_int(min=1, max=1000)
            ),
            "data_set_id": kwargs.get("data_set_id"),
            "data_sink_id": kwargs.get("data_sink_id"),
            "name": kwargs.get(
                "name", f"Test Flow {self.fake.random_int(min=1, max=100)}"
            ),
            "description": kwargs.get("description", self.fake.sentence()),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_user(self, **kwargs) -> Dict[str, Any]:
        """Create mock user data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "email": kwargs.get("email", self.fake.email()),
            "full_name": kwargs.get("full_name", self.fake.name()),
            "super_user": kwargs.get("super_user", self.fake.boolean()),
            "impersonated": kwargs.get("impersonated", False),
            "default_org": kwargs.get(
                "default_org",
                {
                    "id": self.fake.random_int(min=1, max=100),
                    "name": self.fake.company(),
                },
            ),
            "user_tier": kwargs.get(
                "user_tier",
                self.fake.random_element(["FREE", "TRIAL", "PAID", "FREE_FOREVER"]),
            ),
            "status": kwargs.get(
                "status",
                self.fake.random_element(
                    ["ACTIVE", "DEACTIVATED", "SOURCE_COUNT_CAPPED"]
                ),
            ),
            "account_locked": kwargs.get("account_locked", self.fake.boolean()),
            "org_memberships": kwargs.get("org_memberships", []),
            "api_key": kwargs.get(
                "api_key", f"<API-Key-{self.fake.random_int(1000, 9999)}>"
            ),
            "email_verified_at": kwargs.get(
                "email_verified_at",
                (
                    self.fake.date_time(tzinfo=timezone.utc).isoformat()
                    if self.fake.boolean()
                    else None
                ),
            ),
            "tos_signed_at": kwargs.get(
                "tos_signed_at",
                (
                    self.fake.date_time(tzinfo=timezone.utc).isoformat()
                    if self.fake.boolean()
                    else None
                ),
            ),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_team(self, **kwargs) -> Dict[str, Any]:
        """Create mock team data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=1000)),
            "name": kwargs.get("name", f"{self.fake.word().title()} Team"),
            "description": kwargs.get("description", self.fake.sentence()),
            "owner": kwargs.get("owner", self.create_mock_owner()),
            "org": kwargs.get("org", self.create_mock_organization()),
            "member": kwargs.get("member", self.fake.boolean()),
            "members": kwargs.get("members", []),
            "access_roles": kwargs.get("access_roles", ["owner"]),
            "tags": kwargs.get("tags", []),
            "created_at": kwargs.get(
                "created_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "updated_at": kwargs.get(
                "updated_at", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
        }

    def create_mock_team_member(self, **kwargs) -> Dict[str, Any]:
        """Create mock team member data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=10000)),
            "email": kwargs.get("email", self.fake.email()),
            "admin": kwargs.get("admin", self.fake.boolean()),
        }

    def create_mock_org_membership(self, **kwargs) -> Dict[str, Any]:
        """Create mock org membership data."""
        return {
            "id": kwargs.get("id", self.fake.random_int(min=1, max=100)),
            "name": kwargs.get("name", self.fake.company()),
            "is_admin": kwargs.get("is_admin", self.fake.boolean()),
            "org_membership_status": kwargs.get(
                "org_membership_status",
                self.fake.random_element(["ACTIVE", "DEACTIVATED"]),
            ),
            "api_key": kwargs.get(
                "api_key", f"<Org-API-Key-{self.fake.random_int(1000, 9999)}>"
            ),
        }

    def create_mock_flow_response(self, **kwargs) -> Dict[str, Any]:
        """Create mock flow response data."""
        include_elements = kwargs.get("include_elements", True)

        base = {
            "flows": [
                {
                    "id": self.fake.random_int(1, 10000),
                    "origin_node_id": self.fake.random_int(1, 10000),
                    "parent_node_id": (
                        self.fake.random_int(1, 10000) if self.fake.boolean() else None
                    ),
                    "data_source_id": (
                        self.fake.random_int(1, 10000) if self.fake.boolean() else None
                    ),
                    "data_set_id": (
                        self.fake.random_int(1, 10000) if self.fake.boolean() else None
                    ),
                    "data_sink_id": (
                        self.fake.random_int(1, 10000) if self.fake.boolean() else None
                    ),
                    "status": "ACTIVE",
                    "project_id": (
                        self.fake.random_int(1, 1000) if self.fake.boolean() else None
                    ),
                    "flow_type": "batch",
                    "ingestion_mode": "POLL",
                    "name": f"Flow {self.fake.random_int(1, 100)}",
                    "description": "Mock flow for testing",
                    "children": [],
                }
            ]
        }

        if include_elements:
            base["data_sources"] = [self.create_mock_source()]
            base["data_sinks"] = [self.create_mock_destination()]
            base["nexsets"] = [self.create_mock_nexset()]

        # Remove include_elements from kwargs before updating
        flow_kwargs = {k: v for k, v in kwargs.items() if k != "include_elements"}
        base.update(flow_kwargs)
        return base

    def create_mock_flow_metrics(self, **kwargs) -> Dict[str, Any]:
        """Create mock flow metrics data."""
        return {
            "origin_node_id": kwargs.get(
                "origin_node_id", self.fake.random_int(1, 10000)
            ),
            "records": kwargs.get("records", self.fake.random_int(0, 10000)),
            "size": kwargs.get("size", self.fake.random_int(0, 100000)),
            "errors": kwargs.get("errors", self.fake.random_int(0, 100)),
            "reporting_date": kwargs.get(
                "reporting_date", self.fake.date_time(tzinfo=timezone.utc).isoformat()
            ),
            "run_id": kwargs.get("run_id", self.fake.random_int(1, 10000)),
        }

    def create_mock_flow_node(
        self,
        max_depth: int = 2,
        current_depth: int = 0,
        parent_node_id: int = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create mock flow node with optional nested children."""
        node_id = kwargs.get("id", self.fake.random_int(1, 10000))
        node = {
            "id": node_id,
            "origin_node_id": kwargs.get(
                "origin_node_id", self.fake.random_int(1, 10000)
            ),
            "parent_node_id": parent_node_id,
            "data_source_id": kwargs.get(
                "data_source_id",
                self.fake.random_int(1, 10000) if current_depth == 0 else None,
            ),
            "data_set_id": kwargs.get(
                "data_set_id",
                self.fake.random_int(1, 10000) if current_depth > 0 else None,
            ),
            "data_sink_id": kwargs.get("data_sink_id"),
            "status": kwargs.get("status", "ACTIVE"),
            "project_id": kwargs.get("project_id"),
            "flow_type": kwargs.get("flow_type", "batch"),
            "ingestion_mode": kwargs.get("ingestion_mode", "POLL"),
            "name": kwargs.get("name", f"Flow Node {node_id}"),
            "description": kwargs.get("description", "Mock flow node"),
            "children": [],
        }

        # Add children if not at max depth
        if current_depth < max_depth:
            num_children = self.fake.random_int(1, 2)
            for _ in range(num_children):
                child = self.create_mock_flow_node(
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    parent_node_id=node_id,
                )
                node["children"].append(child)

        return node


# Utility functions for list generation
def credential_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock credentials."""
    return [MockResponseBuilder.credential() for _ in range(count)]


def source_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock sources."""
    return [MockResponseBuilder.source() for _ in range(count)]


def destination_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock destinations."""
    return [MockResponseBuilder.destination() for _ in range(count)]


def lookup_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock lookups."""
    return [MockResponseBuilder.lookup() for _ in range(count)]


def user_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock users."""
    return [MockResponseBuilder.user() for _ in range(count)]


def team_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock teams."""
    return [MockResponseBuilder.team() for _ in range(count)]


def project_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of mock projects."""
    return [MockResponseBuilder.project() for _ in range(count)]
