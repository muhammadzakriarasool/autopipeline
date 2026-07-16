"""DataHub metadata context — dataclasses and collector for schemas, lineage, ownership."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from datahub.sdk.main_client import DataHubClient


@dataclass
class SchemaFieldInfo:
    field_path: str
    native_type: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    terms: list[str] = field(default_factory=list)


@dataclass
class DatasetContext:
    urn: str
    name: str
    description: str = ""
    platform: str = ""
    schema_fields: list[SchemaFieldInfo] = field(default_factory=list)
    upstreams: list[str] = field(default_factory=list)
    downstreams: list[str] = field(default_factory=list)
    owners: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    glossary_terms: list[str] = field(default_factory=list)
    domain: str = ""


@dataclass
class PipelineContext:
    target_dataset: DatasetContext
    upstream_datasets: list[DatasetContext] = field(default_factory=list)
    downstream_datasets: list[DatasetContext] = field(default_factory=list)
    all_datasets: list[DatasetContext] = field(default_factory=list)
    fetched_at: str = ""


def short_name(urn: str) -> str:
    if ":dataset:(" in urn:
        parts = urn.split(",")
        if len(parts) >= 2:
            name = parts[1] if len(parts) > 2 else parts[0].split(":")[-1]
            return name[7:] if name.startswith("b2fd91.") else name
    return urn.split(":")[-1]


def extract_platform(urn: str) -> str:
    if "(urn:li:dataPlatform:" in urn:
        start = urn.index("(urn:li:dataPlatform:") + len("(urn:li:dataPlatform:")
        end = urn.index(",", start)
        return urn[start:end]
    return "unknown"


def clean_owner(raw: str) -> str:
    m = re.search(r"(?:corpuser|corpGroup):([\w.@-]+)", str(raw))
    if m:
        name = m.group(1).strip()
        return name[7:] if name.startswith("b2fd91.") else name
    return str(raw).split(":")[-1]


def clean_tag(raw: str) -> str:
    m = re.search(r"tag:([^'\"\})\]]+)", str(raw))
    if m:
        name = m.group(1).strip()
        return name[7:] if name.startswith("b2fd91.") else name
    return str(raw).split(":")[-1]


def clean_term(raw: str) -> str:
    m = re.search(r"glossaryTerm:([\w.@-]+)", str(raw))
    if m:
        name = m.group(1).strip()
        return name[7:] if name.startswith("b2fd91.") else name
    return str(raw).split(":")[-1]


class ContextCollector:
    def __init__(self, client: DataHubClient):
        self.client = client

    def get_dataset_context(self, urn: str, hops: int = 1) -> Optional[DatasetContext]:
        try:
            entity = self.client.entities.get(str(urn))
        except Exception as e:
            print(f"Error fetching entity {urn}: {e}")
            return None

        fields = []
        try:
            for sf in entity.schema:
                fields.append(SchemaFieldInfo(
                    field_path=sf.field_path,
                    native_type=sf.native_type or "UNKNOWN",
                    description=sf.description or "",
                    tags=[str(t) for t in (sf.tags or [])],
                ))
        except Exception:
            pass

        owners = [str(o) for o in (entity.owners or []) if str(o).strip()]
        tags = [str(t) for t in (entity.tags or []) if str(t).strip()]
        terms = [str(t) for t in (entity.terms or []) if str(t).strip()]

        platform = str(entity.platform) if entity.platform else ""
        domain = str(entity.domain) if entity.domain else ""

        upstreams, downstreams = [], []
        try:
            up = self.client.lineage.get_lineage(source_urn=urn, direction="upstream", max_hops=hops)
            for r in up:
                u = str(r.urn)
                if ":dataset:" in u and u not in upstreams:
                    upstreams.append(u)

            down = self.client.lineage.get_lineage(source_urn=urn, direction="downstream", max_hops=hops)
            for r in down:
                d = str(r.urn)
                if ":dataset:" in d and d not in downstreams:
                    downstreams.append(d)
        except Exception:
            pass

        return DatasetContext(
            urn=str(urn), name=entity.display_name or "",
            description=entity.description or "", platform=platform,
            schema_fields=fields, upstreams=upstreams, downstreams=downstreams,
            owners=owners, tags=tags, glossary_terms=terms, domain=domain,
        )

    def resolve_dataset(self, query: str) -> list[DatasetContext]:
        results = []
        try:
            urns = list(self.client.search.get_urns(query))
            for urn in urns:
                s = str(urn)
                if ":dataset:" in s:
                    ctx = self.get_dataset_context(s)
                    if ctx:
                        results.append(ctx)
        except Exception as e:
            print(f"Search error: {e}")
        return results

    def build_pipeline_context(self, target_urn: str, hops: int = 2) -> Optional[PipelineContext]:
        target = self.get_dataset_context(target_urn, hops=hops)
        if not target:
            return None

        ups = [self.get_dataset_context(u, hops=1) for u in target.upstreams]
        ups = [c for c in ups if c]
        downs = [self.get_dataset_context(d, hops=1) for d in target.downstreams]
        downs = [c for c in downs if c]

        return PipelineContext(
            target_dataset=target, upstream_datasets=ups,
            downstream_datasets=downs, all_datasets=[target] + ups + downs,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
