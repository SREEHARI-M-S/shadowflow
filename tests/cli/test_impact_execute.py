from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_execute_requires_rev() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        [
            "impact",
            str(project),
            "--changed-sql",
            "pipeline/01_clean_users.sql",
            "--execute",
        ],
    )
    assert result.exit_code == 1
    assert "--rev" in result.stdout


def test_check_all_contracts() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        ["contracts", "check-all", str(project), "--seed", "--json"],
    )
    assert result.exit_code == 0
    assert '"results"' in result.stdout
