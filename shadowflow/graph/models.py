from enum import Enum

from pydantic import BaseModel, Field


class NodeKind(str, Enum):
    DATASET = "dataset"
    EXTERNAL = "external"


class DatasetNode(BaseModel):
    name: str
    kind: NodeKind = NodeKind.DATASET


class DependencyEdge(BaseModel):
    source: str
    target: str


class PipelineGraph(BaseModel):
    nodes: list[DatasetNode] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)
