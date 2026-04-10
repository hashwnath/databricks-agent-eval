"""Correctness judge - evaluates if agent output matches expected answer."""

from __future__ import annotations

from .base import BaseJudge, JudgeResult
from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


SYSTEM_PROMPT = """You are an evaluation judge assessing whether an AI agent's output is correct.

Given the agent's input, output, and the expected ground truth, determine if the output is correct.
Consider semantic equivalence, not just string matching.

Respond in exactly this format:
Verdict: PASS or FAIL
Confidence: 0.0 to 1.0
Rationale: One sentence explaining your judgment"""


class CorrectnessJudge(BaseJudge):
    def __init__(self, **kwargs):
        super().__init__(name="correctness", **kwargs)

    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        if trace.error:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale=f"Agent raised an error: {trace.error}",
            )

        if not scenario.expected_output:
            return JudgeResult(
                judge_name=self.name,
                passed=True,
                confidence=0.5,
                rationale="No ground truth provided, skipping correctness check",
            )

        user_prompt = f"""Input: {scenario.input}
Agent Output: {trace.output}
Expected Output: {scenario.expected_output}

Is the agent's output correct?"""

        response = await self._call_llm(SYSTEM_PROMPT, user_prompt)
        passed, confidence, rationale = self._parse_judge_response(response)

        return JudgeResult(
            judge_name=self.name,
            passed=passed,
            confidence=confidence,
            rationale=rationale,
        )
