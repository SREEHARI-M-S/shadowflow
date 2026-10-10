from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.config import load_settings
from shadowflow.execution.runner import run_pipeline
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_run_command(app: typer.Typer) -> None:
    @app.command("run")
    def run(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        seed: bool = typer.Option(
            False,
            "--seed",
            help="Generate sample Parquet inputs when missing (basic_pipeline demo)",
        ),
    ) -> None:
        """Execute pipeline SQL steps in order using DuckDB."""
        settings = load_settings(project)
        pipeline_dir = settings.pipeline_dir
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        result = run_pipeline(definition, settings.data_dir, seed_sample_data=seed)

        table = Table(title="Pipeline run complete")
        table.add_column("Output table")
        table.add_column("Row count", justify="right")
        for name, count in sorted(result.tables.items()):
            table.add_row(name, str(count))
        console.print(table)
