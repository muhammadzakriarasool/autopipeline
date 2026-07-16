"""Pipeline generator — renders Jinja2 templates with DataHub metadata."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from autopipeline.context import PipelineContext, short_name

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _infer_tests(field) -> list[str]:
    tests = []
    if field.field_path.endswith("_id") or field.field_path.endswith("_key"):
        tests.append("not_null")
    if "email" in field.field_path.lower() or "phone" in field.field_path.lower():
        tests.append("unique")
    return tests


def _build_sources(ctx: PipelineContext) -> list[dict]:
    sources = []
    for ds in ctx.upstream_datasets:
        if not ds.schema_fields:
            continue
        name = short_name(ds.name) if ds.name else f"src_{len(sources)}"
        sources.append({
            "alias": name,
            "table": ds.name,
            "database": extract_db(ds.urn),
            "schema": extract_schema(ds.urn),
            "platform": short_name(ds.platform) if ds.platform else "unknown",
            "columns": [
                {"name": f.field_path, "type": f.native_type, "description": f.description or "", "tags": f.tags or []}
                for f in ds.schema_fields
            ],
        })
    return sources


def _build_target_cols(ctx: PipelineContext) -> list[dict]:
    return [
        {"name": f.field_path, "type": f.native_type, "description": f.description or "", "tags": f.tags or [], "tests": _infer_tests(f)}
        for f in ctx.target_dataset.schema_fields
    ]


def extract_db(urn: str) -> str:
    name = short_name(urn)
    parts = name.split(".")
    return parts[0] if len(parts) >= 2 else "raw"


def extract_schema(urn: str) -> str:
    name = short_name(urn)
    parts = name.split(".")
    return parts[1] if len(parts) >= 3 else "public"


class PipelineGenerator:
    def __init__(self, template_dir: Optional[Path] = None):
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir or _TEMPLATE_DIR)),
            trim_blocks=True, lstrip_blocks=True,
        )

    def generate_dbt_model(self, ctx: PipelineContext, model_name: str) -> str:
        t = self.env.get_template("dbt_model.sql.j2")
        return t.render(
            model_name=model_name, description=ctx.target_dataset.description or "",
            sources=_build_sources(ctx), target_columns=_build_target_cols(ctx),
            target_urn=ctx.target_dataset.urn,
            upstream_names=[short_name(u.urn) for u in ctx.upstream_datasets],
            tags=[short_name(t) for t in ctx.target_dataset.tags],
            joins=[], generated_at=datetime.now(timezone.utc).isoformat(),
            materialization="table",
        )

    def generate_schema_yml(self, ctx: PipelineContext, model_name: str) -> str:
        t = self.env.get_template("dbt_schema.yml.j2")
        return t.render(model_name=model_name, description=ctx.target_dataset.description or "", target_columns=_build_target_cols(ctx))

    def generate_sql(self, ctx: PipelineContext) -> str:
        t = self.env.get_template("sql_transform.sql.j2")
        return t.render(
            description=ctx.target_dataset.description or "",
            sources=_build_sources(ctx), target_columns=_build_target_cols(ctx),
            upstream_names=[short_name(u.urn) for u in ctx.upstream_datasets],
            target_urn=ctx.target_dataset.urn, joins=[],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def generate_dag(self, ctx: PipelineContext, model_name: str) -> str:
        t = self.env.get_template("airflow_dag.py.j2")
        return t.render(
            model_name=model_name, description=ctx.target_dataset.description or "",
            upstream_names=[short_name(u.urn) for u in ctx.upstream_datasets],
            target_urn=ctx.target_dataset.urn,
            tags=[short_name(t) for t in ctx.target_dataset.tags],
            schedule="@daily", generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def write_artifacts(self, ctx: PipelineContext, model_name: str, output_dir: str = "output", framework: str = "dbt") -> dict[str, str]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        artifacts = {}
        if framework == "dbt":
            (out / "models").mkdir(parents=True, exist_ok=True)
            p1 = out / "models" / f"{model_name}.sql"
            p1.write_text(self.generate_dbt_model(ctx, model_name))
            artifacts["model_sql"] = str(p1)
            p2 = out / "models" / "schema.yml"
            p2.write_text(self.generate_schema_yml(ctx, model_name))
            artifacts["schema_yml"] = str(p2)
        elif framework == "sql":
            p = out / f"{model_name}.sql"
            p.write_text(self.generate_sql(ctx))
            artifacts["sql"] = str(p)
        elif framework == "dag":
            (out / "dags").mkdir(parents=True, exist_ok=True)
            p = out / "dags" / f"{model_name}.py"
            p.write_text(self.generate_dag(ctx, model_name))
            artifacts["dag"] = str(p)
        return artifacts
