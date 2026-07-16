"""Tests for the pipeline generator."""

from pathlib import Path

from autopipeline.generator import PipelineGenerator, _infer_tests
from autopipeline.context import (
    PipelineContext, DatasetContext, SchemaFieldInfo,
)


def _make_test_ctx() -> PipelineContext:
    target = DatasetContext(
        urn="urn:li:dataset:(urn:li:dataPlatform:dbt,db.analytics.orders,PROD)",
        name="orders_v2",
        description="Consolidated orders view",
        platform="urn:li:dataPlatform:dbt",
        schema_fields=[
            SchemaFieldInfo("order_id", "NUMBER", "Unique order ID"),
            SchemaFieldInfo("customer_id", "NUMBER", "Customer FK"),
            SchemaFieldInfo("email", "TEXT", "Customer email"),
            SchemaFieldInfo("amount", "FLOAT", "Order amount"),
        ],
        tags=["urn:li:tag:production"],
    )
    source1 = DatasetContext(
        urn="urn:li:dataset:(urn:li:dataPlatform:postgres,db.raw.orders,PROD)",
        name="orders",
        platform="urn:li:dataPlatform:postgres",
        schema_fields=[
            SchemaFieldInfo("order_id", "NUMBER", ""),
            SchemaFieldInfo("customer_id", "NUMBER", ""),
            SchemaFieldInfo("amount", "FLOAT", ""),
        ],
    )
    return PipelineContext(
        target_dataset=target,
        upstream_datasets=[source1],
        fetched_at="2026-01-01T00:00:00Z",
    )


class TestGenerator:
    def setup_method(self):
        self.gen = PipelineGenerator()
        self.ctx = _make_test_ctx()

    def test_dbt_model_renders(self):
        sql = self.gen.generate_dbt_model(self.ctx, "orders_v2")
        assert "orders_v2" in sql
        assert "config(" in sql
        assert "WITH" in sql
        assert "SELECT * FROM final" in sql

    def test_dbt_schema_yml(self):
        yml = self.gen.generate_dbt_schema_yml(self.ctx, "orders_v2")
        assert "version: 2" in yml
        assert "orders_v2" in yml
        assert "order_id" in yml

    def test_sql_transform(self):
        sql = self.gen.generate_sql(self.ctx)
        assert "WITH" in sql
        assert "SELECT * FROM transformed" in sql

    def test_airflow_dag(self):
        dag = self.gen.generate_airflow_dag(self.ctx, "orders_v2")
        assert "DAG" in dag
        assert "orders_v2" in dag

    def test_write_artifacts_dbt(self, tmp_path):
        artifacts = self.gen.write_artifacts(self.ctx, "orders_v2",
                                              output_dir=str(tmp_path),
                                              framework="dbt")
        assert "model_sql" in artifacts
        assert "schema_yml" in artifacts
        assert Path(artifacts["model_sql"]).exists()
        assert Path(artifacts["schema_yml"]).exists()

    def test_write_artifacts_sql(self, tmp_path):
        artifacts = self.gen.write_artifacts(self.ctx, "my_transform",
                                              output_dir=str(tmp_path),
                                              framework="sql")
        assert "sql" in artifacts
        assert Path(artifacts["sql"]).exists()

    def test_write_artifacts_dag(self, tmp_path):
        artifacts = self.gen.write_artifacts(self.ctx, "my_dag",
                                              output_dir=str(tmp_path),
                                              framework="dag")
        assert "dag" in artifacts
        assert Path(artifacts["dag"]).exists()


class TestInferTests:
    def test_id_field(self):
        class FakeField:
            field_path = "order_id"
        assert "not_null" in _infer_tests(FakeField())

    def test_email_field(self):
        class FakeField:
            field_path = "customer_email"
        assert "unique" in _infer_tests(FakeField())

    def test_plain_field(self):
        class FakeField:
            field_path = "amount"
        assert _infer_tests(FakeField()) == []
