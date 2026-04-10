"""Scoring rubric engine - configurable weights per judge."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Rubric:
    weights: dict[str, float] = field(default_factory=dict)
    pass_threshold: float = 0.7
    required_judges: list[str] = field(default_factory=list)

    def weight_for(self, judge_name: str) -> float:
        return self.weights.get(judge_name, 1.0)

    def is_required(self, judge_name: str) -> bool:
        if not self.required_judges:
            return True
        return judge_name in self.required_judges


def load_rubric(path: str | Path) -> Rubric:
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)

    return Rubric(
        weights=data.get("weights", {}),
        pass_threshold=data.get("pass_threshold", 0.7),
        required_judges=data.get("required_judges", []),
    )
