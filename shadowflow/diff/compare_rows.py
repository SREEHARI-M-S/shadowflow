from __future__ import annotations

from pydantic import BaseModel


class DatasetCompareRow(BaseModel):
    dataset: str
    row_before: int
    row_after: int
    row_delta: int
    schema_changed: bool
