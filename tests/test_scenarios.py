"""Tests for scenario loading and generation."""

import pytest
import tempfile
from pathlib import Path

from src.eval.scenarios.loader import EvalScenario, load_scenarios
from src.eval.scenarios.generator import generate_scenarios


def test_load_yaml_scenarios():
    """Happy path: Load basic_routing.yaml and verify structure."""
    scenarios = load_scenarios("scenarios/basic_routing.yaml")
    assert len(scenarios) == 5
    assert all(isinstance(s, EvalScenario) for s in scenarios)
    assert scenarios[0].id == "route_pipeline_failure"
    assert scenarios[0].metadata["expected_route"] == "pipeline_debugger"


def test_load_malformed_yaml():
    """Edge case: Malformed YAML produces clear error."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write("not_scenarios:\n  - bad: data\n")
        f.flush()
        with pytest.raises(ValueError, match="expected top-level 'scenarios' key"):
            load_scenarios(f.name)


def test_load_missing_file():
    """Edge case: Missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_scenarios("nonexistent.yaml")


def test_load_missing_input_field():
    """Edge case: Scenario without input field raises error."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write("scenarios:\n  - id: bad\n    expected_output: something\n")
        f.flush()
        with pytest.raises(ValueError, match="missing 'input' field"):
            load_scenarios(f.name)


def test_generate_basic_routing():
    """Happy path: Generate scenarios from template."""
    scenarios = generate_scenarios("basic_routing")
    assert len(scenarios) > 0
    assert all(isinstance(s, EvalScenario) for s in scenarios)


def test_generate_unknown_template():
    """Edge case: Unknown template raises error."""
    with pytest.raises(ValueError, match="Unknown template"):
        generate_scenarios("nonexistent_template")


def test_generate_with_count():
    """Generate limited number of scenarios."""
    scenarios = generate_scenarios("basic_routing", count=2, complexity="all")
    assert len(scenarios) == 2
