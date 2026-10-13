from __future__ import annotations

from pathlib import Path

import duckdb
import yaml
from pydantic import BaseModel, Field

from shadowflow.contracts.models import DatasetContract


class ContractViolation(BaseModel):
    dataset: str
    column: str
    message: str


class ContractValidationResult(BaseModel):
    violations: list[ContractViolation] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def load_contract(path: Path) -> DatasetContract:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return DatasetContract.model_validate(data)


def validate_dataset_contract(
    conn: duckdb.DuckDBPyConnection,
    contract: DatasetContract,
) -> ContractValidationResult:
    violations: list[ContractViolation] = []
    for rule in contract.contracts:
        if not rule.nullable:
            row = conn.execute(
                f'SELECT COUNT(*) FROM {contract.dataset} WHERE "{rule.column}" IS NULL',
            ).fetchone()
            nulls = int(row[0]) if row else 0
            if nulls > 0:
                violations.append(
                    ContractViolation(
                        dataset=contract.dataset,
                        column=rule.column,
                        message=f"{nulls} null value(s) found (nullable=false)",
                    ),
                )
        if rule.unique:
            row = conn.execute(
                f"""
                SELECT COUNT(*) - COUNT(DISTINCT "{rule.column}")
                FROM {contract.dataset}
                """,
            ).fetchone()
            dupes = int(row[0]) if row else 0
            if dupes > 0:
                violations.append(
                    ContractViolation(
                        dataset=contract.dataset,
                        column=rule.column,
                        message=f"{dupes} duplicate value(s) (unique=true)",
                    ),
                )
    return ContractValidationResult(violations=violations)
