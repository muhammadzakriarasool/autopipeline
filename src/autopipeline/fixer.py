"""AutoPilot fix generator — produces patches from diagnosis records."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from autopipeline.diagnosis import DiagnosisRecord


@dataclass
class FixRecord:
    diagnosis_id: str
    fix_type: str
    fix_description: str = ""
    code_patches: dict[str, str] = field(default_factory=dict)
    requires_approval: bool = True
    approved: Optional[bool] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))


_FIX_TYPE_MAP = {
    "schema_change": "dbt_model_patch",
    "stale_upstream": "assertion_update",
    "broken_pipeline": "dag_update",
    "null_spike": "dbt_model_patch",
    "volume_anomaly": "doc_fix",
}

_AUTO_APPROVE_TYPES = {"doc_fix", "assertion_update"}


class FixPlanner:
    """Maps diagnosis root cause to fix type and creates FixRecord."""

    @staticmethod
    def plan(diagnosis: DiagnosisRecord) -> FixRecord:
        fix_type = diagnosis.suggested_fix_type
        if fix_type == "none" or fix_type not in {
            "dbt_model_patch", "sql_patch", "dag_update",
            "assertion_update", "doc_fix",
        }:
            fix_type = _FIX_TYPE_MAP.get(diagnosis.root_cause_type, "doc_fix")
        description = (
            f"Fix for {diagnosis.root_cause_type} on {diagnosis.root_cause_dataset}: "
            f"{diagnosis.diagnosis_text}"
        )
        return FixRecord(
            diagnosis_id=diagnosis.id,
            fix_type=fix_type,
            fix_description=description,
            requires_approval=True,
        )


class CodeGenerator:
    """Generates code patches from FixRecord and metadata."""

    @staticmethod
    def generate_patches(diagnosis: DiagnosisRecord, metadata: dict) -> dict[str, str]:
        patches: dict[str, str] = {}
        if diagnosis.suggested_fix_type == "doc_fix" or diagnosis.root_cause_type == "unknown":
            patches["description.md"] = (
                "# AutoPilot Incident Report\n\n"
                + "**Dataset:** " + diagnosis.root_cause_dataset + "\n"
                + "**Issue:** " + diagnosis.root_cause_type + "\n"
                + "**Diagnosis:** " + diagnosis.diagnosis_text + "\n\n"
                + "## Evidence\n\n" + str(diagnosis.evidence) + "\n"
            )
            return patches
        if "schema" in diagnosis.root_cause_type:
            fields = metadata.get("schema_fields", [])
            col_parts = []
            for f in fields:
                fname = f.get("field_path", "col")
                col_parts.append(f"COALESCE({fname}, '') AS {fname}")
            col_list = ",\n    ".join(col_parts)
            patches["model_patch.sql"] = (
                "-- AutoPilot schema fix for " + diagnosis.root_cause_dataset + "\n"
                + "SELECT\n    " + col_list + "\nFROM {{ ref('source_model') }}\n"
            )
        return patches


class ApprovalGate:
    """Controls whether fixes require human approval."""

    def __init__(self, mode: str = "shadow"):
        self.mode = mode

    def requires_approval(self, fix: FixRecord) -> bool:
        if self.mode == "shadow":
            return True
        return fix.fix_type not in _AUTO_APPROVE_TYPES

    def approve(self, fix: FixRecord, approved: bool = True) -> None:
        fix.approved = approved
