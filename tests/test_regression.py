"""Tests for regression detection."""

from src.eval.scoring.regression import detect_regressions, RegressionResult


def test_regression_exact_threshold():
    """Edge case: Drop exactly at threshold is not flagged."""
    baseline = {"routing": 1.0}
    current = {"routing": 0.90}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 0


def test_regression_just_over_threshold():
    """Drop just over threshold is flagged."""
    baseline = {"routing": 1.0}
    current = {"routing": 0.89}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 1
    assert regressions[0].dimension == "routing"


def test_multiple_regressions():
    """Multiple dimensions can regress simultaneously."""
    baseline = {"routing": 0.9, "correctness": 0.9, "groundedness": 0.9}
    current = {"routing": 0.5, "correctness": 0.5, "groundedness": 0.85}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 2


def test_missing_current_dimension():
    """Missing dimension in current scores is treated as 0.0."""
    baseline = {"routing": 0.9}
    current = {}

    regressions = detect_regressions(current, baseline, threshold=0.10)
    assert len(regressions) == 1
    assert regressions[0].current_score == 0.0


def test_delta_pct_format():
    """Regression result formats delta percentage correctly."""
    result = RegressionResult(
        dimension="routing",
        baseline_score=0.9,
        current_score=0.7,
        delta=-0.2,
        threshold=0.1,
        is_regression=True,
    )
    assert result.delta_pct == "-20.0%"
