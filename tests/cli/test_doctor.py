import json
from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_doctor_writes_output_json(tmp_path: Path) -> None:
    out = tmp_path / "doctor.json"
    result = runner.invoke(app, ["doctor", "examples/basic_pipeline", "-o", str(out)])
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["issues"] == []


def test_doctor_mkdir_creates_missing_dirs(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "shadowflow.yaml").write_text(
        "pipeline:\n  directory: ./pipeline\n\ndata:\n  directory: ./data\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["doctor", str(project), "--mkdir"])
    assert (project / "pipeline").is_dir()
    assert (project / "data").is_dir()
    assert result.exit_code == 1
    assert "No .sql files" in result.stdout


def test_doctor_ok_on_basic_pipeline() -> None:
    result = runner.invoke(app, ["doctor", "examples/basic_pipeline"])
    assert result.exit_code == 0
    assert "OK" in result.stdout
