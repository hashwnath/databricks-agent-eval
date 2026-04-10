"""MLflow trace format compatibility layer - scaffolded.

Converts internal Trace objects to MLflow 3 trace format, making eval
traces appear alongside production traces in the Databricks workspace.

Integration point: Install mlflow[databricks]>=3.1 and use
mlflow.tracing to log traces.
"""

from __future__ import annotations

from typing import Any

from .tracer import Trace


def to_mlflow_trace(trace: Trace) -> dict[str, Any]:
    """Convert internal Trace to MLflow 3 trace format.

    TODO: Replace with real MLflow tracing:
        import mlflow
        from mlflow.entities import Trace as MLflowTrace

        mlflow_trace = MLflowTrace(
            request_id=trace_id,
            info=TraceInfo(...),
            data=TraceData(spans=[...]),
        )

    The current implementation returns the correct schema so the
    interface is stable when you wire in the real SDK.
    """
    spans = []
    for i, step in enumerate(trace.steps):
        spans.append({
            "name": step.get("type", f"step_{i}"),
            "span_type": _map_step_type(step.get("type", "")),
            "inputs": {"query": trace.input} if i == 0 else {},
            "outputs": step.get("output", step.get("content", "")),
            "attributes": {
                k: v for k, v in step.items()
                if k not in ("type", "output", "content")
            },
        })

    return {
        "_schema": "mlflow.trace.v3",
        "_scaffolded": True,
        "request": {"query": trace.input},
        "response": trace.output,
        "spans": spans,
        "metrics": {
            "duration_ms": trace.duration_ms,
            "total_tokens": trace.total_tokens,
            "num_steps": len(trace.steps),
        },
    }


def _map_step_type(step_type: str) -> str:
    mapping = {
        "routing": "AGENT",
        "llm_call": "LLM",
        "retrieval": "RETRIEVER",
        "sub_agent_response": "AGENT",
        "tool_call": "TOOL",
    }
    return mapping.get(step_type, "UNKNOWN")
