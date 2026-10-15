from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from shadowflow.config import load_settings
from shadowflow.execution.fingerprint import build_fingerprint
from shadowflow.execution.runner import run_pipeline
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_fingerprint_command(app: typer.Typer) -> None:
    @app.command("fingerprint")
    def fingerprint(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        seed: bool = typer.Option(False, "--seed", help="Seed demo Parquet if missing"),
        output: Path | None = typer.Option(None, "-o", "--output", help="Write JSON fingerprint"),
    ) -> None:
        """Run pipeline and emit dataset fingerprints (row counts + schema hash)."""
        settings = load_settings(project)
        definition = load_pipeline_from_dir(settings.pipeline_dir)
        result = run_pipeline(
            definition,
            settings.data_dir,
            seed_sample_data=seed,
            with_profiles=True,
        )
        fp = build_fingerprint(result.profiles, result.tables)
        text = fp.to_json()
        if output:
            output.write_text(text, encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        else:
            console.print(text)
