import json
from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_report_json_includes_risk() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        ["report", str(project), "--changed-sql", "pipeline/01_clean_users.sql", "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["risk"]["level"]
