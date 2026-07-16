"""Tests for the AutoPipeline context layer."""

import pytest
from datetime import datetime

from autopipeline.context import (
    SchemaFieldInfo,
    DatasetContext,
    PipelineContext,
    ContextCollector,
    short_name,
    extract_platform_from_urn,
)


class TestHelpers:
    def test_short_name_dbt(self):
        urn = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.db.table,PROD)"
        assert short_name(urn) == "db.table"

    def test_short_name_no_prefix(self):
        urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.table,PROD)"
        assert short_name(urn) == "db.table"

    def test_short_name_other(self):
        assert short_name("urn:li:corpuser:user1") == "user1"

    def test_extract_platform_dbt(self):
        urn = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.db.table,PROD)"
        assert extract_platform_from_urn(urn) == "dbt"

    def test_extract_platform_snowflake(self):
        urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.db.table,PROD)"
        assert extract_platform_from_urn(urn) == "snowflake"

    def test_extract_platform_unknown(self):
        assert extract_platform_from_urn("urn:li:corpuser:u1") == "unknown"


class TestSchemaFieldInfo:
    def test_create_with_defaults(self):
        f = SchemaFieldInfo(field_path="id", native_type="NUMBER")
        assert f.field_path == "id"
        assert f.native_type == "NUMBER"
        assert f.description == ""
        assert f.nullable is True
        assert f.tags == []
        assert f.terms == []

    def test_create_full(self):
        f = SchemaFieldInfo(
            field_path="email",
            native_type="TEXT",
            description="User email address",
            nullable=False,
            tags=["PII"],
            terms=["GDPR"],
        )
        assert f.field_path == "email"
        assert f.description == "User email address"
        assert f.nullable is False
        assert "PII" in f.tags


class TestDatasetContext:
    def test_create_minimal(self):
        ds = DatasetContext(urn="test:urn", name="test_ds")
        assert ds.urn == "test:urn"
        assert ds.name == "test_ds"
        assert ds.schema_fields == []
        assert ds.upstreams == []

    def test_create_with_schema(self):
        fields = [
            SchemaFieldInfo("id", "NUMBER", "Primary key"),
            SchemaFieldInfo("name", "TEXT", "Full name"),
        ]
        ds = DatasetContext(
            urn="urn:li:dataset:(urn:li:dataPlatform:dbt,test,PROD)",
            name="test_ds",
            platform="dbt",
            schema_fields=fields,
            owners=["user:john"],
            tags=["PII"],
            upstreams=["src:table1"],
            downstreams=["dest:table2"],
        )
        assert len(ds.schema_fields) == 2
        assert len(ds.owners) == 1
        assert "PII" in ds.tags
        assert "src:table1" in ds.upstreams
        assert "dest:table2" in ds.downstreams


class TestPipelineContext:
    def test_create_empty(self):
        target = DatasetContext(urn="t:urn", name="target")
        ctx = PipelineContext(target_dataset=target)
        assert ctx.target_dataset.name == "target"
        assert ctx.upstream_datasets == []
        assert ctx.downstream_datasets == []
        assert ctx.fetched_at == ""

    def test_create_full(self):
        target = DatasetContext(urn="t:urn", name="target")
        upstream = [DatasetContext(urn="u:urn", name="source1")]
        downstream = [DatasetContext(urn="d:urn", name="consumer1")]
        ctx = PipelineContext(
            target_dataset=target,
            upstream_datasets=upstream,
            downstream_datasets=downstream,
            all_datasets=[target] + upstream + downstream,
            fetched_at="2026-01-01T00:00:00Z",
        )
        assert len(ctx.upstream_datasets) == 1
        assert len(ctx.downstream_datasets) == 1
        assert len(ctx.all_datasets) == 3
        assert ctx.fetched_at == "2026-01-01T00:00:00Z"
