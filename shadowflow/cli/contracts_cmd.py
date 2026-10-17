from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from shadowflow.config import load_settings
from shadowflow.contracts.validator import load_contract, validate_dataset_contract
from shadowflow.execution.runner import run_pipeline_open
from shadowflow.graph.builder import load_pipeline_from_dir

console = Console()


def register_contracts_command(app: typer.Typer) -> None:
    contracts_app = typer.Typer(help="Data contract checks")
    app.add_typer(contracts_app, name="contracts")

    @contracts_app.command("list")
    def list_contracts(
        project: Path = typer.Argument(..., help="Pipeline project root"),
    ) -> None:
        """List contract YAML files under contracts/."""
        contracts_dir = project / "contracts"
        if not contracts_dir.is_dir():
            console.print("[yellow]No contracts/ directory found.[/yellow]")
            raise typer.Exit(code=1)
        for path in sorted(contracts_dir.glob("*.yaml")):
            console.print(path.name)

    @contracts_app.command("check")
    def check(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        contract_file: Path = typer.Argument(..., help="YAML contract file"),
        seed: bool = typer.Option(False, "--seed", help="Seed demo Parquet if missing"),
        json_out: bool = typer.Option(False, "--json", help="Print validation result as JSON"),
    ) -> None:
        """Run pipeline and validate a dataset contract against DuckDB outputs."""
        settings = load_settings(project)
        definition = load_pipeline_from_dir(settings.pipeline_dir)
        _, conn = run_pipeline_open(definition, settings.data_dir, seed_sample_data=seed)
        contract = load_contract(contract_file)
        result = validate_dataset_contract(conn, contract)
        conn.close()

        if json_out:
            console.print(
                json.dumps(
                    {
                        "dataset": contract.dataset,
                        "ok": result.ok,
                        "violations": [v.model_dump() for v in result.violations],
                    },
                    indent=2,
                ),
            )
            raise typer.Exit(code=0 if result.ok else 1)

        if result.ok:
            console.print(f"[green]OK[/green] {contract.dataset}")
            raise typer.Exit(code=0)

        for v in result.violations:
            console.print(f"[red]{v.dataset}.{v.column}[/red]: {v.message}")
        raise typer.Exit(code=1)

    @contracts_app.command("check-all")
    def check_all(
        project: Path = typer.Argument(..., help="Pipeline project root"),
        seed: bool = typer.Option(False, "--seed", help="Seed demo Parquet if missing"),
        json_out: bool = typer.Option(False, "--json", help="Print results as JSON"),
    ) -> None:
        """Validate all YAML files in contracts/."""
        contracts_dir = project / "contracts"
        if not contracts_dir.is_dir():
            console.print("[yellow]No contracts/ directory found.[/yellow]")
            raise typer.Exit(code=1)

        settings = load_settings(project)
        definition = load_pipeline_from_dir(settings.pipeline_dir)
        _, conn = run_pipeline_open(definition, settings.data_dir, seed_sample_data=seed)

        results: list[dict[str, object]] = []
        failed = False
        for path in sorted(contracts_dir.glob("*.yaml")):
            contract = load_contract(path)
            result = validate_dataset_contract(conn, contract)
            results.append(
                {
                    "file": path.name,
                    "dataset": contract.dataset,
                    "ok": result.ok,
                    "violations": [v.model_dump() for v in result.violations],
                },
            )
            if not result.ok:
                failed = True
        conn.close()

        if json_out:
            console.print(json.dumps({"results": results}, indent=2))
            raise typer.Exit(code=1 if failed else 0)

        for item in results:
            if item["ok"]:
                console.print(f"[green]OK[/green] {item['file']}")
            else:
                console.print(f"[red]FAIL[/red] {item['file']}")
        raise typer.Exit(code=1 if failed else 0)
