# AutoPipeline

**Context-Aware Data Pipeline Generator**

AI agents that read DataHub metadata (schemas, lineage, ownership, quality, glossary) to generate production-ready pipeline code — dbt models, SQL transformations, and Airflow/Dagster DAGs — that works on the first try. Then writes back to the DataHub graph with tags, documentation, and lineage so every generated artifact enriches the catalog.

Built for the **Build with DataHub: The Agent Hackathon** — Metadata-Aware Code Generation & Development category.

## Architecture

```
User Request -> AutoPipeline CLI -> DataHub SDK (read context)
                                    -> Context Composer (structured prompt)
                                    -> LLM (generate with real metadata)
                                    -> Pipeline Artifacts (dbt, SQL, DAGs)
                                    -> DataHub Writer (write back docs/tags/lineage)
```

## Current Status — Phase 1 Complete

| Phase | Status | What it includes |
|-------|--------|-----------------|
| 0 — Setup | Done | DataHub running, SDK installed, project scaffolded, connectivity verified |
| 1 — Context Layer | Done | ContextCollector, ContextComposer, DataHubWriter, CLI, 18 tests |
| 2 — Code Generation | In Progress | Jinja2 templates, LLM integration |
| 3 — Agent Orchestrator | Pending | LangChain agent, write-back, example artifacts |
| 4 — DataHub Skill | Pending | datahub-pipeline-generate skill + PR |
| 5 — Demo & Submission | Pending | Demo video, polished README, Devpost submission |

## Quickstart

```bash
# Set env vars
export DATAHUB_SERVER=http://172.17.0.1:8080
export DATAHUB_TOKEN=your-token

# Verify connectivity
autopipeline verify

# Search datasets
autopipeline search -q "order_details"

# Inspect a dataset's full metadata context
autopipeline inspect "urn:li:dataset:(urn:li:dataPlatform:dbt,...)"

# Generate a pipeline (dry-run to preview the prompt)
autopipeline generate -q "Daily revenue report" \
  --target "urn:li:dataset:(...)"

# Tag a dataset (write-back test)
autopipeline tag --urn "urn:li:dataset:(...)" --tag "urn:li:tag:AutoPipeline"
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `verify` | Test DataHub connectivity |
| `search -q <query>` | Search datasets in DataHub |
| `inspect <urn>` | Full metadata context (schema, lineage, owners, tags) |
| `generate -q <prompt> [--target] [--framework] [--dry-run]` | Generate pipeline code |
| `tag --urn <urn> [--tag]` | Add tag to dataset (write-back) |

## DataHub Instance

- **GMS**: `http://172.17.0.1:8080`
- **Frontend**: `http://localhost:9002` (login: `datahub` / `datahub`)
- **Sample data**: showcase-ecommerce (1,307 entities) + bootstrap loaded

## Development

```bash
git clone https://github.com/muhammadzakriarasool/autopipeline.git
cd autopipeline
pip install -e .
```

Run tests:
```bash
pytest tests/ -v
```

## License

Apache 2.0
