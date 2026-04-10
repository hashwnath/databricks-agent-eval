"""Tests for LLM judges."""

import pytest

from src.eval.judges.base import JudgeResult
from src.eval.judges.cost_efficiency import CostEfficiencyJudge
from src.eval.scenarios.loader import EvalScenario
from src.eval.tracing.tracer import Trace


@pytest.fixture
def sample_scenario():
    return EvalScenario(
        id="test_scenario",
        input="My pipeline failed",
        expected_output="Pipeline issue found",
        metadata={"expected_route": "pipeline_debugger"},
    )


@pytest.fixture
def passing_trace():
    trace = Trace(input="My pipeline failed", output="Pipeline issue found")
    trace.add_step("routing", routed_to="pipeline_debugger", confidence=0.9)
    trace.add_step("llm_call", tokens_used=500)
    trace.add_step("sub_agent_response", agent="pipeline_debugger", output="Fixed", tokens_used=300)
    trace.add_step("llm_call", tokens_used=300)
    return trace


@pytest.fixture
def error_trace():
    return Trace(input="test", output=None, error="Connection timeout")


@pytest.mark.asyncio
async def test_cost_judge_within_limits(sample_scenario, passing_trace):
    """Happy path: Trace within cost limits passes."""
    judge = CostEfficiencyJudge()
    result = await judge.evaluate(passing_trace, sample_scenario)

    assert result.passed is True
    assert result.confidence == 1.0
    assert "Within limits" in result.rationale


@pytest.mark.asyncio
async def test_cost_judge_exceeds_tokens(sample_scenario):
    """Edge case: Trace exceeds token limit fails."""
    trace = Trace(input="test", output="result")
    for _ in range(20):
        trace.add_step("llm_call", tokens_used=1000)

    judge = CostEfficiencyJudge(cost_limits={"max_tokens_per_scenario": 5000, "max_llm_calls": 100, "max_duration_ms": 60000})
    result = await judge.evaluate(trace, sample_scenario)

    assert result.passed is False
    assert "Token usage" in result.rationale


@pytest.mark.asyncio
async def test_cost_judge_error_trace(sample_scenario, error_trace):
    """Edge case: Error trace fails cost judge."""
    judge = CostEfficiencyJudge()
    result = await judge.evaluate(error_trace, sample_scenario)

    assert result.passed is False
    assert "error" in result.rationale.lower()


@pytest.mark.asyncio
async def test_cost_judge_custom_limits(sample_scenario, passing_trace):
    """Custom cost limits are respected."""
    judge = CostEfficiencyJudge(cost_limits={
        "max_tokens_per_scenario": 100,
        "max_llm_calls": 1,
        "max_duration_ms": 30000,
    })
    result = await judge.evaluate(passing_trace, sample_scenario)
    assert result.passed is False
