"""Core evaluation harness - orchestrates the full eval loop."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .judges.base import JudgeResult
from .scoring.aggregator import AggregateScore, aggregate_scores
from .scoring.regression import RegressionResult, detect_regressions
from .scenarios.loader import EvalScenario, load_scenarios
from .tracing.tracer import Trace, trace_agent_run


@dataclass
class ScenarioResult:
    scenario: EvalScenario
    trace: Trace
    judge_results: list[JudgeResult]
    aggregate_score: AggregateScore
    passed: bool
    duration_ms: float


@dataclass
class EvalResult:
    scenario_results: list[ScenarioResult] = field(default_factory=list)
    aggregate_score: float = 0.0
    pass_rate: float = 0.0
    regressions: list[RegressionResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return len(self.regressions) == 0 and self.pass_rate >= 0.7


class EvalHarness:
    """Orchestrates multi-agent evaluation runs.

    Usage:
        harness = EvalHarness(judges=[...], rubric_weights={...})
        result = await harness.run(agent_fn, "scenarios/basic_routing.yaml")
    """

    def __init__(
        self,
        judges: list[Any],
        rubric_weights: dict[str, float] | None = None,
        baseline: dict[str, float] | None = None,
        regression_threshold: float = 0.10,
    ):
        self.judges = judges
        self.rubric_weights = rubric_weights or {j.name: 1.0 for j in judges}
        self.baseline = baseline
        self.regression_threshold = regression_threshold

    async def run(
        self,
        agent_fn: Callable,
        scenario_path: str,
        scenarios: list[EvalScenario] | None = None,
    ) -> EvalResult:
        start = time.time()

        if scenarios is None:
            scenarios = load_scenarios(scenario_path)

        scenario_results = []
        all_judge_names: dict[str, list[float]] = {}

        for scenario in scenarios:
            result = await self._eval_scenario(agent_fn, scenario)
            scenario_results.append(result)

            for jr in result.judge_results:
                all_judge_names.setdefault(jr.judge_name, []).append(
                    1.0 if jr.passed else 0.0
                )

        pass_count = sum(1 for r in scenario_results if r.passed)
        pass_rate = pass_count / len(scenario_results) if scenario_results else 0.0

        dimension_scores = {
            name: sum(scores) / len(scores) for name, scores in all_judge_names.items()
        }

        regressions = []
        if self.baseline:
            regressions = detect_regressions(
                current=dimension_scores,
                baseline=self.baseline,
                threshold=self.regression_threshold,
            )

        total_duration = (time.time() - start) * 1000

        return EvalResult(
            scenario_results=scenario_results,
            aggregate_score=sum(dimension_scores.values()) / len(dimension_scores)
            if dimension_scores
            else 0.0,
            pass_rate=pass_rate,
            regressions=regressions,
            total_duration_ms=total_duration,
            metadata={
                "num_scenarios": len(scenarios),
                "num_judges": len(self.judges),
                "dimension_scores": dimension_scores,
            },
        )

    async def _eval_scenario(
        self, agent_fn: Callable, scenario: EvalScenario
    ) -> ScenarioResult:
        start = time.time()

        try:
            trace = await trace_agent_run(agent_fn, scenario.input)
        except Exception as e:
            trace = Trace(
                input=scenario.input,
                output=None,
                steps=[],
                error=str(e),
                duration_ms=0,
            )

        judge_results = []
        for judge in self.judges:
            try:
                result = await judge.evaluate(
                    trace=trace,
                    scenario=scenario,
                )
                judge_results.append(result)
            except Exception as e:
                judge_results.append(
                    JudgeResult(
                        judge_name=judge.name,
                        passed=False,
                        confidence=0.0,
                        rationale=f"Judge error: {e}",
                    )
                )

        agg = aggregate_scores(judge_results, self.rubric_weights)
        passed = agg.weighted_score >= 0.7 and trace.error is None

        duration = (time.time() - start) * 1000

        return ScenarioResult(
            scenario=scenario,
            trace=trace,
            judge_results=judge_results,
            aggregate_score=agg,
            passed=passed,
            duration_ms=duration,
        )
