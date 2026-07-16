"""Context composer — builds structured LLM prompts from DataHub metadata."""

from autopipeline.context import DatasetContext, PipelineContext, short_name


def compose_schema_prompt(dataset: DatasetContext) -> str:
    lines = [f"## Dataset: {dataset.name}", f"URN: {dataset.urn}"]
    if dataset.description:
        lines.append(f"Description: {dataset.description[:500]}")
    if dataset.platform:
        lines.append(f"Platform: {short_name(dataset.platform)}")
    if dataset.owners:
        lines.append(f"Owners: {', '.join(clean_owner_simple(o) for o in dataset.owners)}")
    if dataset.tags:
        lines.append(f"Tags: {', '.join(short_name(t) for t in dataset.tags)}")
    if dataset.glossary_terms:
        lines.append(f"Terms: {', '.join(short_name(t) for t in dataset.glossary_terms)}")
    lines.append(f"\n### Columns ({len(dataset.schema_fields)} total)")
    lines.append("| Column | Type | Description |")
    lines.append("|--------|------|-------------|")
    for f in dataset.schema_fields:
        desc = (f.description or "")[:80].replace("\n", " ")
        lines.append(f"| {f.field_path} | {f.native_type} | {desc} |")
    if dataset.upstreams:
        lines.append(f"\n#### Upstreams ({len(dataset.upstreams)})")
        for u in dataset.upstreams[:10]:
            lines.append(f"- {short_name(u)}")
    if dataset.downstreams:
        lines.append(f"\n#### Downstreams ({len(dataset.downstreams)})")
        for d in dataset.downstreams[:10]:
            lines.append(f"- {short_name(d)}")
    return "\n".join(lines)


def compose_pipeline_prompt(ctx: PipelineContext, user_request: str = "", framework: str = "dbt") -> str:
    parts = [
        f"Framework: {framework}",
        f"Context fetched at: {ctx.fetched_at}",
        "",
    ]
    if user_request:
        parts.append(f"## User Request\n{user_request}\n")
    parts.append("## Target Dataset\n")
    parts.append(compose_schema_prompt(ctx.target_dataset))
    if ctx.upstream_datasets:
        parts.append(f"\n## Upstream Sources ({len(ctx.upstream_datasets)})\n")
        for ds in ctx.upstream_datasets:
            parts.append(compose_schema_prompt(ds))
    if ctx.downstream_datasets:
        parts.append(f"\n## Downstream Consumers ({len(ctx.downstream_datasets)})\n")
        for ds in ctx.downstream_datasets:
            parts.append(compose_schema_prompt(ds))
    target_name = short_name(ctx.target_dataset.urn)
    parts.append(f"""
## Generation Rules
Generate a {framework} pipeline based on the metadata above.
- Use CTEs (WITH clauses), not subqueries
- One CTE per source table
- Column-level descriptions from the schema
- Add dbt tests: not_null for IDs, unique for emails
- Handle NULL values explicitly
- Use source() references in dbt models
- Output model: models/{target_name}.sql""")
    return "\n".join(parts)


def clean_owner_simple(raw: str) -> str:
    import re
    m = re.search(r"(?:corpuser|corpGroup):([\w.@-]+)", str(raw))
    if m:
        name = m.group(1).strip()
        return name[7:] if name.startswith("b2fd91.") else name
    return str(raw).split(":")[-1]
