"""Tests for reporters."""

import pytest
import tempfile
from pathlib import Path

from src.eval.harness import EvalResult, ScenarioResult
from src.eval.judges.base import JudgeResult
from src.eval.scoring.aggregator import AggregateScore
from src.eval.scenarios.loader import EvalScenario
from src.eval.tracing.tracer import Trace
from src.eval.reporters.html import HTMLReporter


def _make_result(passed=True, num_scenarios=3):
    scenario_results = []
    for i in range(num_scenarios):
        sr = ScenarioResult(
            scenario=EvalScenario(id=f"s{i}", input=f"query {i}"),
            trace=Trace(input=f"query {i}", output=f"response {i}"),
            judge_results=[
                JudgeResult(judge_name="correctness", passed=passed, confidence=0.9, rationale="test"),
            ],
            aggregate_score=AggregateScore(
                weighted_score=1.0 if passed else 0.3,
                total_judges=1,
                passing_judges=1 if passed else 0,
            ),
            passed=passed,
            duration_ms=100.0,
        )
        scenario_results.append(sr)

    return EvalResult(
        scenario_results=scenario_results,
        aggregate_score=1.0 if passed else 0.3,
        pass_rate=1.0 if passed else 0.0,
        regressions=[],
        total_duration_ms=300.0,
        metadata={"num_scenarios": num_scenarios, "num_judges": 1, "dimension_scores": {"correctness": 1.0 if passed else 0.0}},
    )


def test_html_report_generated():
    """Happy path: HTML report generated with all sections."""
    result = _make_result(passed=True)
    reporter = HTMLReporter()

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        output_path = reporter.report(result, f.name)
        content = Path(output_path).read_text()

    assert "PASSED" in content
    assert "100%" in content
    assert "s0" in content


def test_html_report_all_fail():
    """Edge case: All-fail report renders gracefully."""
    result = _make_result(passed=False)
    reporter = HTMLReporter()

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        output_path = reporter.report(result, f.name)
        content = Path(output_path).read_text()

    assert "FAILED" in content
    assert "0%" in content
