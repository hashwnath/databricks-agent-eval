"""Load evaluation scenarios from YAML/JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EvalScenario:
    id: str
    input: str
    expected_output: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    @property
    def expected_route(self) -> str | None:
        return self.metadata.get("expected_route")


def load_scenarios(path: str | Path) -> list[EvalScenario]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(path) as f:
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(f)
        elif path.suffix == ".json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}. Use .yaml or .json")

    if not isinstance(data, dict) or "scenarios" not in data:
        raise ValueError(
            f"Invalid scenario file: expected top-level 'scenarios' key in {path}"
        )

    scenarios = []
    for i, item in enumerate(data["scenarios"]):
        if not isinstance(item, dict) or "input" not in item:
            raise ValueError(
                f"Invalid scenario at index {i} in {path}: missing 'input' field"
            )

        scenarios.append(
            EvalScenario(
                id=item.get("id", f"scenario_{i}"),
                input=item["input"],
                expected_output=item.get("expected_output"),
                metadata=item.get("metadata", {}),
                tags=item.get("tags", []),
            )
        )

    return scenarios
