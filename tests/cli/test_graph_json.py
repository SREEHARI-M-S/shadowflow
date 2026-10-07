from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_graph_json_output() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(app, ["graph", str(project), "--format", "json"])
    assert result.exit_code == 0
    assert '"nodes"' in result.stdout
    assert "clean_users" in result.stdout
