"""Supervisor agent - routes tasks to specialized sub-agents.

This demonstrates the "Supervisor Agent" architecture pattern that
Databricks identifies as the leading design pattern, accounting for
37% of enterprise agent deployments per their 2026 State of AI report.
"""

from __future__ import annotations

from typing import Any

from ..eval.tracing.tracer import Trace


ROUTING_PROMPT = """You are a data engineering supervisor agent. Given a user query about data issues,
route it to the most appropriate specialized sub-agent.

Available sub-agents:
- pipeline_debugger: For ETL pipeline failures, data flow issues, dependency problems, scheduling errors
- schema_analyzer: For schema changes, column types, migrations, table structure questions
- query_optimizer: For slow queries, performance tuning, cost optimization, index recommendations

Respond with ONLY the sub-agent name (one of: pipeline_debugger, schema_analyzer, query_optimizer).
If the query is ambiguous or out of scope, respond with: pipeline_debugger

Query: {query}

Route to:"""


class SupervisorAgent:
    """A 3-agent supervisor that routes data engineering tasks.

    Uses an LLM for routing decisions, then dispatches to the
    appropriate sub-agent. Each sub-agent is specialized for
    a specific class of data engineering problems.
    """

    def __init__(self, llm_client: Any = None, model: str = "gpt-4o-mini"):
        self._llm_client = llm_client
        self._model = model
        self._sub_agents = {
            "pipeline_debugger": PipelineDebuggerSubAgent(llm_client, model),
            "schema_analyzer": SchemaAnalyzerSubAgent(llm_client, model),
            "query_optimizer": QueryOptimizerSubAgent(llm_client, model),
        }

    async def run(self, query: str, trace: Trace | None = None) -> str:
        if trace is None:
            trace = Trace(input=query)

        if not query.strip():
            trace.add_step("error", message="Empty query received")
            return "Error: Please provide a data engineering question."

        route, confidence = await self._route(query, trace)
        response = await self._dispatch(route, query, trace)
        return response

    async def _route(self, query: str, trace: Trace) -> tuple[str, float]:
        client = await self._get_client()

        response = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "user", "content": ROUTING_PROMPT.format(query=query)}
            ],
            temperature=0.0,
        )

        route = response.choices[0].message.content.strip().lower()
        tokens = response.usage.total_tokens if response.usage else 0

        if route not in self._sub_agents:
            route = "pipeline_debugger"

        confidence = 0.9 if route in query.lower() else 0.7

        trace.add_step(
            "routing",
            routed_to=route,
            confidence=confidence,
            tokens_used=tokens,
        )
        trace.add_step("llm_call", tokens_used=tokens)

        return route, confidence

    async def _dispatch(self, route: str, query: str, trace: Trace) -> str:
        agent = self._sub_agents[route]
        result = await agent.handle(query, trace)
        return result

    async def _get_client(self):
        if self._llm_client is None:
            from openai import AsyncOpenAI
            self._llm_client = AsyncOpenAI()
        return self._llm_client


class _BaseSubAgent:
    def __init__(self, llm_client: Any, model: str):
        self._llm_client = llm_client
        self._model = model
        self.name = "base"
        self.system_prompt = ""

    async def handle(self, query: str, trace: Trace) -> str:
        client = self._llm_client
        if client is None:
            from openai import AsyncOpenAI
            client = AsyncOpenAI()

        response = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.0,
        )

        output = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0

        trace.add_step(
            "sub_agent_response",
            agent=self.name,
            output=output,
            tokens_used=tokens,
        )
        trace.add_step("llm_call", tokens_used=tokens)

        return output


class PipelineDebuggerSubAgent(_BaseSubAgent):
    def __init__(self, llm_client: Any, model: str):
        super().__init__(llm_client, model)
        self.name = "pipeline_debugger"
        self.system_prompt = (
            "You are a data pipeline debugging specialist. Diagnose ETL pipeline "
            "failures, identify root causes in data dependencies, and suggest fixes. "
            "Be concise and technical. Reference specific tables and pipeline stages."
        )


class SchemaAnalyzerSubAgent(_BaseSubAgent):
    def __init__(self, llm_client: Any, model: str):
        super().__init__(llm_client, model)
        self.name = "schema_analyzer"
        self.system_prompt = (
            "You are a database schema specialist. Analyze schema changes, "
            "column type mismatches, migration impacts, and table structure issues. "
            "Be concise and technical. Suggest safe migration paths."
        )


class QueryOptimizerSubAgent(_BaseSubAgent):
    def __init__(self, llm_client: Any, model: str):
        super().__init__(llm_client, model)
        self.name = "query_optimizer"
        self.system_prompt = (
            "You are a query performance specialist for Spark/Delta Lake. "
            "Analyze slow queries, recommend optimizations (partitioning, Z-ORDER, "
            "bloom filters, broadcast joins), and estimate cost savings. "
            "Be concise and technical."
        )
