from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from shadowflow.config import load_settings
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_doctor_command(app: typer.Typer) -> None:
    @app.command("doctor")
    def doctor(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        json_out: bool = typer.Option(False, "--json", help="Print checks as JSON"),
        mkdir: bool = typer.Option(
            False,
            "--mkdir",
            help="Create missing pipeline and data directories before validating",
        ),
        output: Path | None = typer.Option(None, "-o", "--output", help="Write check results JSON"),
    ) -> None:
        """Validate project layout, config, and pipeline SQL presence."""
        issues: list[str] = []
        config_path = project / "shadowflow.yaml"
        if not config_path.is_file():
            issues.append(f"Missing config: {config_path}")

        settings = load_settings(project) if config_path.is_file() else None
        if settings is not None and mkdir:
            settings.pipeline_dir.mkdir(parents=True, exist_ok=True)
            settings.data_dir.mkdir(parents=True, exist_ok=True)
        if settings is not None:
            if not settings.pipeline_dir.is_dir():
                issues.append(f"Missing pipeline directory: {settings.pipeline_dir}")
            elif not any(settings.pipeline_dir.glob("*.sql")):
                issues.append(f"No .sql files in {settings.pipeline_dir}")
            if not settings.data_dir.is_dir():
                issues.append(f"Missing data directory: {settings.data_dir}")

            if settings.pipeline_dir.is_dir():
                try:
                    load_pipeline_from_dir(settings.pipeline_dir)
                except Exception as exc:  # noqa: BLE001 — surface parse/build errors to user
                    issues.append(f"Pipeline load failed: {exc}")

        ok = not issues
        document = {"ok": ok, "project": str(project), "issues": issues}
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(document, indent=2), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        if json_out:
            console.print(json.dumps(document, indent=2))
        if json_out or output is not None:
            raise typer.Exit(code=0 if ok else 1)

        if ok:
            console.print(f"[green]OK[/green] {project}")
            raise typer.Exit(code=0)

        for item in issues:
            console.print(f"[red]✗[/red] {item}")
        raise typer.Exit(code=1)
