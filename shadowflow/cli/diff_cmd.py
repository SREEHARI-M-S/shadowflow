from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.diff.row_diff import RowCountDiff
from shadowflow.diff.schema_diff import diff_fingerprint_schemas
from shadowflow.execution.fingerprint import load_fingerprint

console = Console()


def register_diff_command(app: typer.Typer) -> None:
    @app.command("diff-counts")
    def diff_counts(
        before: Path = typer.Argument(..., help="JSON fingerprint from shadowflow fingerprint"),
        after: Path = typer.Argument(..., help="JSON fingerprint to compare"),
        json_out: bool = typer.Option(False, "--json", help="Print JSON diff"),
    ) -> None:
        """Compare row counts between two pipeline fingerprint files."""
        before_counts = _counts_from_fingerprint(before)
        after_counts = _counts_from_fingerprint(after)
        diff = RowCountDiff.compare(before_counts, after_counts)

        if json_out:
            console.print(json.dumps(diff.model_dump(), indent=2))
            return

        table = Table(title="Row count diff")
        table.add_column("Table")
        table.add_column("Before", justify="right")
        table.add_column("After", justify="right")
        table.add_column("Delta", justify="right")
        for row in diff.tables:
            table.add_row(str(row.table), str(row.before), str(row.after), str(row.delta))
        console.print(table)


    @app.command("diff-schema")
    def diff_schema_cmd(
        before: Path = typer.Argument(..., help="Before fingerprint JSON"),
        after: Path = typer.Argument(..., help="After fingerprint JSON"),
        json_out: bool = typer.Option(False, "--json", help="Print JSON diff"),
    ) -> None:
        """Compare table schemas between two fingerprint files."""
        b = load_fingerprint(before)
        a = load_fingerprint(after)
        before_cols = {d.table: d.columns for d in b.datasets}
        after_cols = {d.table: d.columns for d in a.datasets}
        result = diff_fingerprint_schemas(before_cols, after_cols)

        if json_out:
            console.print(json.dumps(result.model_dump(), indent=2))
            return

        if not result.tables:
            console.print("[green]No schema changes detected.[/green]")
            return

        table = Table(title="Schema diff")
        table.add_column("Table")
        table.add_column("Added")
        table.add_column("Removed")
        for row in result.tables:
            table.add_row(
                row.table,
                ", ".join(row.diff.added_columns) or "—",
                ", ".join(row.diff.removed_columns) or "—",
            )
        console.print(table)


def _counts_from_fingerprint(path: Path) -> dict[str, int]:
    fp = load_fingerprint(path)
    return {d.table: d.row_count for d in fp.datasets}
