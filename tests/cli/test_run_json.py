import json
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


def test_run_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "run.json"
    result = runner.invoke(
        app,
        ["run", str(Path("examples/basic_pipeline")), "--seed", "-o", str(out)],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "clean_users" in payload["tables"]
