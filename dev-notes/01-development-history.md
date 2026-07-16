# AutoPipeline — Development History

## Hackathon Entry

**Competition:** Build with DataHub: The Agent Hackathon (Devpost)
**Category:** Metadata-Aware Code Generation & Development
**Deadline:** Aug 10, 2026 @ 5pm EDT
**Prize:** $20,500 total, $3,000 per category winner

---

## Phase 0 — Research & Setup

### What we discovered
- DataHub Agent Context Kit has 22 pre-built tools for LangChain agents (10 mutations)
- Sample datasets loaded: showcase-ecommerce (1,307 entities) + bootstrap (105)
- `search.get_urns()` returns generators — call `list()` on it
- Lineage returns mixed types — must filter for `:dataset:` only
- SDK entities have `.schema` (list of SchemaField) with `.field_path`, `.native_type`, `.description`
- Mutations need extra deps: `sqlparse`, `sqlglot`, `patchy`

### Environment
- DataHub GMS at `http://172.17.0.1:8080` (Docker on host)
- Python 3.11 in Docker container
- GitHub: `github.com/muhammadzakriarasool/autopipeline` (public, Apache 2.0)

---

## Phase 1 — Context Layer

Built `context.py`, `composer.py`, `writer.py`:
- `ContextCollector` reads schemas, lineage, ownership, tags, glossary terms
- `PipelineContext` aggregates metadata from target + upstreams + downstreams
- `DataHubWriter` writes tags, descriptions, and lineage back

### Problems solved
1. Lineage returned `schemaField` URNs mixed with dataset URNs — filter with `:dataset:`
2. SDK entities return raw Python class instances for owners/tags — added `clean_owner()`, `clean_tag()`
3. Jinja2 template used non-existent `regex_replace` filter — simplified
4. `add_lineage()` failed with missing deps — added to requirements

---

## Phase 2 — Code Generator

Built `generator.py` with 4 Jinja2 templates:
- `dbt_model.sql.j2` — dbt SQL models with CTEs, source() refs, type casting
- `dbt_schema.yml.j2` — column documentation + inferred tests
- `sql_transform.sql.j2` — plain SQL transformations
- `airflow_dag.py.j2` — Airflow DAG skeletons

### Verified output
- `order_details` (55 columns, 11 upstreams) -> 20KB dbt model SQL
- `promotion_analysis` (6 columns) -> 1KB dbt model
- `customer_orders` (22 columns) -> 1.7KB SQL transform

---

## Phase 3 — Agent Orchestrator

Built `agent.py` with LangChain:
- Uses `build_langchain_tools(client, include_mutations=True)` for all 22 DataHub tools
- OpenRouter `openrouter/free` model (zero cost)
- Agent explores DataHub -> generates code -> falls back to templates if LLM fails

---

## Phase 4 — DataHub Skill

Created `datahub-pipeline-generate` skill for datahub-skills repo:
- SKILL.md with YAML frontmatter + comprehensive markdown body
- PR created at `github.com/muhammadzakriarasool/datahub-skills/pull/1`

---

## Pivot to Idea 3 — AutoPilot

After completing Phases 1-4, we realized pipeline generation was too straightforward for a hackathon win. Research showed:

1. 758 participants, all with access to the same AI tools
2. "Read metadata -> generate code" is table stakes
3. Judges want "beyond what DataHub ships OOTB"
4. Pipeline write-back is obvious — every entrant will do it

### What we chose: AutoPilot — Self-Healing Data Pipeline Agent

An agent that monitors DataHub quality assertions and freshness checks, detects problems, diagnoses root cause via lineage traversal, generates fixes, and documents everything through DataHub mutations.

### Why this wins
- Self-healing pipelines are the #1 data engineering trend in 2026
- Nobody has built one that uses DataHub metadata
- Uses ALL 22 DataHub tools (read + write)
- Healthcare dataset has planted quality issues — perfect demo
- Closed loop: detect -> diagnose -> fix -> validate -> document
