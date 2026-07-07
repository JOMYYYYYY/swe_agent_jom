from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal


StepKind = Literal[
    "user_message",
    "assistant_message",
    "tool_call",
    "tool_result",
    "final_answer",
]


@dataclass
class TrajectoryStep:
    kind: StepKind
    content: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Trajectory:
    steps: list[TrajectoryStep] = field(default_factory=list)

    def record_user_message(self, content: str) -> TrajectoryStep:
        return self._append("user_message", {"content": content})

    def record_assistant_message(self, content: str) -> TrajectoryStep:
        return self._append("assistant_message", {"content": content})

    def record_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        tool_call_id: str | None = None,
    ) -> TrajectoryStep:
        return self._append(
            "tool_call",
            {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "arguments": arguments,
            },
        )

    def record_tool_result(
        self,
        tool_name: str,
        result: dict[str, Any],
        *,
        tool_call_id: str | None = None,
    ) -> TrajectoryStep:
        return self._append(
            "tool_result",
            {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "result": result,
            },
        )

    def record_final_answer(self, content: str) -> TrajectoryStep:
        return self._append("final_answer", {"content": content})

    def to_dicts(self) -> list[dict[str, Any]]:
        return [asdict(step) for step in self.steps]

    def to_jsonl(self) -> str:
        return "\n".join(
            json.dumps(step, ensure_ascii=False) for step in self.to_dicts()
        )

    def _append(self, kind: StepKind, content: dict[str, Any]) -> TrajectoryStep:
        step = TrajectoryStep(kind=kind, content=content)
        self.steps.append(step)
        return step
