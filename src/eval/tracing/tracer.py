"""Execution tracer for agent runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Trace:
    input: str
    output: Any | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0

    def add_step(self, step_type: str, **kwargs) -> None:
        self.steps.append({"type": step_type, **kwargs})

    @property
    def routing_decision(self) -> str | None:
        for step in self.steps:
            if step.get("type") == "routing":
                return step.get("routed_to")
        return None

    @property
    def total_tokens(self) -> int:
        return sum(step.get("tokens_used", 0) for step in self.steps)


async def trace_agent_run(agent_fn: Callable, input_text: str) -> Trace:
    """Execute an agent function and capture its trace.

    The agent function should accept (input_text, trace) and populate
    the trace with steps as it executes.
    """
    trace = Trace(input=input_text)
    start = time.time()

    try:
        import inspect

        sig = inspect.signature(agent_fn)
        if len(sig.parameters) >= 2:
            result = await agent_fn(input_text, trace)
        else:
            result = await agent_fn(input_text)

        trace.output = result
    except Exception as e:
        trace.error = str(e)
    finally:
        trace.duration_ms = (time.time() - start) * 1000

    return trace
