"""CLI runner for the evaluation harness."""

from __future__ import annotations

import asyncio
import sys

import click

from .harness import EvalHarness
from .judges import (
    CorrectnessJudge,
    RoutingAccuracyJudge,
    GroundednessJudge,
    CostEfficiencyJudge,
)
from .reporters.console import ConsoleReporter
from .reporters.html import HTMLReporter
from .scenarios.loader import load_scenarios


@click.command()
@click.option(
    "--scenarios", "-s",
    required=True,
    help="Path to scenario YAML/JSON file",
)
@click.option(
    "--agent", "-a",
    default="sample",
    help="Agent to evaluate: 'sample' (built-in supervisor) or path to custom agent module",
)
@click.option(
    "--output", "-o",
    default="eval_report.html",
    help="Output path for HTML report",
)
@click.option(
    "--baseline", "-b",
    default=None,
    help="Path to baseline scores JSON for regression detection",
)
@click.option(
    "--model", "-m",
    default="gpt-4o-mini",
    help="LLM model for judges and sample agent",
)
@click.option(
    "--threshold", "-t",
    default=0.10,
    help="Regression detection threshold (default: 10%)",
)
@click.option(
    "--console-only",
    is_flag=True,
    help="Only print console output, skip HTML report",
)
def main(
    scenarios: str,
    agent: str,
    output: str,
    baseline: str | None,
    model: str,
    threshold: float,
    console_only: bool,
) -> None:
    """Run multi-agent evaluation harness."""
    asyncio.run(_run(scenarios, agent, output, baseline, model, threshold, console_only))


async def _run(
    scenario_path: str,
    agent_name: str,
    output_path: str,
    baseline_path: str | None,
    model: str,
    threshold: float,
    console_only: bool,
) -> None:
    click.echo(f"Loading scenarios from {scenario_path}...")
    scenario_list = load_scenarios(scenario_path)
    click.echo(f"Loaded {len(scenario_list)} scenarios")

    judges = [
        CorrectnessJudge(model=model),
        RoutingAccuracyJudge(model=model),
        GroundednessJudge(model=model),
        CostEfficiencyJudge(),
    ]

    baseline_scores = None
    if baseline_path:
        import json
        from pathlib import Path

        baseline_scores = json.loads(Path(baseline_path).read_text())

    harness = EvalHarness(
        judges=judges,
        baseline=baseline_scores,
        regression_threshold=threshold,
    )

    if agent_name == "sample":
        from ..agents.supervisor import SupervisorAgent

        supervisor = SupervisorAgent(model=model)
        agent_fn = supervisor.run
    else:
        click.echo(f"Custom agent loading from {agent_name} not yet supported")
        sys.exit(1)

    click.echo("Running evaluation...")
    result = await harness.run(agent_fn, scenario_path, scenarios=scenario_list)

    console_reporter = ConsoleReporter()
    console_reporter.report(result)

    if not console_only:
        html_reporter = HTMLReporter()
        html_reporter.report(result, output_path)
        click.echo(f"\nHTML report saved to: {output_path}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
