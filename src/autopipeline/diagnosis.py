"""AutoPilot RCA engine — diagnoses root cause via lineage and schema analysis."""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional
from uuid import uuid4

from autopipeline.detector import IssueRecord

logger = logging.getLogger(__name__)


@dataclass
class DiagnosisRecord:
    issue_id: str
    root_cause_dataset: str
    root_cause_type: str = "unknown"
    evidence: list[dict] = field(default_factory=list)
    diagnosis_text: str = ""
    confidence: float = 0.0
    suggested_fix_type: str = "none"
    upstream_chain: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


class ContextBuilder:
    """Gathers metadata evidence for an issue from raw metadata dict."""

    @staticmethod
    def build_evidence(issue: IssueRecord, metadata: dict) -> dict:
        return {
            "dataset_urn": issue.dataset_urn,
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "description": issue.description,
            "schema_fields": metadata.get("schema_fields", []),
            "upstreams": metadata.get("upstreams", []),
            "owners": metadata.get("owners", []),
            "tags": metadata.get("tags", []),
        }


class SchemaComparator:
    """Compares schemas between two datasets."""

    @staticmethod
    def compare(
        upstream_fields: list[str], downstream_fields: list[str]
    ) -> Optional[dict]:
        upstream = set(upstream_fields)
        downstream = set(downstream_fields)
        added = upstream - downstream
        removed = downstream - upstream
        if not added and not removed:
            return None
        return {"added": sorted(added), "removed": sorted(removed)}

    @staticmethod
    def compare_with_types(
        upstream_fields: list[dict], downstream_fields: list[dict]
    ) -> Optional[dict]:
        up_map = {f["field_path"]: f.get("native_type") for f in upstream_fields}
        down_map = {f["field_path"]: f.get("native_type") for f in downstream_fields}
        added = sorted(set(up_map) - set(down_map))
        removed = sorted(set(down_map) - set(up_map))
        type_changes = {}
        for field_path in set(up_map) & set(down_map):
            if up_map[field_path] != down_map[field_path]:
                type_changes[field_path] = (down_map[field_path], up_map[field_path])
        if not added and not removed and not type_changes:
            return None
        return {"added": added, "removed": removed, "type_changes": type_changes}


class LineageTraverser:
    """BFS traversal upstream through lineage graph with cycle detection."""

    def __init__(self, max_hops: int = 3):
        self.max_hops = max_hops

    def find_root(
        self, target_urn: str, lineage_map: dict[str, list[str]]
    ) -> tuple[list[str], str]:
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(target_urn, 0)])
        chain: list[str] = []

        while queue:
            urn, depth = queue.popleft()
            if urn in visited or depth > self.max_hops:
                continue
            visited.add(urn)
            chain.append(urn)

            upstreams = lineage_map.get(urn, [])
            if not upstreams:
                return (chain, urn)

            for u in upstreams:
                if u not in visited and depth + 1 <= self.max_hops:
                    queue.append((u, depth + 1))

        return (chain, chain[-1] if chain else target_urn)


class RcaDatabase:
    """In-memory cache of historical diagnoses by root cause type."""

    def __init__(self):
        self._history: list[DiagnosisRecord] = []

    def store(self, diagnosis: DiagnosisRecord) -> None:
        self._history.append(diagnosis)

    def find_similar(self, root_cause_type: str) -> Optional[DiagnosisRecord]:
        for rec in reversed(self._history):
            if rec.root_cause_type == root_cause_type:
                return rec
        return None
