"""Tests for the context composer."""

from autopipeline.context import DatasetContext, SchemaFieldInfo
from autopipeline.context_composer import (
    compose_schema_prompt,
    compose_pipeline_prompt,
    compose_writer_context,
)


class TestComposeSchemaPrompt:
    def test_minimal_dataset(self):
        ds = DatasetContext(urn="u:urn", name="test")
        prompt = compose_schema_prompt(ds)
        assert "Dataset: test" in prompt
        assert "Columns (0 total)" in prompt

    def test_with_schema(self):
        ds = DatasetContext(
            urn="u:urn", name="customers",
            schema_fields=[
                SchemaFieldInfo("id", "NUMBER", "Primary key"),
                SchemaFieldInfo("email", "TEXT", "Email address"),
            ],
        )
        prompt = compose_schema_prompt(ds)
        assert "| id | NUMBER | Primary key |" in prompt or "id" in prompt
        assert "| email | TEXT | Email address |" in prompt or "email" in prompt

    def test_with_lineage(self):
        ds = DatasetContext(
            urn="u:urn", name="orders",
            upstreams=["up:src1", "up:src2"],
            downstreams=["down:dest1"],
        )
        prompt = compose_schema_prompt(ds)
        assert "Upstream Sources" in prompt
        assert "Downstream Consumers" in prompt


class TestComposePipelinePrompt:
    def test_full_pipeline(self):
        from autopipeline.context import PipelineContext
        target = DatasetContext(urn="t:urn", name="daily_revenue")
        up1 = DatasetContext(urn="u:urn", name="orders",
                             schema_fields=[SchemaFieldInfo("amount", "FLOAT", "Order amount")])
        ctx = PipelineContext(
            target_dataset=target,
            upstream_datasets=[up1],
            fetched_at="2026-01-01T00:00:00Z",
        )
        prompt = compose_pipeline_prompt(ctx, user_request="Show daily revenue", framework="dbt")
        assert "daily_revenue" in prompt
        assert "daily revenue" in prompt
        assert "Generation Instructions" in prompt
        assert "dbt Model" in prompt
        assert "CTEs" in prompt

    def test_dag_framework(self):
        from autopipeline.context import PipelineContext
        target = DatasetContext(urn="t:urn", name="report")
        ctx = PipelineContext(target_dataset=target, fetched_at="now")
        prompt = compose_pipeline_prompt(ctx, framework="dag")
        assert "dag" in prompt or "DAG" in prompt
