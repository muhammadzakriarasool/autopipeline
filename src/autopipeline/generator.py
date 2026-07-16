"""Code generator — uses Jinja2 templates + DataHub context to produce pipeline code."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from autopipeline.context import PipelineContext, DatasetContext, short_name

_TEMPLATE_DIR = Path(__file__).parent / "templates"


class PipelineGenerator:
    """Generates pipeline code artifacts from DataHub context using Jinja2 templates."""

    def __init__(self, template_dir: Optional[Path] = None):
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir or _TEMPLATE_DIR)),
            autoescape=select_autoescape(default=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _build_source_list(self, ctx: PipelineContext) -> list[dict]:
        """Build the source list for Jinja2 templates."""
        sources = []
        for ds in ctx.upstream_datasets:
            if not ds.schema_fields:
                continue
            source = {
                "alias": short_name(ds.name) if ds.name else f"src_{len(sources)}",
                "table": ds.name,
                "database": extract_db_from_urn(ds.urn),
                "schema": extract_schema_from_urn(ds.urn),
                "platform": short_name(ds.platform) if ds.platform else "unknown",
                "columns": [
                    {
                        "name": f.field_path,
                        "type": f.native_type,
                        "description": f.description or "",
                        "tags": [_clean_tag_str(t) for t in (f.tags or [])],
                    }
                    for f in ds.schema_fields
                ],
            }
            sources.append(source)
        return sources

    def _build_target_columns(self, ctx: PipelineContext) -> list[dict]:
        """Build target column list for Jinja2 templates."""
        return [
            {
                "name": f.field_path,
                "type": f.native_type,
                "description": f.description or "",
                "tags": [_clean_tag_str(t) for t in (f.tags or [])],
                "tests": _infer_tests(f),
            }
            for f in ctx.target_dataset.schema_fields
        ]

    def generate_dbt_model(self, ctx: PipelineContext, model_name: str) -> str:
        """Generate a dbt SQL model from DataHub context."""
        template = self.env.get_template("dbt_model.sql.j2")
        sources = self._build_source_list(ctx)
        target_cols = self._build_target_columns(ctx)
        upstream_names = [short_name(u.urn) for u in ctx.upstream_datasets]

        return template.render(
            model_name=model_name,
            description=ctx.target_dataset.description or "",
            sources=sources,
            target_columns=target_cols,
            target_urn=ctx.target_dataset.urn,
            upstream_names=upstream_names,
            tags=[short_name(t) for t in ctx.target_dataset.tags],
            joins=_build_joins(ctx),
            generated_at=datetime.now(timezone.utc).isoformat(),
            materialization="table",
        )

    def generate_dbt_schema_yml(self, ctx: PipelineContext, model_name: str) -> str:
        """Generate a dbt schema.yml from DataHub context."""
        template = self.env.get_template("dbt_schema.yml.j2")
        target_cols = self._build_target_columns(ctx)
        return template.render(
            model_name=model_name,
            description=ctx.target_dataset.description or "",
            target_columns=target_cols,
        )

    def generate_sql(self, ctx: PipelineContext) -> str:
        """Generate a plain SQL transformation from DataHub context."""
        template = self.env.get_template("sql_transform.sql.j2")
        sources = self._build_source_list(ctx)
        target_cols = self._build_target_columns(ctx)
        upstream_names = [short_name(u.urn) for u in ctx.upstream_datasets]
        return template.render(
            description=ctx.target_dataset.description or "",
            sources=sources,
            target_columns=target_cols,
            upstream_names=upstream_names,
            target_urn=ctx.target_dataset.urn,
            joins=_build_joins(ctx),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def generate_airflow_dag(self, ctx: PipelineContext, model_name: str) -> str:
        """Generate an Airflow DAG from DataHub context."""
        template = self.env.get_template("airflow_dag.py.j2")
        upstream_names = [short_name(u.urn) for u in ctx.upstream_datasets]
        return template.render(
            model_name=model_name,
            description=ctx.target_dataset.description or "",
            upstream_names=upstream_names,
            target_urn=ctx.target_dataset.urn,
            tags=[short_name(t) for t in ctx.target_dataset.tags],
            schedule="@daily",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def write_artifacts(
        self,
        ctx: PipelineContext,
        model_name: str,
        output_dir: str = "output",
        framework: str = "dbt",
    ) -> dict[str, str]:
        """Generate and write pipeline artifacts to disk.

        Returns:
            Dict mapping artifact names to file paths.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        artifacts = {}

        if framework == "dbt":
            model_sql = self.generate_dbt_model(ctx, model_name)
            model_file = out_path / "models" / f"{model_name}.sql"
            model_file.parent.mkdir(parents=True, exist_ok=True)
            model_file.write_text(model_sql)
            artifacts["model_sql"] = str(model_file)

            schema_yml = self.generate_dbt_schema_yml(ctx, model_name)
            schema_file = out_path / "models" / "schema.yml"
            schema_file.write_text(schema_yml)
            artifacts["schema_yml"] = str(schema_file)

        elif framework == "sql":
            sql = self.generate_sql(ctx)
            sql_file = out_path / f"{model_name}.sql"
            sql_file.write_text(sql)
            artifacts["sql"] = str(sql_file)

        elif framework == "dag":
            dag_py = self.generate_airflow_dag(ctx, model_name)
            dag_file = out_path / "dags" / f"{model_name}.py"
            dag_file.parent.mkdir(parents=True, exist_ok=True)
            dag_file.write_text(dag_py)
            artifacts["dag"] = str(dag_file)

        return artifacts


# --- Helper functions ---


def _clean_tag_str(raw: str) -> str:
    """Extract a clean tag name from a TagAssociationClass string."""
    m = re.search(r"'tag': 'urn:li:tag:([^']+)'", str(raw))
    if m:
        name = m.group(1).strip()
        return name[7:] if name.startswith('b2fd91.') else name
    return str(raw).split(':')[-1].rstrip("}'\"")


def _infer_tests(field) -> list[str]:
    """Infer dbt tests from field metadata."""
    tests = []
    if field.field_path.endswith("_id") or field.field_path.endswith("_key"):
        tests.append("not_null")
    if "email" in field.field_path.lower() or "phone" in field.field_path.lower():
        tests.append("unique")
    return tests


def _build_joins(ctx: PipelineContext) -> list[dict]:
    """Infer joins between upstream sources and target."""
    joins = []
    sources = [short_name(u.urn) for u in ctx.upstream_datasets if u.name]
    if len(sources) >= 2:
        for i in range(1, len(sources)):
            joins.append({
                "type": "LEFT",
                "alias": sources[i],
                "condition": f"{sources[0]}.id = {sources[i]}.id",
            })
    return joins


def extract_db_from_urn(urn: str) -> str:
    """Extract database name from a dataset URN."""
    name = short_name(urn)
    parts = name.split(".")
    return parts[0] if len(parts) >= 2 else "raw"


def extract_schema_from_urn(urn: str) -> str:
    """Extract schema name from a dataset URN."""
    name = short_name(urn)
    parts = name.split(".")
    return parts[1] if len(parts) >= 3 else "public"
