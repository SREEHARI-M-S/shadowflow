from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.config import load_settings
from shadowflow.execution.planner import order_steps, steps_upto
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_plan_command(app: typer.Typer) -> None:
    @app.command("plan")
    def plan(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        json_out: bool = typer.Option(False, "--json", help="Print ordered steps as JSON"),
        upto: str | None = typer.Option(
            None,
            "--upto",
            help="Only show steps required to materialize this output table",
        ),
    ) -> None:
        """Show SQL steps in dependency execution order."""
        settings = load_settings(project)
        definition = load_pipeline_from_dir(settings.pipeline_dir)
        steps = order_steps(definition)
        if upto is not None:
            try:
                steps = steps_upto(steps, upto)
            except ValueError as exc:
                raise typer.BadParameter(str(exc)) from exc

        if json_out:
            payload = [
                {
                    "path": s.path,
                    "outputs": list(s.outputs),
                    "inputs": list(s.inputs),
                }
                for s in steps
            ]
            console.print(json.dumps(payload, indent=2))
            return

        table = Table(title="Execution plan")
        table.add_column("#", justify="right")
        table.add_column("SQL file")
        table.add_column("Outputs")
        for index, step in enumerate(steps, start=1):
            table.add_row(
                str(index),
                Path(step.path).name,
                ", ".join(step.outputs) or "—",
            )
        console.print(table)
