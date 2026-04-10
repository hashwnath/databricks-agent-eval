"""Cost efficiency judge - evaluates token usage and cost per scenario."""

from __future__ import annotations

from .base import BaseJudge, JudgeResult
from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


DEFAULT_COST_LIMITS = {
    "max_tokens_per_scenario": 10000,
    "max_llm_calls": 10,
    "max_duration_ms": 30000,
}


class CostEfficiencyJudge(BaseJudge):
    """Evaluates cost efficiency without calling an LLM - uses trace metrics directly."""

    def __init__(self, cost_limits: dict | None = None, **kwargs):
        super().__init__(name="cost_efficiency", **kwargs)
        self.cost_limits = cost_limits or DEFAULT_COST_LIMITS

    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        if trace.error:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale=f"Agent raised an error: {trace.error}",
            )

        total_tokens = sum(
            step.get("tokens_used", 0) for step in trace.steps
        )
        llm_calls = sum(
            1 for step in trace.steps if step.get("type") == "llm_call"
        )
        duration = trace.duration_ms

        violations = []

        max_tokens = self.cost_limits.get("max_tokens_per_scenario", 10000)
        if total_tokens > max_tokens:
            violations.append(
                f"Token usage ({total_tokens}) exceeds limit ({max_tokens})"
            )

        max_calls = self.cost_limits.get("max_llm_calls", 10)
        if llm_calls > max_calls:
            violations.append(
                f"LLM calls ({llm_calls}) exceeds limit ({max_calls})"
            )

        max_duration = self.cost_limits.get("max_duration_ms", 30000)
        if duration > max_duration:
            violations.append(
                f"Duration ({duration:.0f}ms) exceeds limit ({max_duration}ms)"
            )

        passed = len(violations) == 0
        confidence = 1.0

        if violations:
            rationale = "; ".join(violations)
        else:
            rationale = (
                f"Within limits: {total_tokens} tokens, "
                f"{llm_calls} LLM calls, {duration:.0f}ms"
            )

        return JudgeResult(
            judge_name=self.name,
            passed=passed,
            confidence=confidence,
            rationale=rationale,
            metadata={
                "total_tokens": total_tokens,
                "llm_calls": llm_calls,
                "duration_ms": duration,
            },
        )
