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
        output: Path | None = typer.Option(None, "-o", "--output", help="Write analysis JSON to file"),
    ) -> None:
        """List SQL steps and extracted dependencies."""
        settings = load_settings(project)
        pipeline_dir = settings.pipeline_dir
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        steps_payload = [
            {
                "file": Path(step.path).name,
                "path": step.path,
                "inputs": list(step.inputs),
                "outputs": list(step.outputs),
            }
            for step in definition.steps
        ]
        document = {"project": settings.project_name, "steps": steps_payload}
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(document, indent=2), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        if json_out:
            console.print(json.dumps(document, indent=2))
        if json_out or output is not None:
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
