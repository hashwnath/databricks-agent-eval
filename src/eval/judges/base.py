"""Base judge interface for LLM-as-judge evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..scenarios.loader import EvalScenario
from ..tracing.tracer import Trace


@dataclass
class JudgeResult:
    judge_name: str
    passed: bool
    confidence: float
    rationale: str
    metadata: dict[str, Any] | None = None

    @property
    def score(self) -> float:
        return 1.0 if self.passed else 0.0


class BaseJudge(ABC):
    """Abstract base class for all LLM judges."""

    def __init__(self, name: str, llm_client: Any = None, model: str = "gpt-4o-mini"):
        self.name = name
        self._llm_client = llm_client
        self._model = model

    @abstractmethod
    async def evaluate(self, trace: Trace, scenario: EvalScenario) -> JudgeResult:
        ...

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self._llm_client is None:
            from openai import AsyncOpenAI

            self._llm_client = AsyncOpenAI()

        response = await self._llm_client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""

    def _parse_judge_response(self, response: str) -> tuple[bool, float, str]:
        """Parse LLM judge response into (passed, confidence, rationale)."""
        lines = response.strip().split("\n")
        passed = False
        confidence = 0.5
        rationale = response

        for line in lines:
            lower = line.lower().strip()
            if lower.startswith("verdict:"):
                val = lower.split(":", 1)[1].strip()
                passed = val in ("pass", "yes", "true")
            elif lower.startswith("confidence:"):
                try:
                    confidence = float(lower.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.5
            elif lower.startswith("rationale:"):
                rationale = line.split(":", 1)[1].strip()

        return passed, confidence, rationale
