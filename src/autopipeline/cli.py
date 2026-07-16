"""AutoPipeline CLI — Context-Aware Data Pipeline Generator."""

import os
import re

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from autopipeline.context import short_name, extract_platform_from_urn

from dotenv import load_dotenv

console = Console()
_connector_cache = {}

load_dotenv()

def get_connector():
    """Get or create a DataHubConnector from env vars."""
    key = ("DATAHUB_SERVER", "DATAHUB_TOKEN")
    if key not in _connector_cache:
        server = os.environ.get("DATAHUB_SERVER") or os.environ.get("DATAHUB_GMS_URL")
        token = os.environ.get("DATAHUB_TOKEN")
        if not server or not token:
            console.print("[red]Error:[/red] Set DATAHUB_SERVER and DATAHUB_TOKEN")
            console.print("  export DATAHUB_SERVER=http://172.17.0.1:8080")
            console.print("  export DATAHUB_TOKEN=your-token")
            raise click.Abort()
        from autopipeline.connector import DataHubConnector
        _connector_cache[key] = DataHubConnector(server, token)
    return _connector_cache[key]


def _clean_owner(raw: str) -> str:
    """Extract a clean owner name from an OwnerClass string."""
    m = re.search(r"(?:corpuser|corpGroup):([\w.@-]+)", raw)
    if m:
        name = m.group(1).strip()
        name = name[7:] if name.startswith('b2fd91.') else name
        return name
    return raw.split(":")[-1].rstrip("})\"'")


def _clean_tag(raw: str) -> str:
    """Extract a clean tag name from a TagAssociationClass string."""
    m = re.search(r"tag:([^'\")\]}]+)", raw)
    if m:
        return m.group(1).strip()
    return raw.split(":")[-1].rstrip("})\"'")


def _clean_term(raw: str) -> str:
    """Extract a clean glossary term name."""
    m = re.search(r"glossaryTerm:([^'\")\]}]+)", raw)
    if m:
        return m.group(1).strip()
    return raw.split(":")[-1].rstrip("})\"'")


@click.group()
def main():
    """AutoPipeline: Context-Aware Data Pipeline Generator."""
    pass


@main.command()
def verify():
    """Verify connectivity to DataHub."""
    conn = get_connector()
    healthy = conn.verify()
    server = os.environ.get("DATAHUB_SERVER") or os.environ.get("DATAHUB_GMS_URL", "?")
    if healthy:
        console.print(Panel.fit(
            "[green]\u2713 DataHub connection OK[/green]\n"
            f"  Server: {server}"
        ))
    else:
        console.print(f"[red]\u2717 DataHub connection failed[/red] (server: {server})")


@main.command()
@click.option("--query", "-q", required=True, help="Search term for datasets")
def search(query: str):
    """Search datasets in DataHub."""
    conn = get_connector()
    datasets = conn.collector.resolve_dataset(query)
    if not datasets:
        console.print("[yellow]No datasets found[/yellow]")
        return

    table = Table(title=f"Datasets matching '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Platform", style="green")
    table.add_column("Fields", justify="right")
    table.add_column("Upstreams", justify="right")
    table.add_column("Downstreams", justify="right")
    table.add_column("URN", style="dim")

    for ds in datasets:
        plat = short_name(ds.platform) if ds.platform else extract_platform_from_urn(ds.urn)
        urn_short = ds.urn[:60] + "..." if len(ds.urn) > 60 else ds.urn
        table.add_row(ds.name, plat, str(len(ds.schema_fields)),
                       str(len(ds.upstreams)), str(len(ds.downstreams)), urn_short)
    console.print(table)
    console.print(f"[dim]Total: {len(datasets)} datasets[/dim]")


@main.command()
@click.argument("urn")
def inspect(urn: str):
    """Show full metadata context for a dataset URN."""
    conn = get_connector()
    ds = conn.collector.get_dataset_context(urn, hops=2)
    if not ds:
        console.print(f"[red]Could not fetch dataset: {urn}[/red]")
        return

    console.print(f"\n[bold cyan]{ds.name}[/bold cyan]")
    console.print(f"  [dim]URN:[/dim] {ds.urn}")
    if ds.platform:
        console.print(f"  [dim]Platform:[/dim] {short_name(ds.platform)}")
    if ds.description:
        desc = ds.description[:300].replace("\n", " ")
        console.print(f"\n  [dim]Description:[/dim] {desc}...")

    if ds.owners:
        cleaned = [_clean_owner(o) for o in ds.owners]
        console.print(f"\n  [yellow]Owners:[/yellow] {', '.join(cleaned)}")
    if ds.tags:
        cleaned = [_clean_tag(t) for t in ds.tags]
        console.print(f"  [yellow]Tags:[/yellow] {', '.join(cleaned)}")
    if ds.glossary_terms:
        cleaned = [_clean_term(t) for t in ds.glossary_terms]
        console.print(f"  [yellow]Glossary Terms:[/yellow] {', '.join(cleaned)}")

    if ds.schema_fields:
        schema_table = Table(title=f"Schema ({len(ds.schema_fields)} fields)")
        schema_table.add_column("Field", style="cyan")
        schema_table.add_column("Type", style="green")
        schema_table.add_column("Description")
        for f in ds.schema_fields:
            desc = (f.description or "")[:60]
            schema_table.add_row(f.field_path, f.native_type, desc)
        console.print(schema_table)

    if ds.upstreams:
        console.print(f"\n[bold]Upstream Sources ({len(ds.upstreams)}):[/bold]")
        for u in ds.upstreams[:15]:
            console.print(f"  \u2022 {short_name(u)}")
    if ds.downstreams:
        console.print(f"\n[bold]Downstream Consumers ({len(ds.downstreams)}):[/bold]")
        for d in ds.downstreams[:15]:
            console.print(f"  \u2022 {short_name(d)}")


