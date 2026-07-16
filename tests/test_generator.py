from pathlib import Path
from autopipeline.context import DatasetContext, PipelineContext, SchemaFieldInfo
from autopipeline.generator import PipelineGenerator, _infer_tests


def _make_ctx():
    target = DatasetContext(urn="u:t", name="orders_v2",
                           schema_fields=[SchemaFieldInfo("id", "NUMBER", ""), SchemaFieldInfo("email", "TEXT", "")],
                           tags=["production"])
    src = DatasetContext(urn="u:s", name="orders", schema_fields=[SchemaFieldInfo("id", "NUMBER", "")])
    return PipelineContext(target_dataset=target, upstream_datasets=[src], fetched_at="2026-01-01")


class TestGenerator:
    def setup_method(self):
        self.gen = PipelineGenerator()
        self.ctx = _make_ctx()

    def test_dbt_model(self):
        sql = self.gen.generate_dbt_model(self.ctx, "test_model")
        assert "test_model" in sql
        assert "WITH" in sql

    def test_schema_yml(self):
        yml = self.gen.generate_schema_yml(self.ctx, "test_model")
        assert "version: 2" in yml
        assert "id" in yml

    def test_sql(self):
        sql = self.gen.generate_sql(self.ctx)
        assert "WITH" in sql

    def test_dag(self):
        dag = self.gen.generate_dag(self.ctx, "test_model")
        assert "DAG" in dag

    def test_write_artifacts(self, tmp_path):
        arts = self.gen.write_artifacts(self.ctx, "m", output_dir=str(tmp_path), framework="dbt")
        assert Path(arts["model_sql"]).exists()
        assert Path(arts["schema_yml"]).exists()


class TestInferTests:
    def test_id(self):
        class F:
            field_path = "order_id"
        assert "not_null" in _infer_tests(F())

    def test_email(self):
        class F:
            field_path = "email"
        assert "unique" in _infer_tests(F())

    def test_plain(self):
        class F:
            field_path = "amount"
        assert _infer_tests(F()) == []
