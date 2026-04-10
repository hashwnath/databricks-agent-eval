"""Test scenario generator for multi-agent evaluation."""

from __future__ import annotations

from .loader import EvalScenario
from .templates import SCENARIO_TEMPLATES


def generate_scenarios(
    template_name: str = "basic_routing",
    count: int | None = None,
    complexity: str = "medium",
) -> list[EvalScenario]:
    """Generate scenarios from built-in templates.

    Args:
        template_name: Name of the built-in template to use.
        count: Number of scenarios to generate. Defaults to all in template.
        complexity: Filter by complexity tag - "simple", "medium", "complex".

    Returns:
        List of EvalScenario objects.
    """
    if template_name not in SCENARIO_TEMPLATES:
        available = ", ".join(SCENARIO_TEMPLATES.keys())
        raise ValueError(
            f"Unknown template: {template_name}. Available: {available}"
        )

    scenarios = SCENARIO_TEMPLATES[template_name]

    if complexity != "all":
        scenarios = [s for s in scenarios if complexity in s.tags or not s.tags]

    if count is not None:
        scenarios = scenarios[:count]

    return scenarios
