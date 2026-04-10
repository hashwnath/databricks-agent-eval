"""Console reporter - rich terminal output for eval results."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..harness import EvalResult


class ConsoleReporter:
    def __init__(self):
        self.console = Console()

    def report(self, result: EvalResult) -> None:
        self.console.print()
        self._print_header(result)
        self._print_scenario_table(result)
        self._print_regressions(result)
        self._print_summary(result)

    def _print_header(self, result: EvalResult) -> None:
        status = "[green]PASSED[/green]" if result.passed else "[red]FAILED[/red]"
        self.console.print(
            Panel(
                f"Status: {status}  |  "
                f"Pass rate: {result.pass_rate:.0%}  |  "
                f"Score: {result.aggregate_score:.2f}  |  "
                f"Duration: {result.total_duration_ms:.0f}ms",
                title="Eval Results",
                border_style="green" if result.passed else "red",
            )
        )

    def _print_scenario_table(self, result: EvalResult) -> None:
        table = Table(title="Scenario Results")
        table.add_column("ID", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Score", justify="right")
        table.add_column("Judges", justify="right")
        table.add_column("Duration", justify="right")

        for sr in result.scenario_results:
            status = "[green]PASS[/green]" if sr.passed else "[red]FAIL[/red]"
            judges_str = f"{sr.aggregate_score.passing_judges}/{sr.aggregate_score.total_judges}"
            table.add_row(
                sr.scenario.id,
                status,
                f"{sr.aggregate_score.weighted_score:.2f}",
                judges_str,
                f"{sr.duration_ms:.0f}ms",
            )

        self.console.print(table)

    def _print_regressions(self, result: EvalResult) -> None:
        if not result.regressions:
            return

        self.console.print()
        self.console.print("[bold red]REGRESSIONS DETECTED:[/bold red]")
        for reg in result.regressions:
            self.console.print(
                f"  [red]>{reg.dimension}[/red]: "
                f"{reg.baseline_score:.1%} -> {reg.current_score:.1%} "
                f"({reg.delta_pct})"
            )

    def _print_summary(self, result: EvalResult) -> None:
        self.console.print()
        dims = result.metadata.get("dimension_scores", {})
        if dims:
            self.console.print("[bold]Per-dimension scores:[/bold]")
            for dim, score in dims.items():
                bar_len = int(score * 20)
                bar = "[green]" + ">" * bar_len + "[/green]" + " " * (20 - bar_len)
                self.console.print(f"  {dim:25s} [{bar}] {score:.0%}")
