from autopipeline.context import SchemaFieldInfo, DatasetContext, PipelineContext, short_name, extract_platform, clean_owner, clean_tag, clean_term


class TestHelpers:
    def test_short_name_dbt(self):
        assert short_name("urn:li:dataset:(urn:li:dataPlatform:dbt,db.table,PROD)") == "db.table"

    def test_short_name_clean(self):
        assert short_name("urn:li:dataset:(urn:li:dataPlatform:snowflake,db.table,PROD)") == "db.table"

    def test_extract_platform(self):
        assert extract_platform("urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)") == "dbt"
        assert extract_platform("urn:li:corpuser:u1") == "unknown"

    def test_clean_owner(self):
        assert "jane@example.com" in clean_owner("urn:li:corpuser:b2fd91.jane@example.com")
        assert "ORG_DATA" in clean_owner("urn:li:corpGroup:b2fd91.ORG_DATA_PLATFORM")

    def test_clean_tag(self):
        assert clean_tag("urn:li:tag:b2fd91.PII_Data") == "PII_Data"

    def test_clean_term(self):
        assert clean_term("urn:li:glossaryTerm:b2fd91.some-uuid") == "some-uuid"


class TestDataclasses:
    def test_schema_field(self):
        f = SchemaFieldInfo("id", "NUMBER", "Primary key")
        assert f.field_path == "id"
        assert f.native_type == "NUMBER"

    def test_dataset_context_minimal(self):
        ds = DatasetContext(urn="u", name="test")
        assert ds.name == "test"
        assert ds.schema_fields == []

    def test_pipeline_context(self):
        target = DatasetContext(urn="t", name="target")
        ctx = PipelineContext(target_dataset=target, fetched_at="2026-01-01")
        assert ctx.target_dataset.name == "target"
        assert ctx.all_datasets == []
