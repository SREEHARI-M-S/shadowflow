from __future__ import annotations

from pydantic import BaseModel, Field


class ColumnContract(BaseModel):
    column: str
    nullable: bool = True
    unique: bool = False


class DatasetContract(BaseModel):
    dataset: str
    contracts: list[ColumnContract] = Field(default_factory=list)
