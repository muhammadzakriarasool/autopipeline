"""AutoPipeline CLI — 5 commands for pipeline generation and metadata operations."""

import os
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from autopipeline.config import DATAHUB_SERVER, DATAHUB_TOKEN, OPENROUTER_API_KEY, OUTPUT_DIR
from autopipeline.connector import DataHubConnector
from autopipeline.context import short_name, extract_platform, clean_owner, clean_tag, clean_term
from autopipeline.composer import compose_pipeline_prompt, compose_schema_prompt
from autopipeline.generator import PipelineGenerator

console = Console()


def _get_connector():
    if not DATAHUB_SERVER or not DATAHUB_TOKEN:
        console.print("[red]Set DATAHUB_SERVER and DATAHUB_TOKEN in .env[/red]")
        raise click.Abort()
    return DataHubConnector(DATAHUB_SERVER, DATAHUB_TOKEN)


@click.group()
def main():
    """AutoPipeline: Context-Aware Data Pipeline Generator."""


@main.command()
def verify():
    """Test DataHub connectivity."""
    conn = _get_connector()
    if conn.verify():
        console.print(Panel.fit(f"[green]Connected[/green]\n  Server: {DATAHUB_SERVER}"))
    else:
        console.print(f"[red]Connection failed[/red] (server: {DATAHUB_SERVER})")


@main.command()
@click.option("--query", "-q", required=True)
def search(query):
    """Search datasets in DataHub."""
    conn = _get_connector()
    datasets = conn.collector.resolve_dataset(query)
    if not datasets:
        console.print("[yellow]No datasets found[/yellow]")
        return
    table = Table(title=f"Datasets matching '{query}'")
    for col in ["Name", "Platform", "Fields", "Upstreams", "Downstreams"]:
        table.add_column(col, justify="right" if col in ["Fields", "Upstreams", "Downstreams"] else "left",
                         style="cyan" if col == "Name" else "green" if col == "Platform" else None)
    for ds in datasets:
        table.add_row(ds.name, short_name(ds.platform) if ds.platform else extract_platform(ds.urn),
                      str(len(ds.schema_fields)), str(len(ds.upstreams)), str(len(ds.downstreams)))
    console.print(table)
    console.print(f"[dim]{len(datasets)} datasets found[/dim]")


@main.command()
@click.argument("urn")
def inspect(urn):
    """Full metadata context for a dataset."""
    conn = _get_connector()
    ds = conn.collector.get_dataset_context(urn, hops=2)
    if not ds:
        console.print(f"[red]Could not fetch: {urn}[/red]")
        return
    console.print(f"\n[bold cyan]{ds.name}[/bold cyan]")
    console.print(f"  URN: {ds.urn}")
    if ds.platform:
        console.print(f"  Platform: {short_name(ds.platform)}")
    if ds.description:
        console.print(f"  Description: {ds.description[:300]}...")
    if ds.owners:
        console.print(f"  Owners: {', '.join(clean_owner(o) for o in ds.owners)}")
    if ds.tags:
        console.print(f"  Tags: {', '.join(clean_tag(t) for t in ds.tags)}")
    if ds.glossary_terms:
        console.print(f"  Terms: {', '.join(clean_term(t) for t in ds.glossary_terms)}")
    if ds.schema_fields:
        st = Table(title=f"Schema ({len(ds.schema_fields)} fields)")
        st.add_column("Field", style="cyan")
        st.add_column("Type", style="green")
        st.add_column("Description")
        for f in ds.schema_fields:
            st.add_row(f.field_path, f.native_type, (f.description or "")[:60])
        console.print(st)
    if ds.upstreams:
        console.print(f"\n[bold]Upstreams ({len(ds.upstreams)}):[/bold]")
        for u in ds.upstreams[:15]:
            console.print(f"  {short_name(u)}")
    if ds.downstreams:
        console.print(f"\n[bold]Downstreams ({len(ds.downstreams)}):[/bold]")
        for d in ds.downstreams[:15]:
            console.print(f"  {short_name(d)}")


@main.command()
@click.option("--query", "-q", required=True)
@click.option("--target", "-t", help="Dataset URN (auto-resolved if omitted)")
@click.option("--output", "-o", default=OUTPUT_DIR)
@click.option("--framework", "-f", default="dbt", type=click.Choice(["dbt", "sql", "dag"]))
@click.option("--dry-run", is_flag=True)
def generate(query, target, output, framework, dry_run):
    """Generate pipeline code from metadata context."""
    conn = _get_connector()

    if not target:
        datasets = conn.collector.resolve_dataset(query)
        if datasets:
            target = datasets[0].urn
            console.print(f"[dim]Auto-resolved: {datasets[0].name}[/dim]")

    if not target:
        console.print("[red]No dataset found[/red]")
        raise click.Abort()

    pipeline_ctx = conn.collector.build_pipeline_context(target, hops=2)
    if not pipeline_ctx:
        console.print("[red]Failed to build context[/red]")
        raise click.Abort()

    if dry_run:
        prompt = compose_pipeline_prompt(pipeline_ctx, user_request=query, framework=framework)
        from rich.syntax import Syntax
        console.print(Panel(Syntax(prompt, "markdown", theme="monokai", word_wrap=True),
                           title=f"[bold]LLM Prompt ({framework})[/bold]"))
        console.print(f"\n[dim]{len(pipeline_ctx.all_datasets)} datasets, {len(pipeline_ctx.target_dataset.schema_fields)} columns[/dim]")
        return

    model_name = query.lower().replace(" ", "_").replace("/", "_")[:60]

    if OPENROUTER_API_KEY:
        from autopipeline.agent import generate_with_agent
        console.print("[dim]Generating with AI agent...[/dim]")
        try:
            result = generate_with_agent(pipeline_ctx, query, framework, OPENROUTER_API_KEY,
                                         DATAHUB_SERVER, DATAHUB_TOKEN, output)
            method = result.get("method", "unknown")
            console.print(f"[bold green]Generated![/bold green] [dim]({method})[/dim]")
            arts = result.get("artifacts", {})
            if arts:
                console.print("\n[bold]Files:[/bold]")
                for name, path in arts.items():
                    if os.path.exists(path):
                        console.print(f"  {name}: {path} ({os.path.getsize(path)} bytes)")
        except Exception as e:
            console.print(f"[yellow]Agent failed ({e}), using template...[/yellow]")
            gen = PipelineGenerator()
            arts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output, framework=framework)
            for name, path in arts.items():
                console.print(f"  {name}: {path} ({os.path.getsize(path)} bytes)")
    else:
        console.print("[dim]No LLM key — using template generation[/dim]")
        gen = PipelineGenerator()
        arts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output, framework=framework)
        console.print(f"[bold green]Generated![/bold green]")
        console.print(f"  Model: {model_name} | Framework: {framework}")
        console.print(f"  Context: {len(pipeline_ctx.all_datasets)} datasets, {len(pipeline_ctx.target_dataset.schema_fields)} columns")
        for name, path in arts.items():
            console.print(f"  {name}: {path} ({os.path.getsize(path)} bytes)")


@main.command()
@click.option("--urn", required=True)
@click.option("--tag", default="urn:li:tag:AutoPipeline")
def tag(urn, tag):
    """Tag a dataset in DataHub (write-back test)."""
    conn = _get_connector()
    ok = conn.writer.add_tag(urn, tag)
    console.print(f"[green]Tag added[/green]" if ok else "[red]Failed[/red]")


if __name__ == "__main__":
    main()
