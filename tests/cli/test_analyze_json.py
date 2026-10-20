from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_analyze_json_lists_steps() -> None:
    result = runner.invoke(app, ["analyze", "examples/basic_pipeline", "--json"])
    assert result.exit_code == 0
    assert '"steps"' in result.stdout
    assert "01_clean_users.sql" in result.stdout
