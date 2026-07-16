"""DataHub context collector — retrieves schemas, lineage, ownership, tags, terms."""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

from datahub.sdk.main_client import DataHubClient


@dataclass
class SchemaFieldInfo:
    """A single schema field with its metadata."""
    field_path: str
    native_type: str
    description: str = ""
    nullable: bool = True
    tags: list[str] = field(default_factory=list)
    terms: list[str] = field(default_factory=list)


@dataclass
class DatasetContext:
    """Full context for a single dataset."""
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
    field_lineage: list[dict] = field(default_factory=list)


@dataclass
class PipelineContext:
    """Aggregated context from multiple datasets for pipeline generation."""
    target_dataset: DatasetContext
    upstream_datasets: list[DatasetContext] = field(default_factory=list)
    downstream_datasets: list[DatasetContext] = field(default_factory=list)
    all_datasets: list[DatasetContext] = field(default_factory=list)
    glossary_terms: list[dict] = field(default_factory=list)
    tags: list[dict] = field(default_factory=list)
    fetched_at: str = ""


class ContextCollector:
    """Collects metadata context from DataHub for pipeline generation."""

    def __init__(self, client: DataHubClient):
        self.client = client

    def get_dataset_context(self, urn: str, hops: int = 1) -> Optional[DatasetContext]:
        """Get full context for a single dataset URN."""
        try:
            entity = self.client.entities.get(str(urn))
        except Exception as e:
            print(f"Error fetching entity {urn}: {e}")
            return None

        # Schema fields
        fields = []
        try:
            for sf in entity.schema:
                fields.append(SchemaFieldInfo(
                    field_path=sf.field_path,
                    native_type=sf.native_type or "UNKNOWN",
                    description=sf.description or "",
                    tags=[str(t) for t in (sf.tags or [])],
                    terms=[str(t) for t in (sf.terms or [])] if sf.terms else [],
                ))
        except Exception as e:
            print(f"Warning: could not get schema for {urn}: {e}")

        # Owners
        owners = []
        try:
            for o in (entity.owners or []):
                owner_str = str(o).strip()
                if owner_str:
                    owners.append(owner_str)
        except Exception:
            pass

        # Tags
        tags = []
        try:
            for t in (entity.tags or []):
                tag_str = str(t).strip()
                if tag_str:
                    tags.append(tag_str)
        except Exception:
            pass

        # Glossary terms
        terms = []
        try:
            for gt in (entity.terms or []):
                term_str = str(gt).strip()
                if term_str:
                    terms.append(term_str)
        except Exception:
            pass

        # Platform
        platform = ""
        try:
            platform = str(entity.platform)
        except Exception:
            pass

        # Domain
        domain = ""
        try:
            domain = str(entity.domain) if entity.domain else ""
        except Exception:
            pass

        # Upstream lineage (table-level)
        upstreams = []
        downstreams = []
        field_lineage = []
        try:
            up = self.client.lineage.get_lineage(
                source_urn=urn, direction="upstream", max_hops=hops
            )
            for r in up:
                upstreams.append(str(r.urn))

            down = self.client.lineage.get_lineage(
                source_urn=urn, direction="downstream", max_hops=hops
            )
            for r in down:
                downstreams.append(str(r.urn))
        except Exception as e:
            print(f"Warning: lineage fetch failed for {urn}: {e}")

        return DatasetContext(
            urn=str(urn),
            name=entity.display_name or "",
            description=entity.description or "",
            platform=platform,
            schema_fields=fields,
            upstreams=upstreams,
            downstreams=downstreams,
            owners=owners,
            tags=tags,
            glossary_terms=terms,
            domain=domain,
            field_lineage=field_lineage,
        )

    def resolve_dataset(self, query: str) -> list[DatasetContext]:
        """Search for datasets by name and return their full context."""
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

    def build_pipeline_context(
        self, target_urn: str, hops: int = 2
    ) -> Optional[PipelineContext]:
        """Build a complete pipeline context around a target dataset.

        1. Get the target dataset's full context.
        2. Walk upstream lineage to get source datasets.
        3. Walk downstream lineage to get consumer datasets.
        """
        target = self.get_dataset_context(target_urn, hops=hops)
        if not target:
            return None

        ups = []
        for u in target.upstreams:
            ctx = self.get_dataset_context(u, hops=1)
            if ctx:
                ups.append(ctx)

        downs = []
        for d in target.downstreams:
            ctx = self.get_dataset_context(d, hops=1)
            if ctx:
                downs.append(ctx)

        all_ds = [target] + ups + downs

        return PipelineContext(
            target_dataset=target,
            upstream_datasets=ups,
            downstream_datasets=downs,
            all_datasets=all_ds,
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )


def extract_platform_from_urn(urn: str) -> str:
    """Extract platform name from a dataset URN."""
    if "(urn:li:dataPlatform:" in urn:
        start = urn.index("(urn:li:dataPlatform:") + len("(urn:li:dataPlatform:")
        end = urn.index(",", start)
        return urn[start:end]
    return "unknown"


def short_name(urn: str) -> str:
    """Extract a short human-readable name from a URN."""
    if ":dataset:(" in urn:
        parts = urn.split(",")
        if len(parts) >= 2:
            name = parts[1] if len(parts) > 2 else parts[0].split(":")[-1]
            if name.startswith("b2fd91."):
                name = name[7:]
            return name
    return urn.split(":")[-1]
