"""MLflow metric export - scaffolded with clean integration points.

In production, this module exports eval metrics and traces to MLflow 3,
making them visible in the Databricks workspace alongside Mosaic AI
Agent Evaluation results.

Integration point: Install mlflow[databricks]>=3.1 and configure
DATABRICKS_HOST + DATABRICKS_TOKEN environment variables.
"""

from __future__ import annotations

from typing import Any

from ..harness import EvalResult


class MLflowExporter:
    """Export eval results to MLflow tracking.

    Production usage:
        exporter = MLflowExporter(experiment_name="agent-eval/my-agent")
        exporter.export(result)

    This creates an MLflow run with:
    - Metrics: per-judge scores, aggregate score, pass rate, latency
    - Params: judge names, rubric weights, regression threshold
    - Tags: agent version, eval harness version
    - Artifacts: HTML report, scenario results JSON
    """

    def __init__(
        self,
        experiment_name: str = "agent-eval",
        tracking_uri: str | None = None,
    ):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri

    def export(self, result: EvalResult) -> dict[str, Any]:
        """Export eval results to MLflow.

        Returns dict with run_id and artifact URIs.

        TODO: Replace mock with real MLflow integration:
            import mlflow
            mlflow.set_tracking_uri(self.tracking_uri or "databricks")
            mlflow.set_experiment(self.experiment_name)

            with mlflow.start_run():
                mlflow.log_metrics({
                    "aggregate_score": result.aggregate_score,
                    "pass_rate": result.pass_rate,
                    "total_duration_ms": result.total_duration_ms,
                    **{f"judge_{k}": v for k, v in
                       result.metadata.get("dimension_scores", {}).items()},
                })
                mlflow.log_params({
                    "num_scenarios": result.metadata.get("num_scenarios"),
                    "num_judges": result.metadata.get("num_judges"),
                })
        """
        metrics = {
            "aggregate_score": result.aggregate_score,
            "pass_rate": result.pass_rate,
            "total_duration_ms": result.total_duration_ms,
        }
        for dim, score in result.metadata.get("dimension_scores", {}).items():
            metrics[f"judge_{dim}"] = score

        return {
            "run_id": "[SCAFFOLDED] MLflow run not created - requires mlflow[databricks]>=3.1",
            "metrics": metrics,
            "regressions": len(result.regressions),
        }
