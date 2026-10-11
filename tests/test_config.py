from pathlib import Path

from shadowflow.config import load_settings


def test_load_settings_from_yaml() -> None:
    settings = load_settings(Path("examples/basic_pipeline"))
    assert settings.project_name == "basic_pipeline"
    assert settings.pipeline_dir.name == "pipeline"
    assert settings.data_dir.name == "data"
