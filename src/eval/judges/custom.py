"""Custom judge builder - define judges in natural language."""

from __future__ import annotations

from .base import BaseJudge, JudgeResult
from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


class CustomJudge(BaseJudge):
    """Build a custom LLM judge by defining evaluation criteria in natural language.

    Similar to Databricks' make_judge SDK (MLflow 3.4.0), this lets you create
    judges tailored to your specific quality dimensions.

    Usage:
        judge = CustomJudge(
            name="tone_check",
            criteria="The agent's response should be professional and concise. "
                     "It should not use jargon or be condescending.",
        )
    """

    def __init__(self, name: str, criteria: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.criteria = criteria

    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        if trace.error:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale=f"Agent raised an error: {trace.error}",
            )

        system_prompt = f"""You are an evaluation judge. Assess the agent's output against these criteria:

{self.criteria}

Respond in exactly this format:
Verdict: PASS or FAIL
Confidence: 0.0 to 1.0
Rationale: One sentence explaining your judgment"""

        user_prompt = f"""Input: {scenario.input}
Agent Output: {trace.output}

Does the output meet the criteria?"""

        response = await self._call_llm(system_prompt, user_prompt)
        passed, confidence, rationale = self._parse_judge_response(response)

        return JudgeResult(
            judge_name=self.name,
            passed=passed,
            confidence=confidence,
            rationale=rationale,
        )
