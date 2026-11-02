import json
from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_risk_json_output() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        ["risk", str(project), "--changed-sql", "pipeline/01_clean_users.sql", "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["level"]
    assert payload["factors"]
