from __future__ import annotations

import sqlglot
from sqlglot import exp


def extract_table_dependencies(sql: str, dialect: str = "duckdb") -> tuple[list[str], list[str]]:
    """Return (inputs, outputs) for CREATE TABLE ... AS SELECT ... statements."""
    statements = sqlglot.parse(sql, read=dialect)
    inputs: set[str] = set()
    outputs: set[str] = set()

    for statement in statements:
        if statement is None:
            continue
        if isinstance(statement, exp.Create):
            target = statement.find(exp.Table)
            if target is not None:
                outputs.add(_table_name(target))
            for table in statement.find_all(exp.Table):
                name = _table_name(table)
                if name not in outputs:
                    inputs.add(name)
        else:
            for table in statement.find_all(exp.Table):
                inputs.add(_table_name(table))

    return sorted(inputs), sorted(outputs)


def _table_name(node: exp.Table) -> str:
    parts = [p.name for p in node.parts if p.name]
    return ".".join(parts) if parts else node.name
