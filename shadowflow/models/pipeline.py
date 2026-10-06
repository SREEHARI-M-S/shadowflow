from pydantic import BaseModel, Field


class SqlStep(BaseModel):
    path: str
    sql: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class PipelineDefinition(BaseModel):
    name: str
    steps: list[SqlStep] = Field(default_factory=list)
