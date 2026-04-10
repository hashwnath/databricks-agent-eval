"""Multi-judge score aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..judges.base import JudgeResult


@dataclass
class AggregateScore:
    weighted_score: float
    per_judge: dict[str, float] = field(default_factory=dict)
    weights_used: dict[str, float] = field(default_factory=dict)
    total_judges: int = 0
    passing_judges: int = 0

    @property
    def pass_rate(self) -> float:
        return self.passing_judges / self.total_judges if self.total_judges else 0.0


def aggregate_scores(
    judge_results: list[JudgeResult],
    weights: dict[str, float] | None = None,
) -> AggregateScore:
    if not judge_results:
        return AggregateScore(weighted_score=0.0)

    weights = weights or {}
    total_weight = 0.0
    weighted_sum = 0.0
    per_judge = {}
    weights_used = {}
    passing = 0

    for result in judge_results:
        w = weights.get(result.judge_name, 1.0)
        score = result.score
        weighted_sum += score * w
        total_weight += w
        per_judge[result.judge_name] = score
        weights_used[result.judge_name] = w
        if result.passed:
            passing += 1

    weighted_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    return AggregateScore(
        weighted_score=weighted_score,
        per_judge=per_judge,
        weights_used=weights_used,
        total_judges=len(judge_results),
        passing_judges=passing,
    )
