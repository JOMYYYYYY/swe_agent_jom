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
"""Allowed event kinds in a trajectory.

定义一条轨迹里允许出现的 step 类型。存在这个类型别名，是为了让记录
user/assistant/tool/final answer 时只能使用固定字符串，减少拼写错误。
"""


@dataclass
class TrajectoryStep:
    """One timestamped event in an agent run.

    表示 agent 运行过程中的“一步”：可能是用户输入、assistant 回复、
    工具调用、工具返回结果，或者最终答案。存在这个类型，是为了让每一步
    都有统一结构：kind 表示事件类型，content 存具体内容，created_at 记录时间。
    """

    kind: StepKind
    content: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Trajectory:
    """In-memory log of an agent run.

    表示一次 agent 执行过程的完整轨迹，内部按顺序保存多个 TrajectoryStep。
    存在这个类型，是为了后续调试、复盘和评估 agent 行为：可以看到模型说了什么、
    调用了什么工具、工具返回了什么，以及最后如何回答。
    """

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
