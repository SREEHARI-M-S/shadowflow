import json
from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_compare_json_writes_output(tmp_path: Path) -> None:
    out = tmp_path / "compare.json"
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        [
            "compare",
            str(project),
            "--changed-sql",
            "pipeline/01_clean_users.sql",
            "--seed",
            "--json",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "datasets" in payload