@main.command()
@click.option("--query", "-q", required=True, help="Natural language pipeline request")
@click.option("--target", "-t", help="DataHub URN of the target dataset (optional)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--framework", default="dbt", type=click.Choice(["dbt", "sql", "dag"]))
@click.option("--dry-run", is_flag=True, help="Print the prompt without calling an LLM")
def generate(query: str, target: str, output: str, framework: str, dry_run: bool):
    """Generate a pipeline from a natural language request.

    Uses DataHub metadata context as the foundation for generation.
    """
    conn = get_connector()

    if not target:
        datasets = conn.collector.resolve_dataset(query)
        if datasets:
            target = datasets[0].urn
            console.print(f"[dim]Auto-resolved dataset:[/dim] {datasets[0].name}")

    if target:
        pipeline_ctx = conn.collector.build_pipeline_context(target, hops=2)
        if not pipeline_ctx:
            console.print("[red]Failed to build pipeline context[/red]")
            raise click.Abort()
    else:
        console.print("[yellow]No target dataset found[/yellow]")
        from autopipeline.context import PipelineContext, DatasetContext
        pipeline_ctx = PipelineContext(
            target_dataset=DatasetContext(urn="", name="unknown"),
        )

    from autopipeline.context_composer import compose_pipeline_prompt
    prompt = compose_pipeline_prompt(pipeline_ctx, user_request=query, framework=framework)

    if dry_run:
        syntax = Syntax(prompt, "markdown", theme="monokai", word_wrap=True)
        console.print(Panel(syntax, title=f"[bold]AutoPipeline Prompt ({framework})[/bold]"))
        console.print(f"\n[dim]Target: {pipeline_ctx.target_dataset.urn}[/dim]")
        console.print(f"[dim]Context contains: {len(pipeline_ctx.all_datasets)} datasets, "
                      f"fetched at {pipeline_ctx.fetched_at}[/dim]")
        return

    model_name = query.lower().replace(" ", "_").replace("/", "_")[:60]
    from autopipeline.generator import PipelineGenerator
    gen = PipelineGenerator()

    # Check for OpenRouter API key
    import os
    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    if api_key:
        # Call LLM for smarter code generation
        from autopipeline.llm_client import generate_pipeline_with_llm, FREE_MODELS
        console.print("[dim]Using LLM to generate pipeline...[/dim]")
        try:
            llm_response = generate_pipeline_with_llm(
                prompt=compose_pipeline_prompt(pipeline_ctx, user_request=query, framework=framework),
                api_key=api_key,
            )
            console.print(f"[bold green]LLM pipeline generated![/bold green]")
            # Write the LLM response to the output file
            out_dir = os.path.join(output, "models")
            os.makedirs(out_dir, exist_ok=True)
            llm_file = os.path.join(out_dir, f"{model_name}_llm.sql")
            with open(llm_file, "w") as f:
                f.write(llm_response)
            console.print(f"  [green]LLM output:[/green] {llm_file} ({len(llm_response)} chars)")
            # Also write template version
            artifacts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output, framework=framework)
            for name, path in artifacts.items():
                size = os.path.getsize(path)
                console.print(f"  [green]{name}:[/green] {path} ({size} bytes)")
        except Exception as e:
            console.print(f"[yellow]LLM call failed ({e}), falling back to template...[/yellow]")
            artifacts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output, framework=framework)
            for name, path in artifacts.items():
                size = os.path.getsize(path)
                console.print(f"  [green]{name}:[/green] {path} ({size} bytes)")
    else:
        # Template-based generation (no LLM needed)
        console.print("[dim]No OPENROUTER_API_KEY — using template generation[/dim]")
        try:
            artifacts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output, framework=framework)
            console.print(f"[bold green]Pipeline generated![/bold green]")
            console.print(f"[dim]Model:[/dim] {model_name}")
            console.print(f"[dim]Framework:[/dim] {framework}")
            console.print(f"[dim]Context:[/dim] {len(pipeline_ctx.all_datasets)} datasets, "
                          f"{len(pipeline_ctx.target_dataset.schema_fields)} columns")
            console.print(f"\n[bold]Generated Files:[/bold]")
            for name, path in artifacts.items():
                size = os.path.getsize(path)
                console.print(f"  [green]{name}:[/green] {path} ({size} bytes)")
        except Exception as e:
            console.print(f"[red]Generation failed: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


@main.command()
@click.option("--urn", help="Dataset URN to tag")
@click.option("--tag", default="urn:li:tag:AutoPipeline", help="Tag URN to add")
def tag(urn: str, tag: str):
    """Add a tag to a dataset (write-back test)."""
    conn = get_connector()
    ok = conn.writer.add_tag_to_dataset(urn, tag)
    if ok:
        console.print(f"[green]\u2713 Tag '{tag}' added to {urn}[/green]")
    else:
        console.print(f"[red]\u2717 Failed to add tag[/red]")


if __name__ == "__main__":
    main()
