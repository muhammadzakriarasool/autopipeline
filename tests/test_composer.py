from autopipeline.context import DatasetContext, PipelineContext, SchemaFieldInfo
from autopipeline.composer import compose_schema_prompt, compose_pipeline_prompt


def test_schema_prompt_minimal():
    ds = DatasetContext(urn="u", name="test")
    prompt = compose_schema_prompt(ds)
    assert "Dataset: test" in prompt
    assert "Columns (0 total)" in prompt


def test_schema_prompt_with_schema():
    ds = DatasetContext(urn="u", name="t", schema_fields=[
        SchemaFieldInfo("id", "NUMBER", "Primary key"),
    ])
    prompt = compose_schema_prompt(ds)
    assert "id" in prompt
    assert "NUMBER" in prompt


def test_pipeline_prompt():
    target = DatasetContext(urn="t", name="daily_revenue")
    ctx = PipelineContext(target_dataset=target, fetched_at="2026-01-01")
    prompt = compose_pipeline_prompt(ctx, user_request="Show revenue", framework="dbt")
    assert "daily_revenue" in prompt
    assert "dbt" in prompt
    assert "Generation Rules" in prompt
