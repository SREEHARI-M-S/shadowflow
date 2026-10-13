from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_contracts_check_passes() -> None:
    project = Path("examples/basic_pipeline")
    contract = project / "contracts/clean_users.yaml"
    result = runner.invoke(
        app,
        ["contracts", "check", str(project), str(contract), "--seed"],
    )
    assert result.exit_code == 0
    assert "OK" in result.stdout
