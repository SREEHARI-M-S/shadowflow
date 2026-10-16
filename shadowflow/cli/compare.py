from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.config import load_settings
from shadowflow.diff.pipeline_compare import compare_pipeline_variants
from shadowflow.git.revisions import (
    changed_files,
    find_git_root,
    read_file_at_revision,
    sql_overrides_for_change,
)
from shadowflow.graph.builder import load_pipeline_from_dir
from shadowflow.graph.change_detection import normalize_pipeline_path

console = Console()


def register_compare_command(app: typer.Typer) -> None:
    @app.command("compare")
    def compare(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        rev_range: str | None = typer.Option(
            None,
            "--rev",
            help="Git range for before SQL, e.g. HEAD~1..HEAD",
        ),
        changed_sql: list[str] | None = typer.Option(
            None,
            "--changed-sql",
            help="Changed SQL file(s) under pipeline/",
        ),
        before_ref: str | None = typer.Option(
            None,
            "--before-ref",
            help="Git ref for before SQL when using --changed-sql (e.g. HEAD~1)",
        ),
        seed: bool = typer.Option(False, "--seed", help="Seed demo Parquet inputs"),
        json_out: bool = typer.Option(False, "--json", help="Machine-readable report"),
    ) -> None:
        """Run before/after pipeline variants and diff row counts on affected datasets."""
        settings = load_settings(project)
        definition = load_pipeline_from_dir(settings.pipeline_dir)

        changed_paths: set[str] = set()
        before_overrides: dict[str, str] = {}
        after_overrides: dict[str, str] = {}

        if rev_range:
            repo = find_git_root(project)
            if repo is None:
                console.print("[red]Not a git repository.[/red]")
                raise typer.Exit(code=1)
            changed_paths = changed_files(repo, rev_range)
            before_overrides, after_overrides = sql_overrides_for_change(
                repo,
                project,
                rev_range,
                changed_paths,
            )
        elif changed_sql:
            changed_paths = {normalize_pipeline_path(str(p)) for p in changed_sql}
            repo = find_git_root(project) if before_ref else None
            for path in changed_paths:
                basename = Path(path).name
                disk = settings.pipeline_dir / basename
                if disk.is_file():
                    after_overrides[basename] = disk.read_text(encoding="utf-8")
                if repo and before_ref:
                    try:
                        rel_project = project.resolve().relative_to(repo.resolve())
                        rel_sql = f"{rel_project.as_posix()}/{settings.pipeline_dir.name}/{basename}"
                    except ValueError:
                        rel_sql = f"{settings.pipeline_dir.name}/{basename}"
                    old = read_file_at_revision(repo, before_ref, rel_sql)
                    if old:
                        before_overrides[basename] = old
        else:
            console.print("Provide --rev or --changed-sql.")
            raise typer.Exit(code=1)

        if not before_overrides and not after_overrides:
            console.print("[yellow]No SQL overrides resolved.[/yellow]")
            raise typer.Exit(code=1)

        report = compare_pipeline_variants(
            definition,
            settings.data_dir,
            before_overrides,
            after_overrides,
            changed_paths=changed_paths or {normalize_pipeline_path(k) for k in after_overrides},
            seed_sample_data=seed,
        )

        if json_out:
            console.print(json.dumps(report.model_dump(), indent=2))
            return

        table = Table(title="Differential pipeline compare")
        table.add_column("Dataset")
        table.add_column("Before", justify="right")
        table.add_column("After", justify="right")
        table.add_column("Delta", justify="right")
        table.add_column("Schema?")
        for row in report.datasets:
            table.add_row(
                row.dataset,
                str(row.row_before),
                str(row.row_after),
                str(row.row_delta),
                "yes" if row.schema_changed else "no",
            )
        console.print(table)
        console.print(f"\n[dim]Affected datasets: {len(report.affected_datasets)}[/dim]")
