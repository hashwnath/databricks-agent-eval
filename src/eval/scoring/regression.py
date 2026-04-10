"""Regression detection - compare current scores against baselines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegressionResult:
    dimension: str
    baseline_score: float
    current_score: float
    delta: float
    threshold: float
    is_regression: bool

    @property
    def delta_pct(self) -> str:
        return f"{self.delta * 100:+.1f}%"


def detect_regressions(
    current: dict[str, float],
    baseline: dict[str, float],
    threshold: float = 0.10,
) -> list[RegressionResult]:
    results = []

    for dimension, baseline_score in baseline.items():
        current_score = current.get(dimension, 0.0)
        delta = current_score - baseline_score
        is_regression = delta < -threshold

        results.append(
            RegressionResult(
                dimension=dimension,
                baseline_score=baseline_score,
                current_score=current_score,
                delta=delta,
                threshold=threshold,
                is_regression=is_regression,
            )
        )

    return [r for r in results if r.is_regression]
