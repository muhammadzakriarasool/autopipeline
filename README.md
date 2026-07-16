# AutoPipeline

Context-Aware Data Pipeline Generator — AI agents that read DataHub metadata to generate production-ready pipeline code and write back to the graph.

## Architecture

```
User Request → Agent → DataHub SDK (read context)
                     → LLM (generate with real metadata)
                     → Pipeline Artifacts (dbt, SQL, DAGs)
                     → DataHub SDK (write back docs/tags/lineage)
```

## Quickstart

1. Set up DataHub connection:
   ```
   export DATAHUB_SERVER=https://your-tenant.acryl.io
   export DATAHUB_TOKEN=your-token
   ```

2. Verify connectivity:
   ```
   autopipeline verify
   ```

3. Generate a pipeline:
   ```
   autopipeline generate --query "Create a daily revenue report pipeline" --framework dbt
   ```

## Hackathon Submission

Built for [Build with DataHub: The Agent Hackathon](https://datahub.devpost.com/)
