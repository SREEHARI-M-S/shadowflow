from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.config import load_settings
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_analyze_command(app: typer.Typer) -> None:
    @app.command("analyze")
    def analyze(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        json_out: bool = typer.Option(False, "--json", help="Print steps as JSON"),
    ) -> None:
        """List SQL steps and extracted dependencies."""
        settings = load_settings(project)
        pipeline_dir = settings.pipeline_dir
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        if json_out:
            payload = [
                {
                    "file": Path(step.path).name,
                    "path": step.path,
                    "inputs": list(step.inputs),
                    "outputs": list(step.outputs),
                }
                for step in definition.steps
            ]
            console.print(json.dumps({"project": settings.project_name, "steps": payload}, indent=2))
            return

        table = Table(title=f"Pipeline: {settings.project_name}")
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
