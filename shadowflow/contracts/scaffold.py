from __future__ import annotations

import yaml

from shadowflow.contracts.models import ColumnContract, DatasetContract
from shadowflow.diff.statistics import TableStatistics


def contract_yaml_from_table(dataset: str, stats: TableStatistics) -> str:
    contract = DatasetContract(
        dataset=dataset,
        contracts=[ColumnContract(column=name, nullable=True, unique=False) for name in stats.columns],
    )
    payload = {
        "dataset": contract.dataset,
        "contracts": [rule.model_dump() for rule in contract.contracts],
    }
    return yaml.safe_dump(payload, sort_keys=False)
