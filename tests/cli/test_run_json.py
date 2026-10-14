from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_run_json() -> None:
    result = runner.invoke(
        app,
        ["run", str(Path("examples/basic_pipeline")), "--seed", "--json"],
    )
    assert result.exit_code == 0
    assert '"clean_users"' in result.stdout
