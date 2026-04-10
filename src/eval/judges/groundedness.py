"""Groundedness judge - evaluates if output is grounded in provided context."""

from __future__ import annotations

from .base import BaseJudge, JudgeResult
from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


SYSTEM_PROMPT = """You are an evaluation judge assessing whether an AI agent's output is grounded in the context it was given.

"Grounded" means every claim in the output can be traced back to information in the context or input. The agent should not hallucinate facts, invent data, or make unsupported claims.

Respond in exactly this format:
Verdict: PASS or FAIL
Confidence: 0.0 to 1.0
Rationale: One sentence explaining your judgment, citing any ungrounded claims"""


class GroundednessJudge(BaseJudge):
    def __init__(self, **kwargs):
        super().__init__(name="groundedness", **kwargs)

    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        if trace.error:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale=f"Agent raised an error: {trace.error}",
            )

        if trace.output is None:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale="Agent produced no output",
            )

        context_pieces = []
        for step in trace.steps:
            if step.get("type") == "retrieval":
                context_pieces.append(step.get("content", ""))
            elif step.get("type") == "sub_agent_response":
                context_pieces.append(step.get("output", ""))

        context = "\n---\n".join(context_pieces) if context_pieces else scenario.input

        user_prompt = f"""Context provided to agent:
{context}

Agent output:
{trace.output}

Is every claim in the agent's output grounded in the provided context?"""

        response = await self._call_llm(SYSTEM_PROMPT, user_prompt)
        passed, confidence, rationale = self._parse_judge_response(response)

        return JudgeResult(
            judge_name=self.name,
            passed=passed,
            confidence=confidence,
            rationale=rationale,
        )
