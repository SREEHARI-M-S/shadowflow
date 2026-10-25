import json
from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_analyze_json_lists_steps() -> None:
    result = runner.invoke(app, ["analyze", "examples/basic_pipeline", "--json"])
    assert result.exit_code == 0
    assert '"steps"' in result.stdout
    assert "01_clean_users.sql" in result.stdout


def test_analyze_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "analyze.json"
    result = runner.invoke(app, ["analyze", "examples/basic_pipeline", "-o", str(out)])
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["steps"]
