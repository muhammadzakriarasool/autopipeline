"""Tests for AutoPilot fix generation engine."""
from datetime import datetime, timezone

from autopipeline.diagnosis import DiagnosisRecord
from autopipeline.fixer import (
    FixRecord,
    FixPlanner,
    CodeGenerator,
    ApprovalGate,
)


def _make_diagnosis(fix_type: str = "dbt_model_patch") -> DiagnosisRecord:
    return DiagnosisRecord(
        issue_id="issue-1",
        root_cause_dataset="urn:li:dataset:(urn:li:dataPlatform:dbt,test.model,PROD)",
        root_cause_type="schema_change",
        evidence=[{"added": ["email"], "removed": []}],
        diagnosis_text="Upstream added column email",
        confidence=0.85,
        suggested_fix_type=fix_type,
        upstream_chain=["urn:li:dataset:(urn:li:dataPlatform:dbt,src,PROD)"],
    )


class TestFixRecord:
    def test_create_minimal(self):
        rec = FixRecord(diagnosis_id="d1", fix_type="doc_fix")
        assert rec.diagnosis_id == "d1"
        assert rec.fix_type == "doc_fix"
        assert rec.requires_approval is True
        assert rec.approved is None
        assert rec.id

    def test_create_with_patches(self):
        rec = FixRecord(
            diagnosis_id="d1",
            fix_type="dbt_model_patch",
            code_patches={"model.sql": "SELECT 1"},
        )
        assert "model.sql" in rec.code_patches


class TestFixPlanner:
    def test_schema_change_to_dbt_patch(self):
        diag = _make_diagnosis("dbt_model_patch")
        plan = FixPlanner.plan(diag)
        assert plan.fix_type == "dbt_model_patch"
        assert plan.requires_approval is True

    def test_freshness_to_assertion_update(self):
        diag = DiagnosisRecord(
            issue_id="i2",
            root_cause_dataset="urn:test",
            root_cause_type="stale_upstream",
            suggested_fix_type="assertion_update",
        )
        plan = FixPlanner.plan(diag)
        assert plan.fix_type == "assertion_update"

    def test_unknown_to_doc_fix(self):
        diag = DiagnosisRecord(
            issue_id="i3",
            root_cause_dataset="urn:test",
            root_cause_type="unknown",
            suggested_fix_type="none",
        )
        plan = FixPlanner.plan(diag)
        assert plan.fix_type == "doc_fix"

    def test_plan_has_description(self):
        diag = _make_diagnosis()
        plan = FixPlanner.plan(diag)
        assert len(plan.fix_description) > 0


class TestCodeGenerator:
    def test_generates_sql_for_schema_change(self):
        diag = _make_diagnosis()
        patches = CodeGenerator.generate_patches(
            diag, {"schema_fields": [{"field_path": "id", "native_type": "NUMBER"}]}
        )
        assert isinstance(patches, dict)

    def test_generates_description_for_doc_fix(self):
        diag = DiagnosisRecord(
            issue_id="i",
            root_cause_dataset="urn:test",
            root_cause_type="unknown",
            suggested_fix_type="doc_fix",
            diagnosis_text="Needs documentation",
        )
        patches = CodeGenerator.generate_patches(diag, {})
        assert "description.md" in patches
        assert "Needs documentation" in patches["description.md"]


class TestApprovalGate:
    def test_shadow_always_requires_approval(self):
        gate = ApprovalGate(mode="shadow")
        fix = FixRecord(diagnosis_id="d", fix_type="doc_fix")
        assert gate.requires_approval(fix) is True

    def test_autonomous_auto_approves_doc_fix(self):
        gate = ApprovalGate(mode="autonomous")
        fix = FixRecord(diagnosis_id="d", fix_type="doc_fix")
        assert gate.requires_approval(fix) is False

    def test_autonomous_requires_approval_for_dbt_patch(self):
        gate = ApprovalGate(mode="autonomous")
        fix = FixRecord(diagnosis_id="d", fix_type="dbt_model_patch")
        assert gate.requires_approval(fix) is True

    def test_autonomous_requires_approval_for_sql_patch(self):
        gate = ApprovalGate(mode="autonomous")
        fix = FixRecord(diagnosis_id="d", fix_type="sql_patch")
        assert gate.requires_approval(fix) is True

    def test_approve_fix(self):
        gate = ApprovalGate(mode="shadow")
        fix = FixRecord(diagnosis_id="d", fix_type="doc_fix")
        gate.approve(fix, approved=True)
        assert fix.approved is True

    def test_reject_fix(self):
        gate = ApprovalGate(mode="shadow")
        fix = FixRecord(diagnosis_id="d", fix_type="dbt_model_patch")
        gate.approve(fix, approved=False)
        assert fix.approved is False
