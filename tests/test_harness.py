"""Tests for the eval harness orchestrator."""

import pytest

from src.eval.harness import EvalHarness, EvalResult
from src.eval.judges.cost_efficiency import CostEfficiencyJudge
from src.eval.scenarios.loader import EvalScenario
from src.eval.tracing.tracer import Trace


class MockPassingJudge:
    name = "mock_passing"

    async def evaluate(self, trace, scenario):
        from src.eval.judges.base import JudgeResult
        return JudgeResult(
            judge_name=self.name,
            passed=True,
            confidence=0.9,
            rationale="Mock pass",
        )


class MockFailingJudge:
    name = "mock_failing"

    async def evaluate(self, trace, scenario):
        from src.eval.judges.base import JudgeResult
        return JudgeResult(
            judge_name=self.name,
            passed=False,
            confidence=0.9,
            rationale="Mock fail",
        )


async def mock_agent(input_text, trace=None):
    if trace:
        trace.add_step("routing", routed_to="pipeline_debugger", confidence=0.9)
        trace.add_step("llm_call", tokens_used=100)
    return f"Response to: {input_text}"


async def mock_failing_agent(input_text, trace=None):
    raise RuntimeError("Agent crashed")


@pytest.mark.asyncio
async def test_harness_happy_path():
    """Happy path: Run eval on scenarios, all pass."""
    scenarios = [
        EvalScenario(id="s1", input="test query 1", expected_output="response 1"),
        EvalScenario(id="s2", input="test query 2", expected_output="response 2"),
    ]

    harness = EvalHarness(judges=[MockPassingJudge()])
    result = await harness.run(mock_agent, "", scenarios=scenarios)

    assert isinstance(result, EvalResult)
    assert len(result.scenario_results) == 2
    assert result.pass_rate == 1.0
    assert result.passed is True


@pytest.mark.asyncio
async def test_harness_agent_exception():
    """Edge case: Agent raises exception, harness captures gracefully."""
    scenarios = [
        EvalScenario(id="s1", input="test", expected_output="response"),
    ]

    harness = EvalHarness(judges=[MockPassingJudge()])
    result = await harness.run(mock_failing_agent, "", scenarios=scenarios)

    assert len(result.scenario_results) == 1
    sr = result.scenario_results[0]
    assert sr.trace.error is not None
    assert sr.passed is False


@pytest.mark.asyncio
async def test_harness_regression_detection():
    """Regression detection flags drops from baseline."""
    scenarios = [
        EvalScenario(id="s1", input="test", expected_output="response"),
    ]

    harness = EvalHarness(
        judges=[MockFailingJudge()],
        baseline={"mock_failing": 0.9},
        regression_threshold=0.10,
    )
    result = await harness.run(mock_agent, "", scenarios=scenarios)

    assert len(result.regressions) > 0
    assert result.passed is False


@pytest.mark.asyncio
async def test_harness_empty_scenarios():
    """Edge case: Empty scenario list."""
    harness = EvalHarness(judges=[MockPassingJudge()])
    result = await harness.run(mock_agent, "", scenarios=[])

    assert len(result.scenario_results) == 0
    assert result.pass_rate == 0.0
