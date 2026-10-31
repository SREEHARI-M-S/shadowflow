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
from shadowflow.execution.history import load_compare_report, save_compare_report
from shadowflow.graph.change_detection import normalize_pipeline_path
from shadowflow.report.compare_markdown import compare_report_markdown

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
        show_risk: bool = typer.Option(False, "--risk", help="Print risk assessment"),
        show_propagation: bool = typer.Option(
            True,
            "--propagation/--no-propagation",
            help="Show estimated downstream % impact",
        ),
        save: bool = typer.Option(False, "--save", help="Write report to .shadowflow/last-compare.json"),
        show_last: bool = typer.Option(False, "--last", help="Print last saved compare report"),
        output: Path | None = typer.Option(
            None,
            "-o",
            "--output",
            help="Write markdown compare report to this file",
        ),
        fail_on_change: bool = typer.Option(
            False,
            "--fail-on-change",
            help="Exit with code 1 if any affected dataset has row or schema changes",
        ),
    ) -> None:
        """Run before/after pipeline variants and diff row counts on affected datasets."""
        if show_last:
            last = load_compare_report(project)
            if last is None:
                console.print("[yellow]No saved compare report. Run with --save first.[/yellow]")
                raise typer.Exit(code=1)
            console.print(json.dumps(last.model_dump(), indent=2))
            raise typer.Exit(code=0)

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

        if save:
            path = save_compare_report(project, report)
            console.print(f"[dim]Saved {path}[/dim]")

        if output is not None:
            if json_out:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
            else:
                output.write_text(compare_report_markdown(report), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")

        if json_out:
            console.print(json.dumps(report.model_dump(), indent=2))
            if fail_on_change:
                changed = [r for r in report.datasets if r.row_delta != 0 or r.schema_changed]
                if changed:
                    raise typer.Exit(code=1)
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
        if show_propagation and report.propagated:
            prop = Table(title="Estimated % impact (propagation model)")
            prop.add_column("Dataset")
            prop.add_column("Est. %", justify="right")
            prop.add_column("Source")
            for item in report.propagated:
                pct = f"{item.estimated_pct_change:.2f}" if item.estimated_pct_change is not None else "—"
                prop.add_row(item.dataset, pct, item.source)
            console.print(prop)
        if show_risk and report.risk:
            console.print(f"\n[bold]Risk:[/bold] {report.risk.level} ({report.risk.score})")

        if fail_on_change:
            changed = [r for r in report.datasets if r.row_delta != 0 or r.schema_changed]
            if changed:
                console.print(f"[red]{len(changed)} dataset(s) changed[/red]")
                raise typer.Exit(code=1)
