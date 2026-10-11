from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ShadowFlowSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHADOWFLOW_")

    project_name: str = Field(default="pipeline")
    pipeline_dir: Path = Field(default=Path("pipeline"))
    data_dir: Path = Field(default=Path("data"))
    sample_size: int = Field(default=100_000, ge=1)


def load_settings(project_root: Path) -> ShadowFlowSettings:
    config_path = project_root / "shadowflow.yaml"
    data: dict[str, object] = {}
    if config_path.is_file():
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded

    project = data.get("project", {})
    pipeline = data.get("pipeline", {})
    data_section = data.get("data", {})

    project_name = "pipeline"
    if isinstance(project, dict) and project.get("name"):
        project_name = str(project["name"])

    pipeline_dir = project_root / "pipeline"
    if isinstance(pipeline, dict) and pipeline.get("directory"):
        pipeline_dir = project_root / str(pipeline["directory"])

    data_dir = project_root / "data"
    if isinstance(data_section, dict) and data_section.get("directory"):
        data_dir = project_root / str(data_section["directory"])

    return ShadowFlowSettings(
        project_name=project_name,
        pipeline_dir=pipeline_dir,
        data_dir=data_dir,
    )
