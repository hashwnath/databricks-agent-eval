"""HTML reporter - self-contained report with inline CSS."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from ..harness import EvalResult


class HTMLReporter:
    def report(self, result: EvalResult, output_path: str = "eval_report.html") -> str:
        html = self._render(result)
        Path(output_path).write_text(html)
        return output_path

    def _render(self, result: EvalResult) -> str:
        status_color = "#22c55e" if result.passed else "#ef4444"
        status_text = "PASSED" if result.passed else "FAILED"

        scenario_rows = ""
        for sr in result.scenario_results:
            row_class = "pass-row" if sr.passed else "fail-row"
            judges_detail = ""
            for jr in sr.judge_results:
                j_color = "#22c55e" if jr.passed else "#ef4444"
                judges_detail += (
                    f'<div class="judge-detail">'
                    f'<span style="color:{j_color}">{jr.judge_name}: '
                    f'{"PASS" if jr.passed else "FAIL"}</span>'
                    f"<br><small>{jr.rationale}</small></div>"
                )

            scenario_rows += f"""
            <tr class="{row_class}">
                <td>{sr.scenario.id}</td>
                <td style="color:{('#22c55e' if sr.passed else '#ef4444')}">
                    {'PASS' if sr.passed else 'FAIL'}
                </td>
                <td>{sr.aggregate_score.weighted_score:.2f}</td>
                <td>{sr.aggregate_score.passing_judges}/{sr.aggregate_score.total_judges}</td>
                <td>{sr.duration_ms:.0f}ms</td>
                <td>{judges_detail}</td>
            </tr>"""

        regression_html = ""
        if result.regressions:
            regression_html = '<div class="regressions"><h2>Regressions Detected</h2>'
            for reg in result.regressions:
                regression_html += (
                    f"<div class='regression-item'>"
                    f"<strong>{reg.dimension}</strong>: "
                    f"{reg.baseline_score:.1%} -> {reg.current_score:.1%} "
                    f"({reg.delta_pct})</div>"
                )
            regression_html += "</div>"

        dims = result.metadata.get("dimension_scores", {})
        dimension_bars = ""
        for dim, score in dims.items():
            pct = score * 100
            color = "#22c55e" if score >= 0.7 else "#f59e0b" if score >= 0.5 else "#ef4444"
            dimension_bars += (
                f'<div class="dim-bar">'
                f'<span class="dim-name">{dim}</span>'
                f'<div class="bar-container">'
                f'<div class="bar-fill" style="width:{pct}%;background:{color}"></div>'
                f'</div>'
                f'<span class="dim-score">{score:.0%}</span>'
                f'</div>'
            )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Agent Eval Report</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f172a; color: #e2e8f0; padding: 2rem; }}
  .header {{ text-align: center; margin-bottom: 2rem; }}
  .header h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
  .status {{ display: inline-block; padding: 0.5rem 1.5rem; border-radius: 8px;
             font-weight: bold; font-size: 1.2rem;
             background: {status_color}20; color: {status_color};
             border: 2px solid {status_color}; }}
  .metrics {{ display: flex; gap: 1rem; justify-content: center; margin: 1.5rem 0; }}
  .metric {{ background: #1e293b; padding: 1rem 1.5rem; border-radius: 8px; text-align: center; }}
  .metric .value {{ font-size: 1.5rem; font-weight: bold; color: #f8fafc; }}
  .metric .label {{ font-size: 0.8rem; color: #94a3b8; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th {{ background: #1e293b; padding: 0.75rem; text-align: left; font-size: 0.85rem;
       text-transform: uppercase; color: #94a3b8; }}
  td {{ padding: 0.75rem; border-bottom: 1px solid #334155; }}
  .pass-row {{ background: #22c55e08; }}
  .fail-row {{ background: #ef444408; }}
  .judge-detail {{ margin: 0.25rem 0; }}
  .judge-detail small {{ color: #94a3b8; }}
  .regressions {{ background: #ef444415; border: 1px solid #ef4444; border-radius: 8px;
                  padding: 1rem; margin: 1rem 0; }}
  .regressions h2 {{ color: #ef4444; font-size: 1rem; margin-bottom: 0.5rem; }}
  .regression-item {{ padding: 0.25rem 0; color: #fca5a5; }}
  .dim-bar {{ display: flex; align-items: center; margin: 0.5rem 0; }}
  .dim-name {{ width: 200px; font-size: 0.9rem; }}
  .bar-container {{ flex: 1; background: #334155; border-radius: 4px; height: 20px; margin: 0 1rem; }}
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
  .dim-score {{ width: 50px; text-align: right; }}
  .footer {{ text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="header">
  <h1>Multi-Agent Evaluation Report</h1>
  <div class="status">{status_text}</div>
</div>

<div class="metrics">
  <div class="metric"><div class="value">{result.pass_rate:.0%}</div><div class="label">Pass Rate</div></div>
  <div class="metric"><div class="value">{result.aggregate_score:.2f}</div><div class="label">Aggregate Score</div></div>
  <div class="metric"><div class="value">{len(result.scenario_results)}</div><div class="label">Scenarios</div></div>
  <div class="metric"><div class="value">{result.metadata.get('num_judges', 0)}</div><div class="label">Judges</div></div>
  <div class="metric"><div class="value">{result.total_duration_ms:.0f}ms</div><div class="label">Duration</div></div>
</div>

{regression_html}

<h2 style="margin:1rem 0 0.5rem">Dimension Scores</h2>
{dimension_bars}

<h2 style="margin:1.5rem 0 0.5rem">Scenario Details</h2>
<table>
  <thead><tr>
    <th>Scenario</th><th>Status</th><th>Score</th><th>Judges</th><th>Duration</th><th>Details</th>
  </tr></thead>
  <tbody>{scenario_rows}</tbody>
</table>

<div class="footer">
  Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} |
  databricks-agent-eval v0.1.0 |
  github.com/hashwnath/databricks-agent-eval
</div>
</body>
</html>"""
