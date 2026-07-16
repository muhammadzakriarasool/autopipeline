"""AutoPipeline: Context-Aware Data Pipeline Generator.

Reads DataHub metadata (schemas, lineage, ownership, quality, glossary)
to generate production-ready pipeline code — dbt models, SQL transformations,
and Airflow/Dagster DAGs — that works on the first try.

It then writes back to the DataHub graph with tags, documentation,
and lineage so every generated artifact enriches the catalog.
"""

__version__ = "0.2.0"
__all__ = [
    "DataHubConnector",
    "ContextCollector",
    "DatasetContext",
    "PipelineContext",
    "DataHubWriter",
    "compose_schema_prompt",
    "compose_pipeline_prompt",
]

from autopipeline.connector import DataHubConnector
from autopipeline.context import ContextCollector, DatasetContext, PipelineContext
from autopipeline.writer import DataHubWriter
from autopipeline.context_composer import compose_schema_prompt, compose_pipeline_prompt
