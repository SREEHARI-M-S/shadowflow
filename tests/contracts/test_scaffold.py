from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_contracts_scaffold_writes_yaml(tmp_path: Path) -> None:
    out = tmp_path / "clean_users.yaml"
    result = runner.invoke(
        app,
        [
            "contracts",
            "scaffold",
            "examples/basic_pipeline",
            "--dataset",
            "clean_users",
            "-o",
            str(out),
            "--seed",
        ],
    )
    assert result.exit_code == 0
    text = out.read_text(encoding="utf-8")
    assert "dataset: clean_users" in text
    assert "user_id" in text
