from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolProperty:
    type: str
    description: str | None = None


@dataclass
class ToolSchema:
    type: str = "object"
    properties: dict[str, ToolProperty] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)


@dataclass
class ToolDescriptor:
    name: str
    description: str
    input_schema: ToolSchema
    output_schema: ToolSchema | None = None
    timeout_seconds: float | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ToolContext:
    request_id: str | None = None
    user_id: str | None = None


@dataclass
class ToolError:
    code: str
    message: str


@dataclass
class ToolResult:
    ok: bool
    tool_name: str
    data: dict[str, Any] | None = None
    error: ToolError | None = None
