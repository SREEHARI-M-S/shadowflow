from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.config import load_settings
from shadowflow.graph.builder import build_graph, load_pipeline_from_dir, to_networkx
from shadowflow.graph.change_detection import outputs_for_changed_sql
from shadowflow.impact.blast_radius import compute_blast_radius
from shadowflow.diff.pipeline_compare import compare_pipeline_variants
from shadowflow.git.revisions import find_git_root, sql_overrides_for_change
from shadowflow.impact.risk import assess_blast_radius

console = Console()


def register_impact_command(app: typer.Typer) -> None:
    @app.command("impact")
    def impact(
        project: Path = typer.Argument(..., help="Pipeline project root (contains pipeline/)"),
        rev_range: str | None = typer.Option(
            None,
            "--rev",
            help="Git revision range, e.g. HEAD~1..HEAD",
        ),
        changed_sql: list[str] | None = typer.Option(
            None,
            "--changed-sql",
            help="Changed SQL paths relative to project (repeatable)",
        ),
        json_out: bool = typer.Option(False, "--json", help="Print machine-readable report"),
        show_risk: bool = typer.Option(False, "--risk", help="Include explainable risk score"),
        execute: bool = typer.Option(
            False,
            "--execute",
            help="Run differential pipeline execution (requires --rev)",
        ),
        seed: bool = typer.Option(False, "--seed", help="Seed demo data when using --execute"),
    ) -> None:
        """Estimate blast radius from changed SQL files or a git revision range."""
        settings = load_settings(project)
        pipeline_dir = settings.pipeline_dir
        if not pipeline_dir.is_dir():
            raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

        definition = load_pipeline_from_dir(pipeline_dir)
        graph = to_networkx(build_graph(definition))

        changed_files: set[str] = set()
        if rev_range:
            changed_files |= _git_changed_files(project, rev_range)
        if changed_sql:
            changed_files |= {str(p) for p in changed_sql}

        if not changed_files:
            console.print(
                "[yellow]No changes specified.[/yellow] Use --rev or --changed-sql.",
            )
            raise typer.Exit(code=1)

        seeds = outputs_for_changed_sql(definition, changed_files)
        if not seeds:
            console.print("[yellow]No pipeline outputs matched the changed SQL files.[/yellow]")
            raise typer.Exit(code=1)

        blast = compute_blast_radius(graph, seeds)
        risk = assess_blast_radius(blast) if show_risk or json_out or execute else None
        execution_report = None
        if execute:
            if not rev_range:
                console.print("[red]--execute requires --rev (e.g. HEAD~1..HEAD).[/red]")
                raise typer.Exit(code=1)
            repo = find_git_root(project)
            if repo is None:
                console.print("[red]Not a git repository.[/red]")
                raise typer.Exit(code=1)
            before_overrides, after_overrides = sql_overrides_for_change(
                repo,
                project,
                rev_range,
                changed_files,
            )
            execution_report = compare_pipeline_variants(
                definition,
                settings.data_dir,
                before_overrides,
                after_overrides,
                changed_paths=changed_files,
                seed_sample_data=seed,
            )

        if json_out:
            payload: dict[str, object] = {
                "changed_files": sorted(changed_files),
                "direct": blast.direct,
                "indirect": blast.indirect,
            }
            if risk is not None:
                payload["risk"] = {
                    "level": risk.level,
                    "score": risk.score,
                    "factors": [f.model_dump() for f in risk.factors],
                }
            if execution_report is not None:
                payload["execution"] = execution_report.model_dump()
            console.print(json.dumps(payload, indent=2))
            return

        table = Table(title="ShadowFlow impact (blast radius)")
        table.add_column("Kind", style="cyan")
        table.add_column("Datasets")
        table.add_row("Changed SQL", ", ".join(sorted(changed_files)))
        table.add_row("Direct", ", ".join(blast.direct) or "—")
        table.add_row("Indirect", ", ".join(blast.indirect) or "—")
        console.print(table)
        console.print(f"\n[dim]Total affected datasets: {len(blast.all_affected)}[/dim]")
        if risk is not None:
            console.print(f"\n[bold]Risk:[/bold] {risk.level} ({risk.score})")
        if execution_report is not None:
            exec_table = Table(title="Execution diff (affected datasets)")
            exec_table.add_column("Dataset")
            exec_table.add_column("Before", justify="right")
            exec_table.add_column("After", justify="right")
            exec_table.add_column("Delta", justify="right")
            for row in execution_report.datasets:
                exec_table.add_row(
                    row.dataset,
                    str(row.row_before),
                    str(row.row_after),
                    str(row.row_delta),
                )
            console.print(exec_table)


def _git_changed_files(project: Path, rev_range: str) -> set[str]:
    repo = _find_git_root(project)
    if repo is None:
        console.print("[red]Not a git repository.[/red] Use --changed-sql instead.")
        raise typer.Exit(code=1)

    result = subprocess.run(
        ["git", "diff", "--name-only", rev_range],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        console.print(f"[red]git diff failed:[/red] {result.stderr.strip()}")
        raise typer.Exit(code=1)

    paths = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    try:
        rel = project.resolve().relative_to(repo.resolve())
        prefix = str(rel).replace("\\", "/")
        if prefix != ".":
            paths = {p for p in paths if p.startswith(prefix)}
            paths = {p[len(prefix) + 1 :] if p.startswith(prefix + "/") else p for p in paths}
    except ValueError:
        pass
    return paths


def _find_git_root(start: Path) -> Path | None:
    path = start.resolve()
    for candidate in [path, *path.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None
