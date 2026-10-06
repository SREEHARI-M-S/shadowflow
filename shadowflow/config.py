from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ShadowFlowSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHADOWFLOW_")

    pipeline_dir: Path = Field(default=Path("pipeline"))
    data_dir: Path = Field(default=Path("data"))
    sample_size: int = Field(default=100_000, ge=1)


def load_settings(project_root: Path) -> ShadowFlowSettings:
    return ShadowFlowSettings(
        pipeline_dir=project_root / "pipeline",
        data_dir=project_root / "data",
    )
