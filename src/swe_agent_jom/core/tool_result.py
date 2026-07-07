from __future__ import annotations

from typing import Any, Literal, TypedDict


class SuccessResult(TypedDict):
    ok: Literal[True]
    data: dict[str, Any]


class BaseErrorResult(TypedDict):
    ok: Literal[False]
    error_type: str
    message: str


class ErrorResult(BaseErrorResult, total=False):
    details: dict[str, Any]


ToolResult = SuccessResult | ErrorResult


def success_result(data: dict[str, Any] | None = None) -> SuccessResult:
    return {
        "ok": True,
        "data": data or {},
    }


def error_result(
    error_type: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
) -> ErrorResult:
    result: ErrorResult = {
        "ok": False,
        "error_type": error_type,
        "message": message,
    }

    if details is not None:
        result["details"] = details

    return result
