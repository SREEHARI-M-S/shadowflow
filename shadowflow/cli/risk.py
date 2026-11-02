from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.graph.builder import build_graph, load_pipeline_from_dir, to_networkx
from shadowflow.graph.change_detection import outputs_for_changed_sql
from shadowflow.impact.blast_radius import compute_blast_radius
from shadowflow.impact.risk import assess_blast_radius

console = Console()


def register_risk_command(app: typer.Typer) -> None:
    @app.command("risk")
    def risk(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        changed_sql: list[str] = typer.Option(
            ...,
            "--changed-sql",
            help="Changed SQL paths (repeatable)",
        ),
        json_out: bool = typer.Option(False, "--json", help="Print risk assessment as JSON"),
        output: Path | None = typer.Option(None, "-o", "--output", help="Write risk JSON to file"),
    ) -> None:
        """Explainable risk score from blast-radius analysis."""
        pipeline_dir = project / "pipeline"
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        graph = to_networkx(build_graph(definition))
        changed = {str(p) for p in changed_sql}
        seeds = outputs_for_changed_sql(definition, changed)
        if not seeds:
            console.print("[yellow]No matching outputs for changed SQL.[/yellow]")
            raise typer.Exit(code=1)

        blast = compute_blast_radius(graph, seeds)
        assessment = assess_blast_radius(blast)
        document = {
            "level": assessment.level,
            "score": assessment.score,
            "direct": blast.direct,
            "indirect": blast.indirect,
            "factors": [f.model_dump() for f in assessment.factors],
        }
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(document, indent=2), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        if json_out:
            console.print(json.dumps(document, indent=2))
        if json_out or output is not None:
            raise typer.Exit(code=0)

        console.print(f"\n[bold]RISK: {assessment.level}[/bold] (score {assessment.score})\n")
        table = Table(title="Factors")
        table.add_column("Points", justify="right")
        table.add_column("Reason")
        for factor in assessment.factors:
            table.add_row(str(factor.points), factor.description)
        console.print(table)
