from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_doctor_ok_on_basic_pipeline() -> None:
    result = runner.invoke(app, ["doctor", "examples/basic_pipeline"])
    assert result.exit_code == 0
    assert "OK" in result.stdout
