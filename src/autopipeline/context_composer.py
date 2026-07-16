"""Context composer — assembles DataHub metadata into structured LLM prompts."""

from autopipeline.context import (
    DatasetContext,
    PipelineContext,
    SchemaFieldInfo,
    short_name,
    extract_platform_from_urn,
)


def compose_schema_prompt(dataset: DatasetContext) -> str:
    """Build a formatted schema description for LLM consumption."""
    lines = [f"## Dataset: {dataset.name}", f"URN: {dataset.urn}"]

    if dataset.description:
        lines.append(f"Description: {dataset.description[:500]}")

    if dataset.platform:
        lines.append(f"Platform: {short_name(dataset.platform)}")

    if dataset.owners:
        owner_names = [short_name(o) for o in dataset.owners]
        lines.append(f"Owners: {', '.join(owner_names)}")

    if dataset.tags:
        tag_names = [short_name(t) for t in dataset.tags]
        lines.append(f"Tags: {', '.join(tag_names)}")

    if dataset.glossary_terms:
        term_names = [short_name(t) for t in dataset.glossary_terms]
        lines.append(f"Glossary Terms: {', '.join(term_names)}")

    # Schema columns
    lines.append(f"\n### Columns ({len(dataset.schema_fields)} total)")
    lines.append("| Column | Type | Description |")
    lines.append("|--------|------|-------------|")
    for f in dataset.schema_fields:
        desc = (f.description or "")[:80].replace("\n", " ")
        lines.append(f"| {f.field_path} | {f.native_type} | {desc} |")

    # Upstream lineage
    if dataset.upstreams:
        lines.append(f"\n#### Upstream Sources ({len(dataset.upstreams)})")
        for u in dataset.upstreams[:10]:
            lines.append(f"- {short_name(u)}")

    # Downstream consumers
    if dataset.downstreams:
        lines.append(f"\n#### Downstream Consumers ({len(dataset.downstreams)})")
        for d in dataset.downstreams[:10]:
            lines.append(f"- {short_name(d)}")

    return "\n".join(lines)


def compose_pipeline_prompt(
    ctx: PipelineContext,
    user_request: str = "",
    framework: str = "dbt",
) -> str:
    """Build a comprehensive LLM prompt for code generation.

    Assembles all collected context into a structured prompt that an LLM
    can use to generate pipeline code (dbt models, SQL, DAGs).
    """
    parts = []

    # System context
    parts.append(
        f"""You are AutoPipeline, a context-aware data pipeline generator.
You read DataHub metadata and generate production-ready pipeline code.
Framework: {framework}
Context fetched at: {ctx.fetched_at}
"""
    )

    # User request
    if user_request:
        parts.append(f"## User Request\n{user_request}\n")

    # Target dataset
    parts.append("## Target Dataset\n")
    parts.append(compose_schema_prompt(ctx.target_dataset))

    # Upstream source datasets
    if ctx.upstream_datasets:
        parts.append(
            f"\n## Upstream Source Datasets ({len(ctx.upstream_datasets)})\n"
        )
        for ds in ctx.upstream_datasets:
            parts.append(compose_schema_prompt(ds))

    # Downstream consumers
    if ctx.downstream_datasets:
        parts.append(
            f"\n## Downstream Consumers ({len(ctx.downstream_datasets)})\n"
        )
        for ds in ctx.downstream_datasets:
            parts.append(compose_schema_prompt(ds))

    # Global metadata summary
    parts.append("\n## Metadata Summary\n")
    all_tags = set()
    all_terms = set()
    for ds in ctx.all_datasets:
        all_tags.update(ds.tags)
        all_terms.update(ds.glossary_terms)

    if all_tags:
        parts.append(f"Tags across pipeline: {', '.join(short_name(t) for t in all_tags)}")
    if all_terms:
        parts.append(f"Glossary terms across pipeline: {', '.join(short_name(t) for t in all_terms)}")

    # Generation instructions
    parts.append(f"""
## Generation Instructions

Generate a {framework} pipeline based on the metadata above:

### dbt Model
- Create a SQL model that transforms data from upstream sources into the target schema.
- Use the exact column names and types from the schema.
- Include documentation, tests, and descriptions.
- Handle NULL values and type casting where needed.

### Output Files
1. `models/{short_name(ctx.target_dataset.urn)}.sql` — The model SQL
2. `models/schema.yml` — dbt schema documentation with column descriptions
3. An Airflow DAG to run the model (if framework=dag)

### Style Rules
- Use CTEs (WITH clauses), not subqueries.
- One CTE per source table.
- Column-level descriptions from the schema.
- Add appropriate tests (not_null, unique, relationships, accepted_values).
""")

    return "\n".join(parts)


def compose_writer_context(dataset: DatasetContext) -> str:
    """Build a concise context for write-back operations (tags, docs, ownership)."""
    lines = [f"Dataset: {dataset.name}", f"URN: {dataset.urn}"]

    if dataset.description:
        lines.append(f"Current description: {dataset.description[:300]}")

    if dataset.owners:
        lines.append(f"Current owners: {', '.join(short_name(o) for o in dataset.owners)}")

    if dataset.tags:
        lines.append(f"Current tags: {', '.join(short_name(t) for t in dataset.tags)}")

    if dataset.glossary_terms:
        lines.append(f"Current glossary terms: {', '.join(short_name(t) for t in dataset.glossary_terms)}")

    lines.append(f"Schema columns: {', '.join(f.field_path for f in dataset.schema_fields)}")

    return "\n".join(lines)
