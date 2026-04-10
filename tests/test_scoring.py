"""Tests for scoring engine and regression detection."""

import pytest

from src.eval.judges.base import JudgeResult
from src.eval.scoring.aggregator import AggregateScore, aggregate_scores
from src.eval.scoring.regression import detect_regressions


def test_aggregate_scores_happy_path():
    """Happy path: 4 judges return scores, weighted aggregate matches."""
    results = [
        JudgeResult(judge_name="correctness", passed=True, confidence=0.9, rationale="ok"),
        JudgeResult(judge_name="routing", passed=True, confidence=0.95, rationale="ok"),
        JudgeResult(judge_name="groundedness", passed=True, confidence=0.8, rationale="ok"),
        JudgeResult(judge_name="cost", passed=False, confidence=1.0, rationale="over budget"),
    ]
    weights = {"correctness": 1.5, "routing": 2.0, "groundedness": 1.0, "cost": 0.5}

    agg = aggregate_scores(results, weights)

    assert agg.total_judges == 4
    assert agg.passing_judges == 3
    # Expected: (1*1.5 + 1*2.0 + 1*1.0 + 0*0.5) / (1.5+2.0+1.0+0.5) = 4.5/5.0 = 0.9
    assert abs(agg.weighted_score - 0.9) < 0.01


def test_aggregate_scores_empty():
    """Edge case: No judge results."""
    agg = aggregate_scores([])
    assert agg.weighted_score == 0.0
    assert agg.total_judges == 0


def test_aggregate_scores_default_weights():
    """All judges weighted equally when no weights provided."""
    results = [
        JudgeResult(judge_name="a", passed=True, confidence=1.0, rationale="ok"),
        JudgeResult(judge_name="b", passed=False, confidence=1.0, rationale="fail"),
    ]
    agg = aggregate_scores(results)
    assert abs(agg.weighted_score - 0.5) < 0.01


def test_regression_detected():
    """Regression detected when routing accuracy drops >10%."""
    baseline = {"correctness": 0.9, "routing_accuracy": 0.875}
    current = {"correctness": 0.85, "routing_accuracy": 0.75}

    regressions = detect_regressions(current, baseline, threshold=0.10)

    assert len(regressions) == 1
    assert regressions[0].dimension == "routing_accuracy"
    assert regressions[0].is_regression is True


def test_no_regression():
    """No regression when scores improve."""
    baseline = {"correctness": 0.8, "routing": 0.7}
    current = {"correctness": 0.9, "routing": 0.85}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 0


def test_regression_within_threshold():
    """Small drop within threshold is not flagged."""
    baseline = {"correctness": 0.9}
    current = {"correctness": 0.85}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 0
