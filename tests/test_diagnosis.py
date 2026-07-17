"""Tests for AutoPilot RCA engine."""
from autopipeline.detector import IssueRecord
from autopipeline.diagnosis import (
    DiagnosisRecord,
    SchemaComparator,
    LineageTraverser,
    RcaDatabase,
    ContextBuilder,
)


class TestDiagnosisRecord:
    def test_create_minimal(self):
        rec = DiagnosisRecord(
            issue_id="abc",
            root_cause_dataset="urn:test",
            root_cause_type="schema_change",
        )
        assert rec.issue_id == "abc"
        assert rec.confidence == 0.0
        assert rec.suggested_fix_type == "none"
        assert rec.id  # auto-generated

    def test_create_full(self):
        rec = DiagnosisRecord(
            issue_id="abc",
            root_cause_dataset="urn:test",
            root_cause_type="stale_upstream",
            evidence=[{"type": "schema_diff", "added": ["col1"]}],
            diagnosis_text="Upstream table missing column",
            confidence=0.85,
            suggested_fix_type="dbt_model_patch",
            upstream_chain=["urn:a", "urn:b", "urn:test"],
        )
        assert rec.confidence == 0.85
        assert len(rec.upstream_chain) == 3


class TestSchemaComparator:
    def test_added_fields(self):
        upstream = ["id", "name", "email"]
        downstream = ["id", "name"]
        result = SchemaComparator.compare(upstream, downstream)
        assert result is not None
        assert "email" in result["added"]

    def test_removed_fields(self):
        upstream = ["id"]
        downstream = ["id", "name", "email"]
        result = SchemaComparator.compare(upstream, downstream)
        assert result is not None
        assert "email" in result["removed"]

    def test_type_changes(self):
        upstream_fields = [{"field_path": "id", "native_type": "TEXT"}]
        downstream_fields = [{"field_path": "id", "native_type": "NUMBER"}]
        result = SchemaComparator.compare_with_types(upstream_fields, downstream_fields)
        assert result is not None
        assert "id" in result["type_changes"]

    def test_no_diff(self):
        result = SchemaComparator.compare(["id", "name"], ["id", "name"])
        assert result is None

    def test_no_type_change(self):
        fields = [{"field_path": "id", "native_type": "TEXT"}]
        result = SchemaComparator.compare_with_types(fields, fields)
        assert result is None


class TestLineageTraverser:
    def test_single_hop(self):
        lineage_map = {
            "urn:c": ["urn:b"],
            "urn:b": ["urn:a"],
            "urn:a": [],
        }
        traverser = LineageTraverser(max_hops=3)
        chain, root = traverser.find_root("urn:c", lineage_map)
        assert root == "urn:a"
        assert "urn:c" in chain
        assert "urn:a" in chain

    def test_cycle_detection(self):
        lineage_map = {
            "urn:a": ["urn:b"],
            "urn:b": ["urn:a"],
        }
        traverser = LineageTraverser(max_hops=3)
        chain, root = traverser.find_root("urn:a", lineage_map)
        assert root == "urn:b"
        assert len(chain) == 2

    def test_max_hops_limit(self):
        lineage_map = {
            "urn:d": ["urn:c"],
            "urn:c": ["urn:b"],
            "urn:b": ["urn:a"],
            "urn:a": [],
        }
        traverser = LineageTraverser(max_hops=1)
        chain, root = traverser.find_root("urn:d", lineage_map)
        assert root == "urn:c"
        assert len(chain) == 2

    def test_no_upstream(self):
        traverser = LineageTraverser(max_hops=3)
        chain, root = traverser.find_root("urn:leaf", {"urn:leaf": []})
        assert root == "urn:leaf"
        assert chain == ["urn:leaf"]


class TestRcaDatabase:
    def test_store_and_find(self):
        db = RcaDatabase()
        rec = DiagnosisRecord(
            issue_id="1",
            root_cause_dataset="urn:x",
            root_cause_type="schema_change",
        )
        db.store(rec)
        found = db.find_similar("schema_change")
        assert found is not None
        assert found.root_cause_type == "schema_change"

    def test_find_unknown(self):
        db = RcaDatabase()
        assert db.find_similar("nonexistent") is None

    def test_stores_multiple(self):
        db = RcaDatabase()
        db.store(DiagnosisRecord(issue_id="1", root_cause_dataset="a", root_cause_type="freshness"))
        db.store(DiagnosisRecord(issue_id="2", root_cause_dataset="b", root_cause_type="volume"))
        assert db.find_similar("freshness") is not None
        assert db.find_similar("volume") is not None


class TestContextBuilder:
    def test_build_evidence(self):
        issue = IssueRecord(
            dataset_urn="urn:test",
            issue_type="schema",
            severity="critical",
            description="Schema drift detected",
        )
        metadata = {
            "schema_fields": [
                {"field_path": "id", "native_type": "NUMBER"},
                {"field_path": "name", "native_type": "TEXT"},
            ],
            "upstreams": ["urn:up1", "urn:up2"],
            "owners": ["user@test.com"],
            "tags": ["PII"],
        }
        evidence = ContextBuilder.build_evidence(issue, metadata)
        assert evidence["dataset_urn"] == "urn:test"
        assert evidence["issue_type"] == "schema"
        assert len(evidence["schema_fields"]) == 2
        assert len(evidence["upstreams"]) == 2
