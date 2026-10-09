from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_analyze_command(app: typer.Typer) -> None:
    @app.command("analyze")
    def analyze(
        project: Path = typer.Argument(..., help="Pipeline project root"),
    ) -> None:
        """List SQL steps and extracted dependencies."""
        pipeline_dir = project / "pipeline"
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        table = Table(title=f"Pipeline: {definition.name}")
        table.add_column("Step")
        table.add_column("Inputs")
        table.add_column("Outputs")
        for step in definition.steps:
            table.add_row(
                Path(step.path).name,
                ", ".join(step.inputs) or "—",
                ", ".join(step.outputs) or "—",
            )
        console.print(table)
