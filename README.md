# AutoPipeline

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![DataHub](https://img.shields.io/badge/DataHub-1.6.0%2B-orange)](https://github.com/datahub-project/datahub)

AI agents that read DataHub metadata to generate production-ready pipeline code — and write back to the graph.

Built for the **Build with DataHub: The Agent Hackathon** — *Metadata-Aware Code Generation & Development* category.

---

## Architecture

```
User Request
    |
    v
AutoPipeline CLI
    |
    +-- ContextCollector --> DataHub (schemas, lineage, ownership, tags)
    +-- ContextComposer  --> Structured LLM prompt
    +-- PipelineGenerator --> Jinja2 templates (dbt, SQL, DAGs)
    +-- LangChain Agent   --> DataHub tools (explore + generate + write-back)
    +-- DataHubWriter     --> Tags, descriptions, lineage (write-back to graph)
```

---

## Quickstart

```bash
git clone https://github.com/muhammadzakriarasool/autopipeline.git
cd autopipeline
pip install -e .
```

Configure `.env` with your DataHub connection and OpenRouter key (free tier):

```
DATAHUB_SERVER=http://172.17.0.1:8080
DATAHUB_TOKEN=your-token
OPENROUTER_API_KEY=sk-or-v1-...
```

---

## Commands

| Command | Description |
|---------|-------------|
| `autopipeline verify` | Test DataHub connectivity |
| `autopipeline search -q "query"` | Search datasets in DataHub |
| `autopipeline inspect <urn>` | Full metadata context for a dataset |
| `autopipeline generate -q "prompt" [-t urn] [-f dbt] [--dry-run]` | Generate pipeline code |
| `autopipeline tag --urn <urn>` | Tag a dataset (write-back test) |

---

## Generated Artifacts

| Example | Framework | Output |
|---------|-----------|--------|
| [order_details_revenue](examples/order_details_revenue/) | dbt | 55-column model + schema.yml |
| [promotion_analysis](examples/promotion_analysis/) | dbt | 6-column model + schema.yml |
| [customer_orders](examples/customer_orders/) | SQL | 22-column transform |
| [order_inventory_dag](examples/order_inventory_dag/) | Airflow | DAG skeleton |

---

## Write-Back to DataHub

Every generated artifact enriches the DataHub catalog:

- **Tags** — marks datasets with `AutoPipeline`
- **Descriptions** — appends generation metadata
- **Lineage** — records upstream source to generated model

---

## Project Structure

```
autopipeline/
  .env                    # Configuration (gitignored)
  pyproject.toml          # Package config (Apache 2.0)
  LICENSE                 # Apache 2.0
  README.md               # This file
  dev-notes/              # Development history + Idea 3 plan
  examples/               # Generated pipeline artifacts
  src/autopipeline/
    __init__.py
    cli.py                # CLI (5 commands)
    config.py             # Environment variables
    context.py            # Metadata collector + dataclasses
    composer.py           # LLM prompt assembly
    writer.py             # DataHub write-back mutations
    generator.py          # Jinja2 template rendering
    llm.py                # OpenAI-compatible LLM client
    agent.py              # LangChain agent with DataHub tools
    templates/            # Jinja2 pipeline templates
  tests/                  # Unit tests
```

---

## Tests

```bash
python3 -m pytest tests/ -v
```

---

## License

[Apache 2.0](LICENSE)

---

*Built for the Build with DataHub Agent Hackathon — Deadline Aug 10, 2026*
