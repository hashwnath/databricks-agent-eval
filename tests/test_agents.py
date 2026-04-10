"""Tests for the sample multi-agent system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.supervisor import SupervisorAgent
from src.eval.tracing.tracer import Trace


def _mock_llm_response(content: str, tokens: int = 100):
    """Create a mock OpenAI response."""
    choice = MagicMock()
    choice.message.content = content
    usage = MagicMock()
    usage.total_tokens = tokens
    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


@pytest.mark.asyncio
async def test_supervisor_routes_pipeline():
    """Happy path: Pipeline query routes to pipeline_debugger."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _mock_llm_response("pipeline_debugger"),
            _mock_llm_response("Root cause: timeout on orders ETL"),
        ]
    )

    agent = SupervisorAgent(llm_client=mock_client, model="test")
    trace = Trace(input="My pipeline failed")
    result = await agent.run("My pipeline failed", trace)

    assert "orders" in result.lower() or "pipeline" in result.lower() or "root cause" in result.lower()
    assert trace.routing_decision == "pipeline_debugger"


@pytest.mark.asyncio
async def test_supervisor_routes_schema():
    """Schema query routes to schema_analyzer."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _mock_llm_response("schema_analyzer"),
            _mock_llm_response("Column type mismatch detected"),
        ]
    )

    agent = SupervisorAgent(llm_client=mock_client, model="test")
    trace = Trace(input="Column type mismatch")
    result = await agent.run("Column type mismatch", trace)

    assert trace.routing_decision == "schema_analyzer"


@pytest.mark.asyncio
async def test_supervisor_empty_input():
    """Edge case: Empty input returns error message."""
    mock_client = AsyncMock()
    agent = SupervisorAgent(llm_client=mock_client, model="test")
    trace = Trace(input="")
    result = await agent.run("", trace)

    assert "error" in result.lower() or "please provide" in result.lower()


@pytest.mark.asyncio
async def test_supervisor_unknown_route_defaults():
    """Edge case: Unknown route defaults to pipeline_debugger."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _mock_llm_response("unknown_agent"),
            _mock_llm_response("Analyzing the issue"),
        ]
    )

    agent = SupervisorAgent(llm_client=mock_client, model="test")
    trace = Trace(input="Something is wrong")
    result = await agent.run("Something is wrong", trace)

    assert trace.routing_decision == "pipeline_debugger"
