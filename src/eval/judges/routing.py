"""Routing accuracy judge - evaluates supervisor routing decisions."""

from __future__ import annotations

from .base import BaseJudge, JudgeResult
from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


SYSTEM_PROMPT = """You are an evaluation judge assessing whether a supervisor agent routed a task to the correct sub-agent.

In a multi-agent system, the supervisor receives a user query and must route it to the most appropriate specialized sub-agent. You must evaluate whether the routing decision was correct.

Consider:
1. Does the query's primary intent match the sub-agent's specialization?
2. Could another sub-agent have handled it better?
3. Was the routing confidence appropriate?

Respond in exactly this format:
Verdict: PASS or FAIL
Confidence: 0.0 to 1.0
Rationale: One sentence explaining your judgment"""


class RoutingAccuracyJudge(BaseJudge):
    def __init__(self, **kwargs):
        super().__init__(name="routing_accuracy", **kwargs)

    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        if trace.error:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=1.0,
                rationale=f"Agent raised an error: {trace.error}",
            )

        routing_step = None
        for step in trace.steps:
            if step.get("type") == "routing":
                routing_step = step
                break

        if routing_step is None:
            return JudgeResult(
                judge_name=self.name,
                passed=False,
                confidence=0.8,
                rationale="No routing decision found in trace",
            )

        expected_route = scenario.metadata.get("expected_route")
        actual_route = routing_step.get("routed_to")

        if expected_route and actual_route:
            if actual_route == expected_route:
                return JudgeResult(
                    judge_name=self.name,
                    passed=True,
                    confidence=0.95,
                    rationale=f"Correctly routed to {actual_route}",
                )

        user_prompt = f"""Input: {scenario.input}
Available sub-agents: {scenario.metadata.get('available_agents', 'unknown')}
Supervisor routed to: {actual_route}
Expected route: {expected_route or 'not specified'}
Routing confidence: {routing_step.get('confidence', 'unknown')}

Was this the correct routing decision?"""

        response = await self._call_llm(SYSTEM_PROMPT, user_prompt)
        passed, confidence, rationale = self._parse_judge_response(response)

        return JudgeResult(
            judge_name=self.name,
            passed=passed,
            confidence=confidence,
            rationale=rationale,
            metadata={"actual_route": actual_route, "expected_route": expected_route},
        )
