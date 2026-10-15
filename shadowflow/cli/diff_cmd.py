from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shadowflow.diff.row_diff import RowCountDiff

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


def _counts_from_fingerprint(path: Path) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for item in data.get("datasets", []):
        counts[str(item["table"])] = int(item["row_count"])
    return counts
