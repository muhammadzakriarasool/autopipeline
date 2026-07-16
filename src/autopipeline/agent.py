"""LangChain agent orchestrator for DataHub metadata-aware pipeline generation.

Uses a LangChain agent with 22 pre-built DataHub tools to:
  1. Accept a natural language pipeline request.
  2. Explore DataHub metadata (search, schema, lineage, queries, tags, terms).
  3. Generate pipeline code artifacts (dbt models, SQL, DAGs).
  4. Write back to DataHub (tag generated models, add descriptions, record lineage).
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from datahub.sdk.main_client import DataHubClient
from datahub_agent_context.langchain_tools import build_langchain_tools

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from autopipeline.connector import DataHubConnector
from autopipeline.context import DatasetContext, PipelineContext
from autopipeline.generator import PipelineGenerator
from autopipeline.writer import DataHubWriter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class AgentConfig:
    """Configuration for the LangChain agent orchestrator."""

    datahub_server: str = "http://172.17.0.1:8080"
    datahub_token: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://openrouter.ai/api/v1"
    model: str = "openrouter/free"
    temperature: float = 0.0
    max_tokens: int = 8000
    request_timeout: int = 120
    agent_max_iterations: int = 30
    agent_max_execution_time: int = 300  # seconds
    output_dir: str = "output"
    generate_framework: str = "dbt"  # dbt | sql | dag
    default_tag_urn: str = "urn:li:tag:AutoPipeline"
    verbose: bool = False

    @classmethod
    def from_env(cls, **overrides: Any) -> "AgentConfig":
        """Build config from environment variables, merged with overrides."""
        return cls(
            datahub_server=os.environ.get(
                "DATAHUB_SERVER",
                os.environ.get("DATAHUB_GMS_URL", "http://172.17.0.1:8080"),
            ),
            datahub_token=os.environ.get("DATAHUB_TOKEN", ""),
            openai_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            openai_base_url=os.environ.get(
                "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            model=os.environ.get("OPENAI_MODEL", "openrouter/free"),
            output_dir=os.environ.get("AUTOPIPELINE_OUTPUT_DIR", "output"),
            generate_framework=os.environ.get(
                "AUTOPIPELINE_FRAMEWORK", "dbt"
            ),
            verbose=bool(os.environ.get("AUTOPIPELINE_VERBOSE", "")),
            **overrides,
        )


# ---------------------------------------------------------------------------
# Tool wrapper helpers for custom mutation tools not in build_langchain_tools
# ---------------------------------------------------------------------------


def _make_tag_dataset_tool(connector: DataHubConnector):
    """Create a direct tag-dataset tool using the existing connector."""
    from langchain_core.tools import tool

    @tool
    def tag_dataset(dataset_urn: str, tag_urn: str = "urn:li:tag:AutoPipeline") -> str:
        """Add a tag to a dataset in DataHub.

        Args:
            dataset_urn: The full URN of the dataset to tag.
            tag_urn: The tag URN to add (default: AutoPipeline).
        """
        ok = connector.writer.add_tag_to_dataset(dataset_urn, tag_urn)
        if ok:
            return f"Successfully added tag `{tag_urn}` to `{dataset_urn}`."
        return f"Failed to add tag `{tag_urn}` to `{dataset_urn}`."

    return tag_dataset


def _make_set_description_tool(connector: DataHubConnector):
    """Create a direct set-description tool."""
    from langchain_core.tools import tool

    @tool
    def set_dataset_description(dataset_urn: str, description: str) -> str:
        """Update the description / documentation of a dataset in DataHub.

        Args:
            dataset_urn: The full URN of the dataset.
            description: The new description text.
        """
        ok = connector.writer.set_description(dataset_urn, description)
        if ok:
            return f"Description updated for `{dataset_urn}`."
        return f"Failed to update description for `{dataset_urn}`."

    return set_dataset_description


def _make_add_lineage_tool(connector: DataHubConnector):
    """Create a direct add-lineage tool."""
    from langchain_core.tools import tool

    @tool
    def add_dataset_lineage(
        upstream_urn: str,
        downstream_urn: str,
        transformation_text: Optional[str] = None,
    ) -> str:
        """Record lineage between two datasets in DataHub.

        Args:
            upstream_urn: The source (upstream) dataset URN.
            downstream_urn: The target (downstream) dataset URN.
            transformation_text: Optional description of the transformation.
        """
        ok = connector.writer.add_lineage(
            upstream_urn, downstream_urn, transformation_text
        )
        if ok:
            return (
                f"Lineage added: `{upstream_urn}` -> `{downstream_urn}`."
            )
        return f"Failed to add lineage: `{upstream_urn}` -> `{downstream_urn}`."

    return add_dataset_lineage


# ---------------------------------------------------------------------------
# Pipeline exploration & generation helpers (for agent use)
# ---------------------------------------------------------------------------


def _make_explore_and_generate_tools(
    connector: DataHubConnector,
) -> list:
    """Create higher-level tools that combine exploration + generation.

    These tools let the agent explore DataHub metadata, build a pipeline
    context, and generate code artifacts — all in a single tool call.
    """
    from langchain_core.tools import tool

    @tool
    def explore_dataset(urn: str, hops: int = 2) -> str:
        """Explore a dataset in detail: schema, lineage, owners, tags, terms.

        Args:
            urn: The full DataHub URN of the dataset.
            hops: Number of lineage hops (default 2).
        """
        ds = connector.collector.get_dataset_context(urn, hops=hops)
        if not ds:
            return f"Could not fetch dataset: {urn}"

        lines = [
            f"## Dataset: {ds.name}",
            f"URN: {ds.urn}",
            f"Platform: {ds.platform or 'unknown'}",
            f"Description: {ds.description[:300] if ds.description else '(none)'}",
            f"Owners: {', '.join(ds.owners) if ds.owners else '(none)'}",
            f"Tags: {', '.join(ds.tags) if ds.tags else '(none)'}",
            f"Glossary Terms: {', '.join(ds.glossary_terms) if ds.glossary_terms else '(none)'}",
            "",
            f"### Schema ({len(ds.schema_fields)} fields)",
        ]
        for f in ds.schema_fields:
            lines.append(
                f"  - {f.field_path}: {f.native_type}  {f.description or ''}"
            )
        lines.append("")
        lines.append(f"### Upstream Sources ({len(ds.upstreams)})")
        for u in ds.upstreams[:10]:
            lines.append(f"  - {u}")
        lines.append(f"### Downstream Consumers ({len(ds.downstreams)})")
        for d in ds.downstreams[:10]:
            lines.append(f"  - {d}")
        return "\n".join(lines)

    @tool
    def search_datasets(query: str) -> str:
        """Search for datasets in DataHub by name or description.

        Args:
            query: Search term (e.g. 'customer', 'orders', 'revenue').
        """
        results = connector.collector.resolve_dataset(query)
        if not results:
            return f"No datasets found matching '{query}'."

        lines = [f"### Datasets matching '{query}' ({len(results)} found)"]
        for ds in results:
            urn_short = (
                ds.urn[:80] + "..." if len(ds.urn) > 80 else ds.urn
            )
            lines.append(
                f"- **{ds.name}** ({len(ds.schema_fields)} fields, "
                f"{len(ds.upstreams)} upstreams, {len(ds.downstreams)} downstreams) "
                f"`{urn_short}`"
            )
        return "\n".join(lines)

    @tool
    def build_pipeline_context(target_urn: str) -> str:
        """Build a full pipeline context for a target dataset.

        Walks upstream and downstream lineage to build a complete picture.
        Returns a detailed JSON summary of all collected metadata.

        Args:
            target_urn: The URN of the target dataset.
        """
        ctx = connector.collector.build_pipeline_context(target_urn, hops=2)
        if not ctx:
            return f"Failed to build pipeline context for {target_urn}"

        summary = {
            "target": {
                "name": ctx.target_dataset.name,
                "urn": ctx.target_dataset.urn,
                "fields": len(ctx.target_dataset.schema_fields),
            },
            "upstream_count": len(ctx.upstream_datasets),
            "downstream_count": len(ctx.downstream_datasets),
            "total_datasets": len(ctx.all_datasets),
            "upstreams": [
                {"name": d.name, "urn": d.urn, "fields": len(d.schema_fields)}
                for d in ctx.upstream_datasets
            ],
            "downstreams": [
                {"name": d.name, "urn": d.urn, "fields": len(d.schema_fields)}
                for d in ctx.downstream_datasets
            ],
            "all_tags": list(
                set(t for ds in ctx.all_datasets for t in ds.tags)
            ),
            "all_glossary_terms": list(
                set(t for ds in ctx.all_datasets for t in ds.glossary_terms)
            ),
        }
        return json.dumps(summary, indent=2)

    @tool
    def generate_pipeline_code(
        target_urn: str,
        model_name: str,
        framework: str = "dbt",
        output_dir: str = "output",
    ) -> str:
        """Generate pipeline code artifacts from DataHub metadata context.

        Builds the pipeline context, generates code via Jinja2 templates,
        writes files to disk, and writes metadata back to DataHub
        (tag, description, lineage).

        Args:
            target_urn: The URN of the target dataset.
            model_name: Short name for the generated model (e.g. 'daily_revenue').
            framework: Code framework — 'dbt' (default), 'sql', or 'dag'.
            output_dir: Directory to write artifacts to.
        """
        ctx = connector.collector.build_pipeline_context(target_urn, hops=2)
        if not ctx:
            return f"Failed to build pipeline context for {target_urn}"

        gen = PipelineGenerator()
        try:
            artifacts = gen.write_artifacts(
                ctx,
                model_name=model_name,
                output_dir=output_dir,
                framework=framework,
            )
        except Exception as e:
            logger.exception("Code generation failed")
            return f"Code generation failed: {e}"

        # Write-back metadata to DataHub
        upstream_urns = [d.urn for d in ctx.upstream_datasets if d.urn]
        wb_results = connector.writer.write_back_pipeline_metadata(
            dataset_urn=target_urn,
            generated_sql=str(artifacts.get("model_sql", artifacts.get("sql", ""))),
            upstream_urns=upstream_urns,
            model_name=model_name,
        )

        result_parts = [
            f"### Generated Pipeline: {model_name}",
            f"Framework: {framework}",
            f"Target: {ctx.target_dataset.name} ({target_urn})",
            f"Context: {len(ctx.all_datasets)} datasets, "
            f"{len(ctx.target_dataset.schema_fields)} target columns",
            "",
            "**Artifacts:**",
        ]
        for name, path in artifacts.items():
            result_parts.append(f"  - {name}: {path}")
        result_parts.append("")
        result_parts.append("**Write-back to DataHub:**")
        for key, val in wb_results.items():
            status = "✓" if val else "✗"
            result_parts.append(f"  - {key}: {status}")

        return "\n".join(result_parts)

    return [
        explore_dataset,
        search_datasets,
        build_pipeline_context,
        generate_pipeline_code,
    ]


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------


def build_agent(
    config: Optional[AgentConfig] = None,
    connector: Optional[DataHubConnector] = None,
) -> Any:
    """Build and return a LangChain agent wired with DataHub tools.

    The agent uses the 22 pre-built tools from
    ``datahub_agent_context.langchain_tools.build_langchain_tools``
    plus custom high-level exploration and generation tools.

    Args:
        config: Agent configuration. Falls back to environment variables.
        connector: Pre-configured DataHubConnector (created from config if
                   not provided).

    Returns:
        A compiled LangChain agent graph ready for ``.invoke()``.
    """
    if config is None:
        config = AgentConfig.from_env()

    # --- DataHub connector ---
    if connector is None:
        connector = DataHubConnector(
            server=config.datahub_server,
            token=config.datahub_token,
        )

    if config.verbose:
        logging.basicConfig(level=logging.INFO)
        logger.info(
            "DataHub server: %s  model: %s  framework: %s",
            config.datahub_server,
            config.model,
            config.generate_framework,
        )

    # --- Pre-built DataHub tools (22 tools incl. mutations) ---
    try:
        dh_tools = build_langchain_tools(
            connector.client,
            include_mutations=True,
        )
    except Exception as e:
        logger.warning(
            "build_langchain_tools failed (%s), falling back to connector-based tools.",
            e,
        )
        dh_tools = []

    # --- Custom tools ---
    custom_tools = [
        _make_tag_dataset_tool(connector),
        _make_set_description_tool(connector),
        _make_add_lineage_tool(connector),
    ]
    custom_tools += _make_explore_and_generate_tools(connector)

    all_tools = list(dh_tools) + custom_tools

    # --- LLM ---
    if not config.openai_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY (or openai_api_key) is required. "
            "Set the environment variable or pass it via AgentConfig."
        )

    llm = ChatOpenAI(
        model=config.model,
        openai_api_key=config.openai_api_key,
        openai_api_base=config.openai_base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout=config.request_timeout,
        default_headers={
            "HTTP-Referer": "https://github.com/muhammadzakriarasool/autopipeline",
            "X-Title": "AutoPipeline",
        },
    )

    # --- System prompt ---
    system_prompt = (
        "You are AutoPipeline, an intelligent data pipeline generator grounded in "
        "DataHub metadata.\n\n"
        "YOUR CAPABILITIES\n"
        "You have access to a comprehensive set of DataHub tools that let you:\n"
        "1. SEARCH for datasets, entities, and documents in the catalog.\n"
        "2. EXPLORE schema fields, lineage (upstream/downstream), owners, tags,\n"
        "   glossary terms, and dataset queries.\n"
        "3. GENERATE pipeline code artifacts — dbt models, SQL transformations,\n"
        "   and Airflow/Dagster DAGs — using the metadata you find.\n"
        "4. WRITE BACK to DataHub: add tags, update descriptions, add owners,\n"
        "   add glossary terms, and record lineage for generated artifacts.\n"
        "\n"
        "WORKFLOW\n"
        "When a user gives you a natural language pipeline request (e.g., "
        "\"build a daily revenue report from orders and customers\"):\n"
        "  Step 1 — Search for relevant datasets using `search` or `search_datasets`.\n"
        "  Step 2 — Explore each dataset with `explore_dataset` or `get_entities`\n"
        "           to understand schema, lineage, and metadata.\n"
        "  Step 3 — Build a full pipeline context with `build_pipeline_context`.\n"
        "  Step 4 — Generate code using `generate_pipeline_code` (dbt/sql/dag).\n"
        "  Step 5 — Write back to DataHub: tag the generated model, update the\n"
        "           description, and record lineage with `tag_dataset`,\n"
        "           `set_dataset_description`, `add_dataset_lineage`, or the\n"
        "           built-in mutation tools.\n"
        "\n"
        "IMPORTANT RULES\n"
        "  - Always include URNs in your responses so the user can reference them.\n"
        "  - When searching, try multiple terms if the first attempt yields nothing.\n"
        "  - For code generation, prefer the `generate_pipeline_code` tool which\n"
        "    handles context building, file generation, and write-back in one call.\n"
        "  - After generation, verify the write-back succeeded and report results.\n"
        "  - If a tool errors, report the error clearly and suggest alternatives.\n"
        "  - Use the `save_document` tool to persist structured generation reports\n"
        "    as DataHub documents.\n"
        "\n"
        f"Default generation framework: {config.generate_framework}\n"
        f"Default output directory: {config.output_dir}\n"
    )

    # --- Build agent ---
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=system_prompt,
        name="autopipeline_agent",
    )

    return agent


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------


def generate_with_agent(
    request: str,
    output_dir: Optional[str] = None,
    framework: Optional[str] = None,
    config: Optional[AgentConfig] = None,
    connector: Optional[DataHubConnector] = None,
) -> dict[str, Any]:
    """Accept a natural language pipeline request and execute it via the agent.

    This is the primary entry point for programmatic use. It builds the
    agent, invokes it with the user's request, and returns structured results.

    Args:
        request: Natural language pipeline request
            (e.g. "Build a dbt model for daily revenue from orders and customers").
        output_dir: Override output directory.
        framework: Override generation framework ('dbt', 'sql', 'dag').
        config: Agent configuration (falls back to environment variables).
        connector: Pre-configured DataHubConnector (created from config if
                   not provided).

    Returns:
        Dict with keys:
          - "success": bool
          - "request": the original request
          - "response": the agent's final response text
          - "messages_count": int, number of messages exchanged
          - "execution_time_seconds": float
          - "error": str (only on failure)

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set.
        RuntimeError: If the agent fails unexpectedly.
    """
    if config is None:
        config = AgentConfig.from_env()

    if output_dir:
        config.output_dir = output_dir
    if framework:
        config.generate_framework = framework

    # Verify DataHub connectivity early
    if connector is None:
        connector = DataHubConnector(
            server=config.datahub_server,
            token=config.datahub_token,
        )
    if not connector.verify():
        logger.warning(
            "DataHub connection verification failed. Continuing anyway — "
            "tools that require DataHub will report errors."
        )

    # Build agent
    agent = build_agent(config=config, connector=connector)

    # Invoke
    start_time = time.monotonic()
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": request}],
        })
        elapsed = time.monotonic() - start_time
    except Exception as e:
        elapsed = time.monotonic() - start_time
        logger.exception("Agent invocation failed after %.1fs", elapsed)
        return {
            "success": False,
            "request": request,
            "response": "",
            "messages": [],
            "execution_time_seconds": elapsed,
            "error": str(e),
        }

    # Extract the final response
    messages = result.get("messages", [])
    final_text = ""
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "content"):
            final_text = last_msg.content or ""
        elif isinstance(last_msg, dict):
            final_text = last_msg.get("content", "")

    return {
        "success": bool(final_text),
        "request": request,
        "response": final_text,
        "messages_count": len(messages),
        "execution_time_seconds": elapsed,
        "error": None,
    }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for the agent orchestrator.

    Reads the pipeline request from argv and runs the agent.
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m autopipeline.agent \"<pipeline request>\"")
        print()
        print("Examples:")
        print('  python -m autopipeline.agent "Build a dbt model for daily revenue"')
        print(
            '  AUTOPIPELINE_FRAMEWORK=dag python -m autopipeline.agent '
            '"Create an Airflow DAG for order processing"'
        )
        sys.exit(1)

    request = " ".join(sys.argv[1:])

    # Set up console logging if not already configured
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO if os.environ.get("AUTOPIPELINE_VERBOSE") else logging.WARNING,
            format="%(levelname)s: %(message)s",
        )

    print(f"🤖 AutoPipeline Agent")
    print(f"   Request: {request[:120]}{'...' if len(request) > 120 else ''}")
    print()

    result = generate_with_agent(request)

    print()
    if result["success"]:
        print("✅ Pipeline generation complete!")
        print()
        print(result["response"])
    else:
        print(f"❌ Generation failed: {result.get('error', 'unknown error')}")

    print()
    print(f"   Time: {result['execution_time_seconds']:.1f}s")
    print(f"   Messages exchanged: {result.get('messages_count', 0)}")


if __name__ == "__main__":
    main()
