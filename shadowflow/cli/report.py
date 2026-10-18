from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from shadowflow.config import load_settings
from shadowflow.graph.builder import build_graph, load_pipeline_from_dir, to_networkx
from shadowflow.graph.change_detection import outputs_for_changed_sql
from shadowflow.impact.blast_radius import compute_blast_radius
from shadowflow.impact.risk import assess_blast_radius
from shadowflow.execution.history import load_compare_report
from shadowflow.report.compare_markdown import compare_report_markdown
from shadowflow.report.markdown import impact_report_markdown

console = Console()


def register_report_command(app: typer.Typer) -> None:
    @app.command("report")
    def report(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        changed_sql: list[str] = typer.Option(
            ...,
            "--changed-sql",
            help="Changed SQL paths (repeatable)",
        ),
        output: Path | None = typer.Option(
            None,
            "-o",
            "--output",
            help="Write markdown report to this file",
        ),
        include_last_compare: bool = typer.Option(
            False,
            "--last-compare",
            help="Append saved differential compare section if present",
        ),
    ) -> None:
        """Generate a markdown impact report."""
        settings = load_settings(project)
        pipeline_dir = settings.pipeline_dir
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        graph = to_networkx(build_graph(definition))
        changed = {str(p) for p in changed_sql}
        seeds = outputs_for_changed_sql(definition, changed)
        if not seeds:
            console.print("[yellow]No matching pipeline outputs for changed SQL.[/yellow]")
            raise typer.Exit(code=1)

        blast = compute_blast_radius(graph, seeds)
        risk = assess_blast_radius(blast)
        md = impact_report_markdown(sorted(changed), blast, risk=risk)
        if include_last_compare:
            last = load_compare_report(project)
            if last is not None:
                md = md + "\n---\n\n" + compare_report_markdown(last)
            else:
                console.print("[yellow]No saved compare report (.shadowflow/last-compare.json).[/yellow]")
        if output:
            output.write_text(md, encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        else:
            console.print(md)
